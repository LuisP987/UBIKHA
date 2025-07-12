from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import LoginUsuario
from db.database import obtener_sesion
from crud.user import buscar_usuario_por_email
from utils.seguridad import verificar_password


print("⚡ auth.py cargado")
router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/login")
async def login(datos: LoginUsuario, db: AsyncSession = Depends(obtener_sesion)):
    usuario = await buscar_usuario_por_email(db, datos.email)
    
    if not usuario or not verificar_password(datos.password, usuario.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    return {"mensaje": "Inicio de sesión exitoso", "usuario": usuario.email}
