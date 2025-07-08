from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from app.crud.database import get_db, init_db
from app.auth.create_admin import create_admin
from models.models import User, Todo, SupportTicket, SupportTicketMessage
from app.auth.auth import hash_password, verify_password
from dotenv import load_dotenv
from datetime import datetime, timezone
import logging
import secrets
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    create_admin()
    yield

load_dotenv()

app = FastAPI(lifespan=lifespan)

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET"), https_only=False, max_age=3600)  # type: ignore

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Static and template setup
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_current_user(request: Request, db: Session):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter_by(id=user_id).first()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Status: {response.status_code}")
    return response

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.update({
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",
        "Referrer-Policy": "no-referrer-when-downgrade",
        "Permissions-Policy": "geolocation=(), microphone=()",
        "Content-Security-Policy": "default-src 'self'"
    })
    return response

@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(status_code=500, content={"message": "Internal Server Error"})

# ---------------- AUTH ROUTES ---------------- #

@app.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    if "csrf_token" not in request.session:
        request.session["csrf_token"] = secrets.token_hex(16)
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register_user(request: Request,
                        username: str = Form(...), 
                        password: str = Form(...),
                        csrf_token: str = Form(...),
                        db: Session = Depends(get_db)):
    session_token = request.session.get("csrf_token")
    if csrf_token != session_token:
        raise HTTPException(status_code=403, detail="CSRF token mismatch")
    
    if db.query(User).filter_by(username=username).first():
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username already exists"})
    user = User(username=username, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    return RedirectResponse("/login", status_code=302)

@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    if "csrf_token" not in request.session:
        request.session["csrf_token"] = secrets.token_hex(16)
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
@limiter.limit("5/minute")
def login_user(request: Request,
                      username: str = Form(...),
                        password: str = Form(...),
                        csrf_token: str = Form(...),
                        db: Session = Depends(get_db)):
    session_token = request.session.get("csrf_token")
    if csrf_token != session_token:
        raise HTTPException(status_code=403, detail="CSRF token mismatch")
    
    user = db.query(User).filter_by(username=username).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    request.session["user_id"] = user.id
    return RedirectResponse("/", status_code=302)

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)

# ---------------- TODO ROUTES ---------------- #

@app.get("/", response_class=HTMLResponse)
def show_todos(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)
    todos = db.query(Todo).filter_by(owner_id=user.id).all()
    return templates.TemplateResponse("todos.html", {"request": request, "todos": todos, "user": user})

@app.post("/todos", response_class=HTMLResponse)
def create_todo(request: Request,
                title: str = Form(...),
                description: str = Form(""),
                csrf_token: str = Form(...),
                db: Session = Depends(get_db)):
    session_token = request.session.get("csrf_token")
    if csrf_token != session_token:
        raise HTTPException(status_code=403, detail="CSRF token mismatch")
    
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)
    todo = Todo(title=title, description=description, owner_id=user.id)
    db.add(todo)
    db.commit()
    return RedirectResponse("/", status_code=302)

@app.get("/complete/{todo_id}")
def complete_todo(todo_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)
    todo = db.query(Todo).filter_by(id=todo_id, owner_id=user.id).first()
    if todo:
        todo.completed = True  # type: ignore
        db.commit()
    return RedirectResponse("/")

@app.get("/delete/{todo_id}")
def delete_todo(todo_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)
    todo = db.query(Todo).filter_by(id=todo_id, owner_id=user.id).first()
    if todo:
        db.delete(todo)
        db.commit()
    return RedirectResponse("/")

# ---------------- SUPPORT ROUTES ---------------- #

@app.get("/support", response_class=HTMLResponse)
def support_form(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("support.html", {"request": request, "user": user})

@app.post("/support", response_class=HTMLResponse)
def submit_ticket(request: Request, 
                  title: str = Form(...), 
                  description: str = Form(...),
                  csrf_token: str = Form(...), 
                  db: Session = Depends(get_db)):
    session_token = request.session.get("csrf_token")
    if csrf_token != session_token:
        raise HTTPException(status_code=403, detail="CSRF token mismatch")
    
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")
    ticket = SupportTicket(title=title, description=description, user_id=user.id)
    db.add(ticket)
    db.commit()
    return RedirectResponse("/support", status_code=302)

# ---------------- ADMIN ROUTES ---------------- #
@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user or not bool(current_user.is_admin):
        raise HTTPException(status_code=403, detail="Unauthorized")

    users = db.query(User).all()
    todos = db.query(Todo).all()
    tickets = db.query(SupportTicket).order_by(SupportTicket.created_at.desc()).all()
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "users": users,
        "todos": todos,
        "tickets": tickets,
        "user": current_user
    })

