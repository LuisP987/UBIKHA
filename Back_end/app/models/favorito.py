from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from db.database import Base
from sqlalchemy.orm import relationship

class Favorito(Base):
    __tablename__ = "favoritos"
    id_inmueble = Column(Integer, ForeignKey("inmuebles.id_inmueble"), primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), primary_key=True)
    fecha_guardado = Column(DateTime, server_default=func.now())

    usuario = relationship("Usuario", back_populates="favoritos")
    inmueble = relationship("Inmueble", back_populates="favoritos")

    def __repr__(self):
        return f"<Favorito(id_usuario={self.id_usuario}, id_inmueble={self.id_inmueble})>"
