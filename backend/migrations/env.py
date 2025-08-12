from app.db.database import Base
import app.db.base  # 👈 carga TODOS los modelos
target_metadata = Base.metadata
