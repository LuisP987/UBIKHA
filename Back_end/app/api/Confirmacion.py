from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.database import obtener_sesion
from models.user import Usuario as User
from utils.email_utils import enviar_codigo_verificacion
import secrets

router = APIRouter(prefix="/verificacion", tags=["Verificación"])

# Diccionario temporal para guardar los códigos de verificación
codigos_temporales = {}  # En producción usa Redis o base de datos

@router.post("/enviar-codigo")
async def enviar_codigo(email: str, db: AsyncSession = Depends(obtener_sesion)):
    result = await db.execute(select(User).where(User.email == email))
    usuario = result.scalars().first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    codigo = str(secrets.randbelow(1000000)).zfill(6)
    codigos_temporales[email] = codigo
    print(f"[DEBUG] Código generado para {email}: {codigo}")

    enviar_codigo_verificacion(email, codigo)

    return {"mensaje": f"Código enviado a {email}"}

@router.post("/validar-codigo")
async def validar_codigo(email: str, codigo: str):
    codigo_almacenado = codigos_temporales.get(email)

    if not codigo_almacenado:
        raise HTTPException(status_code=404, detail="No se encontró un código para este email")
    if codigo != codigo_almacenado:
        raise HTTPException(status_code=400, detail="Código incorrecto")

    return {"mensaje": "Código verificado correctamente"}
