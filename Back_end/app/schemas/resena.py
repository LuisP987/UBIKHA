from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class EstadoResenaEnum(str, Enum):
    visible = "visible"
    oculta = "oculta"
    reportada = "reportada"

class ResenaCreate(BaseModel):
    id_inmueble: int
    calificacion: int  # 1-5
    comentario: Optional[str] = None

class ResenaOut(BaseModel):
    id_resena: int
    id_usuario: int
    id_inmueble: int
    calificacion: int
    comentario: Optional[str]
    fecha_resena: datetime
    estado_resena: str

    class Config:
        from_attributes = True

class ResenaUpdate(BaseModel):
    calificacion: Optional[int] = None
    comentario: Optional[str] = None
    estado_resena: Optional[EstadoResenaEnum] = None
