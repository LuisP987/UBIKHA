from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from db.database import Base
from sqlalchemy.orm import relationship

class Inmueble(Base):
    __tablename__ = "inmuebles"
    id_inmueble = Column(Integer, primary_key=True, index=True)
    id_propietario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    titulo = Column(String(100), nullable=False)
    descripcion = Column(String(255), nullable=True)
    precio_mensual = Column(Float, nullable=False)
    tipo_inmueble = Column(String(50), nullable=False)
    fecha_publicacion = Column(DateTime, server_default=func.now())
    estado = Column(String(20), default="disponible")
    calificacion_promedio = Column(Float, default=0.0)
    total_resenas = Column(Integer, default=0)

    propietario = relationship("Usuario", back_populates="inmuebles")
    caracteristicas = relationship("CaracteristicasInmueble", back_populates="inmueble", uselist=False)
    reservas = relationship("Reserva", back_populates="inmueble")
    favoritos = relationship("Favorito", back_populates="inmueble")
    resenas = relationship("Resena", back_populates="inmueble")
    imagenes = relationship("ImagenInmueble", back_populates="inmueble")
    reportes = relationship("Reporte", back_populates="inmueble")

    def __repr__(self):
        return f"<Inmueble(id_inmueble={self.id_inmueble}, titulo='{self.titulo}')>"

class CaracteristicasInmueble(Base):
    __tablename__ = "caracteristicas_inmueble"
    id_caracteristica = Column(Integer, primary_key=True, index=True)
    id_inmueble = Column(Integer, ForeignKey("inmuebles.id_inmueble"), unique=True)
    direccion = Column(String(255), nullable=False)
    referencias = Column(String(255), nullable=True)  # Referencias adicionales de ubicación
    habitaciones = Column(Integer, nullable=False)
    camas = Column(Integer, nullable=False)
    banos = Column(Integer, nullable=False)
    capacidad = Column(Integer, nullable=False)  # Huéspedes máximos
    
    # Servicios disponibles (todos ahora existen en la BD)
    wifi = Column(Boolean, default=False)
    cocina = Column(Boolean, default=False)
    estacionamiento = Column(Boolean, default=False)
    mascotas_permitidas = Column(Boolean, default=False)
    camaras_seguridad = Column(Boolean, default=False)
    television = Column(Boolean, default=False)
    aire_acondicionado = Column(Boolean, default=False)
    servicio_lavanderia = Column(Boolean, default=False)

    inmueble = relationship("Inmueble", back_populates="caracteristicas")

    def __repr__(self):
        return f"<CaracteristicasInmueble(id_caracteristica={self.id_caracteristica}, id_inmueble={self.id_inmueble})>"