@app.get("/admin/users/edit/{user_id}", response_class=HTMLResponse)
def edit_user_form(user_id: int, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user or not bool(current_user.is_admin):
        raise HTTPException(status_code=403, detail="Unauthorized")

    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    return templates.TemplateResponse("admin_user_edit.html", {"request": request, "user": user})


@app.get("/admin/users/delete/{user_id}")
def delete_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user or not bool(current_user.is_admin):
        raise HTTPException(status_code=403, detail="Unauthorized")

    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    db.delete(user)
    db.commit()
    return RedirectResponse("/admin", status_code=302)


@app.get("/admin/todos/edit/{todo_id}", response_class=HTMLResponse)
def edit_todo_form(todo_id: int, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user or not bool(current_user.is_admin):
        raise HTTPException(status_code=403, detail="Unauthorized")

    todo = db.query(Todo).filter_by(id=todo_id).first()
    if not todo:
        raise HTTPException(404, "Todo not found")
    return templates.TemplateResponse("admin_todo_edit.html", {"request": request, "todo": todo})


@app.post("/admin/todos/edit/{todo_id}")
def edit_todo(todo_id: int, request: Request,
              title: str = Form(...),
              description: str = Form(...),
              completed: bool = Form(False),
              db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user or not bool(current_user.is_admin):
        raise HTTPException(status_code=403, detail="Unauthorized")

    todo = db.query(Todo).filter_by(id=todo_id).first()
    if not todo:
        raise HTTPException(404, "Todo not found")

    todo.title = title #type: ignore
    todo.description = description #type: ignore
    todo.completed = completed #type: ignore
    db.commit()
    return RedirectResponse("/admin", status_code=302)


@app.get("/admin/todos/delete/{todo_id}")
def admin_delete_todo(todo_id: int, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user or not bool(current_user.is_admin):
        raise HTTPException(status_code=403, detail="Unauthorized")

    todo = db.query(Todo).filter_by(id=todo_id).first()
    if not todo:
        raise HTTPException(404, "Todo not found")
    db.delete(todo)
    db.commit()
    return RedirectResponse("/admin", status_code=302)

@app.get("/admin/support/{ticket_id}", response_class=HTMLResponse)
def admin_view_ticket(ticket_id: int, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user or not bool(current_user.is_admin):
        raise HTTPException(status_code=403, detail="Unauthorized")

    ticket = db.query(SupportTicket).filter_by(id=ticket_id).first()
    if not ticket:
        raise HTTPException(404, "Ticket not found")

    return templates.TemplateResponse("support_detail.html", {"request": request, "ticket": ticket, "user": current_user})


@app.post("/admin/support/{ticket_id}/reply")
def admin_reply_ticket(ticket_id: int, request: Request,
                       message: str = Form(...),
                       status: str = Form(...),
                       csrf_token: str = Form(...),
                       db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user or not bool(current_user.is_admin):
        raise HTTPException(status_code=403, detail="Unauthorized")

    session_token = request.session.get("csrf_token")
    if csrf_token != session_token:
        raise HTTPException(status_code=403, detail="CSRF token mismatch")

    ticket = db.query(SupportTicket).filter_by(id=ticket_id).first()
    if not ticket:
        raise HTTPException(404, "Ticket not found")

    reply = SupportTicketMessage(
        ticket_id=ticket.id,
        sender_id=current_user.id,
        message=message,
        created_at=datetime.now(timezone.utc)
    )
    ticket.status = status  #type:ignore
    db.add(reply)
    db.commit()
    return RedirectResponse(f"/admin/support/{ticket_id}", status_code=302)

@app.get("/admin/support/{ticket_id}/delete")
def admin_delete_ticket(ticket_id: int, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user or not bool(current_user.is_admin):
        raise HTTPException(status_code=403, detail="Unauthorized")

    ticket = db.query(SupportTicket).filter_by(id=ticket_id).first()
    if not ticket:
        raise HTTPException(404, "Ticket not found")

    db.delete(ticket)
    db.commit()
    return RedirectResponse("/admin", status_code=302)

