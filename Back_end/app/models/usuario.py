from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from db.database import Base  # Importamos la Base declarativa
from sqlalchemy import Float, ForeignKey
from sqlalchemy.orm import relationship

# Modelo Usuario
class Usuario(Base):
    __tablename__ = "usuarios"
    id_usuario = Column(Integer, primary_key=True, index=True)
    nombres = Column(String(100), nullable=False)
    apellido_paterno = Column(String(50), nullable=False)
    apellido_materno = Column(String(50), nullable=True)
    num_celular = Column(String(20), unique=True, nullable=True)
    fecha_nacimiento = Column(DateTime, nullable=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    celular_verificado = Column(Boolean, default=False)
    codigo_verificacion = Column(String(10), nullable=True)
    fecha_registro = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, onupdate=func.now())
    tipo_usuario = Column(String(20), default="arrendatario")  # Por defecto es arrendatario (inquilino)
    activo = Column(Boolean, default=True)
    notificaciones = relationship("Notificacion", back_populates="usuario")

    inmuebles = relationship("Inmueble", back_populates="propietario")
    reservas = relationship("Reserva", back_populates="usuario")
    favoritos = relationship("Favorito", back_populates="usuario")
    resenas = relationship("Resena", back_populates="usuario")
    reportes = relationship("Reporte", back_populates="usuario")

    def __repr__(self):
        return f"<Usuario(id_usuario={self.id_usuario}, email='{self.email}', tipo_usuario='{self.tipo_usuario}')>"
