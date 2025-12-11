# Task Manager API (FastAPI)

A minimal, production-ready **Task Manager** backend built with **FastAPI**, **SQLAlchemy 2.0 (async)** and **SQLite**.  
Perfect to practice CRUD operations, validation with Pydantic, and REST API design. Auto-documented with Swagger UI.

---

## 🧩 Stack
- Python 3.11+
- FastAPI
- SQLAlchemy 2.0 (async)
- SQLite (aiosqlite)
- Pydantic v2
- Uvicorn

---

## ⚙️ Features
- CRUD for tasks (create, list with filters/pagination, get by id, update, delete)
- Filter by completion status (`?completed=true|false`)
- Sort by `due_date` then `created_at`
- Auto database creation on startup
- CORS enabled (adjust origins as needed)
- Swagger UI at `/docs`
- Async implementation (SQLAlchemy 2.0 + AsyncSession)

---

## 📁 Project structure
app/

init.py

main.py

db.py

models.py

schemas.py

crud.py

requirements.txt


---

## Roadmap
- [x] Initialize repository with README and MIT License
- [x] Add JWT authentication
- [x] Add pagination metadata (total, pages)
- [ ] Add unit tests (pytest)
- [x] Dockerize
- [ ] Deploy to Render/Railway

---

## 🚀 Getting started

### 1️⃣ Setup environment
```bash
# Create virtual environment
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
# .venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2️⃣ Run the API
uvicorn app.main:app --reload

## Author
Adrián Félix

Software Engineering

Passionate about Android Developer, Full Stack and iOS development and clean architecture.

GitHub: @Elmamis69
Email: guerofelix234@gmail.com

**License**
This project is licensed under the MIT License.

## Getting Started
1. Clone the repository:
   ```bash
https://github.com/Elmamis69/fastapi-task-manager.git
