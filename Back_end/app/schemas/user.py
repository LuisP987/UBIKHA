from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginUsuario(BaseModel):
    email: EmailStr
    password: str

class UsuarioCrear(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None

class UsuarioMostrar(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: bool

    class Config:
        orm_mode = True
