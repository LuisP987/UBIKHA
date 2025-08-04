from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class LoginUsuario(BaseModel):
    email: EmailStr
    password: str

class UsuarioCrear(BaseModel):
    nombres: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    num_celular: Optional[str] = None
    fecha_nacimiento: Optional[datetime] = None
    email: EmailStr
    password: str  # Esto luego lo puedes hashear

class UsuarioMostrar(BaseModel):
    id_usuario: int
    email: EmailStr
    tipo_usuario: str
    activo: bool

    class Config:
        from_attributes = True  # Para compatibilidad con SQLAlchemy
        
class RegistroUsuario(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str = Field(..., max_length=100)

class UsuarioActualizar(BaseModel):
    full_name: Optional[str]
    password: Optional[str]
    phone_number: Optional[str]

class CambiarPassword(BaseModel):
    email: EmailStr
    password_actual: str
    password_nueva: str

class UsuarioEstado(BaseModel):
    activo: bool