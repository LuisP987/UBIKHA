from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from db.database import Base
from sqlalchemy.orm import relationship

class Notificacion(Base):
    __tablename__ = "notificaciones"
    id_notificacion = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    mensaje = Column(String(255), nullable=False)
    fecha_notificacion = Column(DateTime, server_default=func.now())
    estado_notificacion = Column(String(20), default="no_leida")

    usuario = relationship("Usuario", back_populates="notificaciones")

    def __repr__(self):
        return f"<Notificacion(id_notificacion={self.id_notificacion}, id_usuario={self.id_usuario}, estado_notificacion='{self.estado_notificacion}')>"
