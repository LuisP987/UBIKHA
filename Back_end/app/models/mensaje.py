from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from db.database import Base
from sqlalchemy.orm import relationship

class Mensaje(Base):
    __tablename__ = "mensajes"
    id_mensaje = Column(Integer, primary_key=True, index=True)
    id_remitente = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_destinatario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    contenido = Column(String(255), nullable=False)
    fecha_envio = Column(DateTime, server_default=func.now())
    estado_mensaje = Column(String(20), default="enviado")

    remitente = relationship("Usuario", foreign_keys=[id_remitente], backref="mensajes_enviados")
    destinatario = relationship("Usuario", foreign_keys=[id_destinatario], backref="mensajes_recibidos")

    def __repr__(self):
        return f"<Mensaje(id_mensaje={self.id_mensaje}, remitente={self.id_remitente}, destinatario={self.id_destinatario})>"
