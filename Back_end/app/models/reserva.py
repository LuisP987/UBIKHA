from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from db.database import Base
from sqlalchemy.orm import relationship

class Reserva(Base):
    __tablename__ = "reservas"
    id_reserva = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    id_inmueble = Column(Integer, ForeignKey("inmuebles.id_inmueble"))
    estado = Column(String(20), default="pendiente")
    monto_total = Column(Float, nullable=False)
    fecha_reserva = Column(DateTime, server_default=func.now())

    usuario = relationship("Usuario", back_populates="reservas")
    inmueble = relationship("Inmueble", back_populates="reservas")
    pagos = relationship("Pago", back_populates="reserva")

    def __repr__(self):
        return f"<Reserva(id_reserva={self.id_reserva}, estado='{self.estado}')>"

class Pago(Base):
    __tablename__ = "pagos"
    id_pago = Column(Integer, primary_key=True, index=True)
    id_reserva = Column(Integer, ForeignKey("reservas.id_reserva"))
    fecha_pago = Column(DateTime, server_default=func.now())
    monto = Column(Float, nullable=False)
    metodo_pago = Column(String(50), nullable=False)
    estado_pago = Column(String(20), default="pendiente")

    reserva = relationship("Reserva", back_populates="pagos")

    def __repr__(self):
        return f"<Pago(id_pago={self.id_pago}, estado_pago='{self.estado_pago}')>"
