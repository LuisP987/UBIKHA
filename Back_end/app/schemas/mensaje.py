from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MensajeCreate(BaseModel):
    id_remitente: int
    id_destinatario: int
    contenido: str

class MensajeOut(BaseModel):
    id_mensaje: int
    id_remitente: int
    id_destinatario: int
    contenido: str
    fecha_envio: datetime
    estado_mensaje: str

    class Config:
        from_attributes = True
