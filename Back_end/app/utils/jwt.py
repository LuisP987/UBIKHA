from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv() 

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
EXPIRACION_MINUTOS = 60

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
