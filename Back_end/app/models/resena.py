from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from db.database import Base
from sqlalchemy.orm import relationship

class Resena(Base):
    __tablename__ = "resenas"
    id_resena = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    id_inmueble = Column(Integer, ForeignKey("inmuebles.id_inmueble"))
    calificacion = Column(Integer, nullable=False)
    comentario = Column(String(255), nullable=True)
    fecha_resena = Column(DateTime, server_default=func.now())
    estado_resena = Column(String(20), default="visible")

    usuario = relationship("Usuario", back_populates="resenas")
    inmueble = relationship("Inmueble", back_populates="resenas")

    def __repr__(self):
        return f"<Resena(id_resena={self.id_resena}, calificacion={self.calificacion})>"
