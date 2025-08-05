from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class EstadoReporteEnum(str, Enum):
    pendiente = "pendiente"
    en_revision = "en_revision"
    resuelto = "resuelto"
    rechazado = "rechazado"

class ReporteCreate(BaseModel):
    id_inmueble: int
    motivo: str
    descripcion: Optional[str] = None

class ReporteOut(BaseModel):
    id_reporte: int
    id_usuario: int
    id_inmueble: int
    motivo: str
    descripcion: Optional[str]
    fecha_reporte: datetime
    estado_reporte: str

    class Config:
        from_attributes = True

class ReporteUpdate(BaseModel):
    estado_reporte: EstadoReporteEnum
