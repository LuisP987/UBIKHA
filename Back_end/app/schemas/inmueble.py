from pydantic import BaseModel
from typing import Optional
from enum import Enum

class InmuebleCreate(BaseModel):
    id_propietario: int
    titulo: str
    descripcion: Optional[str] = None
    precio_mensual: float
    tipo_inmueble: str

class InmuebleOut(BaseModel):
    id_inmueble: int
    id_propietario: int
    titulo: str
    descripcion: Optional[str]
    precio_mensual: float
    tipo_inmueble: str
    estado: str

class InmuebleUpdate(BaseModel):
    precio: Optional[float]
    tipo_inmueble: Optional[str]
    descripcion: Optional[str]
    estado: Optional[str]

    class Config:
        extra = "forbid"

class EstadoInmuebleEnum(str, Enum):
    disponible = "disponible"
    ocupado = "ocupado"
    vendido = "vendido"

class EstadoInmueble(BaseModel):
    estado: EstadoInmuebleEnum