@echo off
cd /d "%~dp0backend"
set DATABASE_URL=postgresql+psycopg2://sc_user:sc_pass@localhost:5432/sc_db
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload


