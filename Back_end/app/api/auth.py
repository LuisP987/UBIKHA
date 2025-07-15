from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import LoginUsuario
from db.database import obtener_sesion
from crud.user import buscar_usuario_por_email
from utils.seguridad import verificar_password
from utils.jwt import crear_token

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/login")
async def login(datos: LoginUsuario, db: AsyncSession = Depends(obtener_sesion)):
    # Buscar al usuario en la base de datos por su email
    usuario = await buscar_usuario_por_email(db, datos.email)
    
    # Verificar si el usuario existe y la contraseña es correcta
    if not usuario or not verificar_password(datos.password, usuario.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

    # Generar JWT (con rol incluido)
    token = crear_token({
        "sub": usuario.email,
        "id": usuario.id,
        "rol": usuario.rol  # 👈 incluir el rol en el token (útil para autorización futura)
    })

    # Retornar token y datos del usuario
    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": usuario.email,
        "rol": usuario.rol  # 👈 Mostrar rol en la respuesta también
    }
