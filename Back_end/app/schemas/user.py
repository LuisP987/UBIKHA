from pydantic import BaseModel, EmailStr

class LoginUsuario(BaseModel):
    email: EmailStr
    password: str