from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from db.database import Base
from sqlalchemy.orm import relationship

class Reporte(Base):
    __tablename__ = "reportes"
    id_reporte = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_inmueble = Column(Integer, ForeignKey("inmuebles.id_inmueble"), nullable=False)
    tipo_reporte = Column(String(255), nullable=False)
    descripcion = Column(String(500), nullable=True)
    fecha_reporte = Column(DateTime, server_default=func.now())
    estado_reporte = Column(String(20), default="pendiente")

    usuario = relationship("Usuario", back_populates="reportes")
    inmueble = relationship("Inmueble", back_populates="reportes")

    def __repr__(self):
        return f"<Reporte(id_reporte={self.id_reporte}, tipo_reporte='{self.tipo_reporte}', estado_reporte='{self.estado_reporte}')>"
