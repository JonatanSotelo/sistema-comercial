from app.db.database import Base
import app.db.base    # 💡 esto es lo que fuerza a registrar el modelo User
target_metadata = Base.metadata
