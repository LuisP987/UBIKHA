from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import LoginUsuario, RegistroUsuario
from db.database import obtener_sesion
from services.user import buscar_usuario_por_email, crear_usuario
from utils.security.seguridad import verificar_password, hashear_password
from utils.security.jwt import crear_token

router = APIRouter(prefix="/auth", tags=["Autenticación"])

# 🚪 LOGIN
@router.post("/login")
async def login(datos: LoginUsuario, db: AsyncSession = Depends(obtener_sesion)):
    usuario = await buscar_usuario_por_email(db, datos.email)
    
    if not usuario or not verificar_password(datos.password, usuario.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

    token = crear_token({
        "sub": usuario.email,
        "id": usuario.id,
        "rol": usuario.rol
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": usuario.email,
        "rol": usuario.rol
    }


# 📝 REGISTRO
@router.post("/registro", status_code=201)
async def registro(datos: RegistroUsuario, db: AsyncSession = Depends(obtener_sesion)):
    # Verificar si el email ya está en uso
    existente = await buscar_usuario_por_email(db, datos.email)
    if existente:
        raise HTTPException(
            status_code=400,
            detail="El correo ya está registrado."
        )
    
    # Encriptar la contraseña antes de guardarla
    datos_dict = datos.dict()
    datos_dict["hashed_password"] = hashear_password(datos.password)
    del datos_dict["password"]  # ya no necesitamos el campo original

    # Crear nuevo usuario en la BD
    nuevo_usuario = await crear_usuario(db, datos_dict)

    return {
        "mensaje": "Usuario registrado exitosamente",
        "usuario": nuevo_usuario.email
    }
