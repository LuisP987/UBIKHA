from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from enum import Enum

# Enums para validaciones
class TipoInmuebleEnum(str, Enum):
    casa = "casa"
    cuarto = "cuarto"
    mini_departamento = "mini departamento"
    departamento = "departamento"

class EstadoInmuebleEnum(str, Enum):
    en_revision = "en revisión"
    disponible = "disponible"
    ocupado = "ocupado"
    rechazado = "rechazado"
    pausado = "pausado"

# Schema para crear inmueble (completo)
class InmuebleCreateCompleto(BaseModel):
    # Datos básicos del inmueble
    tipo_inmueble: TipoInmuebleEnum = Field(..., description="Tipo de inmueble (casa, cuarto, mini departamento, departamento)")
    titulo: str = Field(..., 
                        min_length=5, 
                        max_length=100, 
                        description="Título del inmueble (entre 5 y 100 caracteres)",
                        example="Casa familiar en San Isidro")
    descripcion: Optional[str] = Field(None, 
                                       max_length=500, 
                                       description="Descripción del inmueble (máximo 500 caracteres)",
                                       example="Hermosa casa de 3 pisos con jardín, completamente amoblada")
    precio_mensual: float = Field(..., 
                                  gt=0, 
                                  le=50000,
                                  description="Precio mensual del inmueble en soles (mínimo S/1, máximo S/50,000)",
                                  example=3600.00)
    
    # Datos de ubicación
    direccion: str = Field(..., 
                           min_length=10, 
                           max_length=255, 
                           description="Dirección completa del inmueble (incluir distrito de Lima)",
                           example="Av. Conquistadores 1245, San Isidro, Lima")
    referencias: Optional[str] = Field(None, 
                                       max_length=255, 
                                       description="Referencias adicionales de ubicación",
                                       example="Frente al parque Kennedy, edificio color azul")
    referencias: Optional[str] = Field(None, 
                                       max_length=255, 
                                       description="Referencias adicionales de ubicación",
                                       example="Frente al parque Kennedy, edificio color azul")
    
    # Cantidades (capacidad)
    huespedes: int = Field(..., 
                           ge=1, 
                           le=20, 
                           description="Número máximo de huéspedes (entre 1 y 20)",
                           example=4)
    habitaciones: int = Field(..., 
                              ge=0, 
                              le=10, 
                              description="Número de habitaciones (entre 0 y 10)",
                              example=3)
    banos: int = Field(..., 
                       ge=1, 
                       le=10, 
                       description="Número de baños (entre 1 y 10)",
                       example=2)
    camas: int = Field(..., 
                       ge=1, 
                       le=15, 
                       description="Número de camas (entre 1 y 15)",
                       example=3)
    
    # Servicios disponibles (todos ahora existen en la BD)
    wifi: bool = Field(default=False, description="¿Tiene WiFi?")
    cocina: bool = Field(default=False, description="¿Tiene cocina?")
    estacionamiento: bool = Field(default=False, description="¿Tiene estacionamiento?")
    television: bool = Field(default=False, description="¿Tiene televisión?")
    aire_acondicionado: bool = Field(default=False, description="¿Tiene aire acondicionado?")
    servicio_lavanderia: bool = Field(default=False, description="¿Tiene servicio de lavandería?")
    camaras_seguridad: bool = Field(default=False, description="¿Tiene cámaras de seguridad?")
    mascotas_permitidas: bool = Field(default=False, description="¿Permite mascotas?")
    
    @field_validator('titulo')
    @classmethod
    def validate_titulo(cls, v):
        if not v.strip():
            raise ValueError("El título no puede estar vacío")
        if len(v.strip()) < 5:
            raise ValueError("El título debe tener al menos 5 caracteres")
        return v.strip()
    
    @field_validator('descripcion')
    @classmethod
    def validate_descripcion(cls, v):
        if v and len(v.strip()) < 10:
            raise ValueError("La descripción debe tener al menos 10 caracteres si se proporciona")
        return v.strip() if v else None
    
    @field_validator('direccion')
    @classmethod
    def validate_direccion(cls, v):
        if not v.strip():
            raise ValueError("La dirección no puede estar vacía")
        if len(v.strip()) < 10:
            raise ValueError("La dirección debe ser más específica (mínimo 10 caracteres)")
        
        # Verificar que contenga palabras clave de Lima
        direccion_lower = v.lower()
        distritos_lima = ['lima', 'miraflores', 'san isidro', 'surco', 'la molina', 
                          'barranco', 'chorrillos', 'jesús maría', 'magdalena', 
                          'pueblo libre', 'san miguel', 'lince', 'breña', 'callao',
                          'san borja', 'providencia', 'independencia', 'los olivos',
                          'comas', 'villa el salvador', 'san juan de miraflores']
        
        if not any(distrito in direccion_lower for distrito in distritos_lima):
            raise ValueError("La dirección debe incluir un distrito válido de Lima Metropolitana")
        return v.strip()
    
    @field_validator('precio_mensual')
    @classmethod
    def validate_precio(cls, v):
        if v <= 0:
            raise ValueError("El precio debe ser mayor a S/0")
        if v > 50000:
            raise ValueError("El precio máximo es S/50,000 por mes")
        return round(v, 2)
    
    @field_validator('huespedes')
    @classmethod
    def validate_huespedes(cls, v):
        if v < 1:
            raise ValueError("Debe permitir al menos 1 huésped")
        if v > 20:
            raise ValueError("El máximo de huéspedes permitido es 20")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "tipo_inmueble": "casa",
                "titulo": "Casa familiar en San Isidro",
                "descripcion": "Hermosa casa de 3 pisos con jardín, completamente amoblada. Ideal para familias visitando Lima.",
                "precio_mensual": 3600.00,
                "direccion": "Av. Conquistadores 1245, San Isidro, Lima",
                "referencias": "Frente al parque Kennedy, edificio color azul",
                "huespedes": 4,
                "habitaciones": 3,
                "banos": 2,
                "camas": 3,
                "wifi": True,
                "cocina": True,
                "estacionamiento": True,
                "television": True,
                "aire_acondicionado": False,
                "servicio_lavanderia": True,
                "camaras_seguridad": True,
                "mascotas_permitidas": False
            }
        }

# Schema simplificado para compatibilidad (se elimina id_propietario)
class InmuebleCreate(BaseModel):
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
    precio_final: Optional[float] = None  # Precio con comisión de UBIKHA incluida
    tipo_inmueble: str
    estado: str
    # Datos de ubicación
    direccion: Optional[str] = None
    referencias: Optional[str] = None
    # Capacidad
    huespedes: Optional[int] = None
    habitaciones: Optional[int] = None
    banos: Optional[int] = None
    camas: Optional[int] = None
    # Servicios disponibles (todos los campos restaurados)
    wifi: bool = False
    cocina: bool = False
    estacionamiento: bool = False
    television: bool = False
    aire_acondicionado: bool = False
    servicio_lavanderia: bool = False
    camaras_seguridad: bool = False
    mascotas_permitidas: bool = False

    class Config:
        from_attributes = True

class InmuebleUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=5, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    precio_mensual: Optional[float] = Field(None, gt=0)
    tipo_inmueble: Optional[TipoInmuebleEnum] = None
    estado: Optional[EstadoInmuebleEnum] = None
    # Ubicación
    direccion: Optional[str] = Field(None, min_length=10, max_length=255)
    referencias: Optional[str] = Field(None, max_length=255)
    # Capacidad
    huespedes: Optional[int] = Field(None, ge=1, le=20)
    habitaciones: Optional[int] = Field(None, ge=0, le=10)
    banos: Optional[int] = Field(None, ge=1, le=10)
    camas: Optional[int] = Field(None, ge=1, le=15)
    # Servicios (todos los campos restaurados)
    wifi: Optional[bool] = None
    cocina: Optional[bool] = None
    estacionamiento: Optional[bool] = None
    television: Optional[bool] = None
    aire_acondicionado: Optional[bool] = None
    servicio_lavanderia: Optional[bool] = None
    camaras_seguridad: Optional[bool] = None
    mascotas_permitidas: Optional[bool] = None

    class Config:
        extra = "forbid"

class EstadoInmueble(BaseModel):
    estado: EstadoInmuebleEnum

# Schema para respuesta de creación
class InmuebleCreateResponse(BaseModel):
    mensaje: str
    id_inmueble: int
    estado: str
    precio_mensual: float
    precio_final: float
    comision_ubikha: float
    nuevo_rol_usuario: str

# Schema para listado de inmuebles con mensajes informativos
class ListaInmueblesResponse(BaseModel):
    """Respuesta completa para el listado de inmuebles"""
    mensaje: str = Field(..., description="Mensaje descriptivo sobre los inmuebles encontrados")
    total_inmuebles: int = Field(..., description="Número total de inmuebles encontrados")
    filtros_aplicados: Optional[dict] = Field(None, description="Filtros que se aplicaron en la búsqueda")
    inmuebles: List[InmuebleOut] = Field(..., description="Lista de inmuebles (puede estar vacía)")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "mensaje": "Se encontraron 5 inmuebles disponibles",
                    "total_inmuebles": 5,
                    "filtros_aplicados": {"tipo_inmueble": "casa"},
                    "inmuebles": []
                },
                {
                    "mensaje": "No se encontraron inmuebles que coincidan con tus criterios. Intenta ajustar los filtros o explora todas las opciones disponibles.",
                    "total_inmuebles": 0,
                    "filtros_aplicados": {"tipo_inmueble": "mansión"},
                    "inmuebles": []
                }
            ]
        }