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

    ```bash
    python -m venv venv
    source venv/bin/activate    # On Windows: venv\Scripts\activate

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt

4. **Create .env file**

   ```bash
   touch > .env   # On Windows: type nul  > .env

5. **Add environment variables:**

   ```bash
   DATABASE_URL="sqlite:///./yourdb.db"
   SECRET="your-secret-phrase"
   ADMIN_USER="your-username"
   ADMIN_PASS="your-password"

5. **Run the application:**

    ```bash
    python -m run.py

If errors arise with external imports ensure your venv interpreter is selected.