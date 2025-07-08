# ToDo App

A simple and lightweight task management web application built with **FastAPI**, **SQLAlchemy**, and **Jinja2** templates.  
Includes user authentication and supports creating, updating, and deleting tasks.

---

## Features

- User registration and login with password hashing
- Create, edit, and delete to-do items
- Responsive HTML templates with Jinja2
- SQLite database using SQLAlchemy ORM
- Basic rate limiting and security headers

---

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/BlainePrice/todo-app.git
   cd todo-app

2. **Create and activate a virtual environment:**
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate

3. **Install dependencies:**
pip install -r requirements.txt

4. **Run the application:**
python -m run.py