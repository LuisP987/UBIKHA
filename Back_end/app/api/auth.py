from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import LoginUsuario, RegistroUsuario, UsuarioMostrar
from db.database import obtener_sesion
from services.user import buscar_usuario_por_email, crear_usuario
from utils.security.seguridad import verificar_password, hashear_password
from utils.security.jwt import crear_token, obtener_usuario_actual
from schemas.verification import PhoneVerification, CodeVerification
from services.whatsapp import WhatsAppService
from schemas.user import CambiarPassword, UsuarioActualizar
from models.user import Usuario

router = APIRouter(prefix="/auth", tags=["Autenticación"])
#verification de telefono
whatsapp_service = WhatsAppService()


# 🚪 LOGIN
@router.post("/login")
async def login(datos: LoginUsuario, db: AsyncSession = Depends(obtener_sesion)):
    usuario = await buscar_usuario_por_email(db, datos.email)
    
    if not usuario or not verificar_password(datos.password, usuario.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

    token = crear_token({
        "sub": usuario.email,
        "id": usuario.id_usuario,
        "rol": usuario.tipo_usuario
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": usuario.email,
        "rol": usuario.tipo_usuario
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

    # Convertir a diccionario y hashear la contraseña
    datos_dict = datos.dict()
    datos_dict["password"] = hashear_password(datos.password)

    # Crear nuevo usuario en la BD
    nuevo_usuario = await crear_usuario(db, datos_dict)

    return {
        "mensaje": "Usuario registrado exitosamente",
        "usuario": nuevo_usuario.email
    }

@router.post("/enviar-codigo")
async def Enviar_Codigo(phone: PhoneVerification):
    success = await whatsapp_service.send_code(phone.phone_number)
    if not success:
        raise HTTPException(status_code=500, detail="Error sending verification code")
    return {"message": "Enviar codigo"}

@router.post("/verificar-codigo")
async def Verificar_Codigo(verification: CodeVerification):
    if whatsapp_service.verify_code(verification.phone_number, verification.code):
        return {"verified": True}
    raise HTTPException(status_code=400, detail="Invalid verification code")

@router.put("/{email}/perfil")
async def actualizar_perfil(datos: UsuarioActualizar,email: str, db: AsyncSession = Depends(obtener_sesion)):
    usuario = await buscar_usuario_por_email(db, email)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Actualiza los campos permitidos
    usuario.nombres = datos.nombres
    usuario.apellido_paterno = datos.apellido_paterno
    usuario.apellido_materno = datos.apellido_materno
    usuario.num_celular = datos.num_celular
    

    await db.commit()
    await db.refresh(usuario)
    return {"mensaje": "Perfil actualizado", "usuario": usuario.email}

@router.post("/{email}/cambiar-password")
async def cambiar_password(datos: CambiarPassword ,email: str, db: AsyncSession = Depends(obtener_sesion)):
    usuario = await buscar_usuario_por_email(db, email)
    if not usuario or not verificar_password(datos.password_actual, usuario.password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    usuario.hashed_password = hashear_password(datos.password_nueva)
    await db.commit()
    await db.refresh(usuario)
    return {"mensaje": "Contraseña actualizada correctamente"}

@router.get("/perfil", response_model=UsuarioMostrar)
async def obtener_perfil(usuario: Usuario = Depends(obtener_usuario_actual)):
    return usuario