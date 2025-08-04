from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import obtener_sesion
from services.user import buscar_usuario_por_email  # asegúrate de tener esto

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if SECRET_KEY is None:
    raise ValueError("SECRET_KEY no está configurada en .env")

ALGORITHM = "HS256"
EXPIRACION_MINUTOS = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def crear_token(data: dict):
    datos_a_codificar = data.copy()
    expiracion = datetime.utcnow() + timedelta(minutes=EXPIRACION_MINUTOS)
    datos_a_codificar.update({"exp": expiracion})
    token_jwt = jwt.encode(datos_a_codificar, SECRET_KEY, algorithm=ALGORITHM)
    return token_jwt

def verificar_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

async def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(obtener_sesion)
):
    credenciales_incorrectas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credenciales_incorrectas
    except JWTError:
        raise credenciales_incorrectas

    usuario = await buscar_usuario_por_email(db, email)
    if usuario is None:
        raise credenciales_incorrectas

    return usuario

