@echo off
cd backend
call venv\Scripts\activate
set DATABASE_URL=postgresql+psycopg2://sc_user:sc_pass@localhost:5432/sc_db
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload


