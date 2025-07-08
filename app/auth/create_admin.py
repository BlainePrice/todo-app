from sqlalchemy.orm import Session
from app.crud.database import SessionLocal
from models.models import User
from app.auth.auth import hash_password
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(level=logging.INFO)
load_dotenv()

def create_admin():
    db: Session = SessionLocal()
    existing = db.query(User).filter_by(username=os.getenv("ADMIN_USER")).first()
    if existing:
        logging.info("Admin already exists.")
        return
    admin = User(username=os.getenv("ADMIN_USER"), hashed_password=hash_password(os.getenv('ADMIN_PASS')), is_admin=True) # type: ignore
    db.add(admin)
    db.commit()
    logging.info("Admin user created.")
