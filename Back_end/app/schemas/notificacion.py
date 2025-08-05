from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class EstadoNotificacionEnum(str, Enum):
    no_leida = "no_leida"
    leida = "leida"

class NotificacionOut(BaseModel):
    id_notificacion: int
    id_usuario: int
    mensaje: str
    fecha_notificacion: datetime
    estado_notificacion: str

    class Config:
        from_attributes = True

class NotificacionUpdate(BaseModel):
    estado_notificacion: EstadoNotificacionEnum
