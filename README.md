<<<<<<< HEAD
# Megapolis Backend (FastAPI + PostgreSQL)
Generated scaffold for your React Vite + Tailwind UI project.

## What's included
- FastAPI app structure
- SQLAlchemy + PostgreSQL
- Pydantic schemas
- JWT auth skeleton
- Password hashing (bcrypt via passlib)
- Example routes for auth, users, organizations
- .env.example to configure DATABASE_URL and JWT_SECRET

## Quick start (Windows)
1. Create and activate a virtualenv:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` → `.env` and edit values (set your postgres password and DB name `megapolisdb`)
4. Create the database (if not exists):
   ```sql
   CREATE DATABASE megapolisdb;
   ```
   you can run that from psql as postgres superuser.
5. Run app:
   ```bash
   uvicorn app.main:app --reload
   ```
6. Visit `http://127.0.0.1:8000/docs` for interactive OpenAPI docs.
=======
# megapolisBackEnd
>>>>>>> 082b6d4c510ed30deaf0ac5865cc27e4f383b25f
