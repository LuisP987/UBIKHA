from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class EstadoReservaEnum(str, Enum):
    pendiente = "pendiente"
    confirmada = "confirmada"
    cancelada = "cancelada"
    completada = "completada"

class ReservaCreate(BaseModel):
    id_inmueble: int
    monto_total: float

class ReservaOut(BaseModel):
    id_reserva: int
    id_usuario: int
    id_inmueble: int
    estado: str
    monto_total: float
    fecha_reserva: datetime

    class Config:
        from_attributes = True

class ReservaUpdate(BaseModel):
    estado: EstadoReservaEnum

class EstadoPagoEnum(str, Enum):
    pendiente = "pendiente"
    completado = "completado"
    fallido = "fallido"
    reembolsado = "reembolsado"

class PagoCreate(BaseModel):
    monto: float
    metodo_pago: str

class PagoOut(BaseModel):
    id_pago: int
    id_reserva: int
    fecha_pago: datetime
    monto: float
    metodo_pago: str
    estado_pago: str

    class Config:
        from_attributes = True

class PagoUpdate(BaseModel):
    estado_pago: EstadoPagoEnum
