from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

# Enum para los tipos de reporte (según el modal de la imagen)
class TipoReporteEnum(str, Enum):
    incorrecto_impreciso = "Es incorrecto o poco preciso"
    no_alojamiento_real = "No es un alojamiento real"
    estafa = "Es una estafa"
    ofensivo = "Es ofensivo"
    otra_cosa = "Es otra cosa"

class EstadoReporteEnum(str, Enum):
    pendiente = "pendiente"
    en_revision = "en_revision"
    resuelto = "resuelto"
    rechazado = "rechazado"

# Schema para crear reporte (paso 1: seleccionar tipo)
class ReporteCreatePaso1(BaseModel):
    id_inmueble: int = Field(..., description="ID del inmueble a reportar")
    tipo_reporte: TipoReporteEnum = Field(..., description="Tipo de reporte seleccionado")

# Schema para completar reporte (paso 2: agregar comentarios)
class ReporteCreateCompleto(BaseModel):
    id_inmueble: int = Field(..., description="ID del inmueble a reportar")
    tipo_reporte: TipoReporteEnum = Field(..., description="Tipo de reporte seleccionado")
    comentario: str = Field(
        ..., 
        min_length=10, 
        max_length=500, 
        description="Comentario detallado sobre el reporte"
    )

# Schema legacy para compatibilidad
class ReporteCreate(BaseModel):
    id_inmueble: int
    tipo_reporte: str
    descripcion: Optional[str] = None

# Schema para mostrar reportes
class ReporteOut(BaseModel):
    id_reporte: int
    id_usuario: int
    id_inmueble: int
    tipo_reporte: str
    descripcion: str  # Cambiado a required ya que la BD lo requiere
    fecha_reporte: datetime
    estado_reporte: str
    # Información adicional del inmueble reportado
    titulo_inmueble: Optional[str] = None
    propietario_inmueble: Optional[str] = None

    class Config:
        from_attributes = True

# Schema para actualizar estado de reporte (administradores)
class ReporteUpdate(BaseModel):
    estado_reporte: EstadoReporteEnum
    # Removido comentario_admin ya que no existe en la BD

# Schema para respuesta de creación de reporte
class ReporteCreateResponse(BaseModel):
    mensaje: str
    id_reporte: int
    tipo_reporte: str
    estado: str
    fecha_reporte: datetime
