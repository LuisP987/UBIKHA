from jose import JWTError, jwt, ExpiredSignatureError
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import obtener_sesion
from services.user import buscar_usuario_por_email, buscar_usuario_por_celular  # asegúrate de tener esto

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if SECRET_KEY is None:
    raise ValueError("SECRET_KEY no está configurada en .env")

ALGORITHM = "HS256"
EXPIRACION_MINUTOS = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

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
    except ExpiredSignatureError:
        return {"error": "token_expired"}
    except JWTError:
        return {"error": "token_invalid"}

async def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(obtener_sesion)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        num_celular: str = payload.get("sub")
        if num_celular is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: falta información del usuario",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado. Por favor, inicia sesión nuevamente",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o corrupto",
            headers={"WWW-Authenticate": "Bearer"},
        )

    usuario = await buscar_usuario_por_celular(db, num_celular)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado. El token puede estar vinculado a un usuario eliminado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return usuario

