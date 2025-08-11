Sistema Comercial — Backend (FastAPI)
Backend modular y escalable para gestión comercial: productos, clientes, ventas y usuarios.
Stack: FastAPI + SQLAlchemy + Pydantic + Uvicorn + Poetry.
DB por defecto: SQLite (simple para dev). Fácil migración a PostgreSQL.

📦 Requisitos
Python 3.10+

Poetry 2.x

(Opcional) Docker Desktop (para Postgres más adelante)

🚀 Instalación
# Estar en la carpeta backend/
poetry install
poetry add "pydantic[email]" passlib[bcrypt]  # si no los tenés aún

# (solución warning bcrypt/passlib en Windows)
poetry add "bcrypt==3.2.2"

▶️ Ejecutar
poetry run uvicorn app.main:app --reload

Docs: http://localhost:8000/docs

Healthcheck: GET /health → { "status": "ok" }

🗂️ Estructura
backend/
└── app/
    ├── core/                 # (futuro) settings, logging
    ├── db/
    │   ├── database.py       # engine, SessionLocal, Base, get_db()
    ├── models/               # SQLAlchemy models
    │   ├── producto_model.py
    │   ├── cliente_model.py
    │   ├── venta_model.py
    │   └── user_model.py
    ├── schemas/              # Pydantic (Create/Update/Out)
    ├── services/             # Lógica de negocio (DB ops)
    ├── routers/              # Endpoints FastAPI
    └── main.py               # Punto de entrada

🔌 Base de datos
Opción A: SQLite (por defecto)
app/db/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Opción B: PostgreSQL (producción, con Docker)
Instalar driver:
poetry add psycopg2-binary

Cambiar en database.py:
# DATABASE_URL = "postgresql+psycopg2://admin:admin@localhost:5432/sistema"
# engine = create_engine(DATABASE_URL)
Próximo paso: agregar Alembic para migraciones (lo dejamos listo en la próxima iteración).

📚 Endpoints (CRUD)
Productos
POST /productos/ — Crear

GET /productos/ — Listar

GET /productos/{id} — Obtener uno

PUT /productos/{id} — Actualizar

DELETE /productos/{id} — Eliminar

Clientes
POST /clientes/

GET /clientes/

GET /clientes/{id}

PUT /clientes/{id}

DELETE /clientes/{id}

Ventas
POST /ventas/

GET /ventas/

GET /ventas/{id}

PUT /ventas/{id}

DELETE /ventas/{id}

Usuarios
POST /usuarios/ (hashea password con passlib[bcrypt])

GET /usuarios/

GET /usuarios/{id}

PUT /usuarios/{id}

DELETE /usuarios/{id}

🧪 Pruebas rápidas (Swagger)
Abrí http://localhost:8000/docs

Probá el flujo CRUD en cada entidad:

Crear → Listar → Obtener → Actualizar → Eliminar

Ventas requieren cliente_id válido.


🧩 Commit & Push (rama master)
# Estar en backend/ o en la raíz del repo según tu .git
git add .
git commit -m "Backend FastAPI: CRUD completo (productos, clientes, ventas, usuarios)"
git branch -M master
git push -u origin master






🛠️ Troubleshooting
1) Warning de Pydantic v2
   UserWarning: 'orm_mode' has been renamed to 'from_attributes'
Soluciones:

Mantener class Config: orm_mode = True (funciona igual), o

Usar Pydantic v2:
from pydantic import ConfigDict
class ProductoOut(...):
    model_config = ConfigDict(from_attributes=True)


2) Warning/trace de bcrypt
   (trapped) error reading bcrypt version
AttributeError: module 'bcrypt' has no attribute '__about__'

Solución:
poetry add "bcrypt==3.2.2"

3) Error relaciones SQLAlchemy (has no property 'ventas')
Asegurate de definir ambos lados:
# cliente_model.py
ventas = relationship("Venta", back_populates="cliente")

# venta_model.py
cliente = relationship("Cliente", back_populates="ventas")

Si cambiaste modelos, borrar test.db y reiniciar.

4) Swagger no deja editar body en POST/PUT
Revisá que el endpoint reciba un schema Pydantic (no dict) como parámetro.

🧭 Roadmap próximo (lo trabajamos en la siguiente sesión)
Migración a PostgreSQL con docker-compose

Alembic para migraciones

Autenticación JWT (login/logout, protección de rutas)

Validaciones y constraints adicionales

Tests con pytest

CI/CD básico (GitHub Actions)

👤 Autor
Jonatan Sotelo

Organización técnica: FastAPI + SQLAlchemy + Poetry

Mentoría técnica: ChatGPT


6) 

