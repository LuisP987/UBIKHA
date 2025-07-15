from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from db.database import Base  # Importamos la Base declarativa

class User(Base):
    __tablename__ = "users"

    # --- Columnas Principales ---
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # --- Información del Perfil ---
    full_name = Column(String(100), nullable=True)
    phone_number = Column(String(20), unique=True, nullable=True)

    # --- Roles y Estado ---
    is_active = Column(Boolean, default=True)
    rol = Column(String(20), default="client")  # Valores esperados: client, owner, admin

    # --- Timestamps (Auditoría) ---
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', rol='{self.rol}')>"
