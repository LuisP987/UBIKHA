from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from db.database import Base
from sqlalchemy.orm import relationship

class ImagenInmueble(Base):
    __tablename__ = "imagenes_inmueble"
    id_imagen = Column(Integer, primary_key=True, index=True)
    id_inmueble = Column(Integer, ForeignKey("inmuebles.id_inmueble"), nullable=False)
    url_imagen = Column(String(255), nullable=False)
    fecha_subida = Column(DateTime, server_default=func.now())

    inmueble = relationship("Inmueble", back_populates="imagenes")

    def __repr__(self):
        return f"<ImagenInmueble(id_imagen={self.id_imagen}, id_inmueble={self.id_inmueble})>"
