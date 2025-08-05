from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ImagenCreate(BaseModel):
    id_inmueble: int
    url_imagen: str

class ImagenOut(BaseModel):
    id_imagen: int
    id_inmueble: int
    url_imagen: str
    fecha_subida: datetime

    class Config:
        from_attributes = True
