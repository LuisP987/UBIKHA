from pydantic import BaseModel, Field
from typing import Optional, List
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

# Nuevos esquemas para respuestas más informativas
class ListaReservasResponse(BaseModel):
    """Respuesta completa para el listado de reservas"""
    mensaje: str = Field(..., description="Mensaje descriptivo sobre el estado de las reservas")
    total_reservas: int = Field(..., description="Número total de reservas del usuario")
    reservas: List[ReservaOut] = Field(..., description="Lista de reservas (puede estar vacía)")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "mensaje": "Tienes 2 reservas activas",
                    "total_reservas": 2,
                    "reservas": [
                        {
                            "id_reserva": 1,
                            "id_usuario": 60,
                            "id_inmueble": 3,
                            "estado": "confirmada",
                            "monto_total": 800.0,
                            "fecha_reserva": "2025-08-17T10:30:00"
                        }
                    ]
                },
                {
                    "mensaje": "No tienes reservas realizadas aún. ¡Explora nuestros inmuebles y haz tu primera reserva!",
                    "total_reservas": 0,
                    "reservas": []
                }
            ]
        }

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
