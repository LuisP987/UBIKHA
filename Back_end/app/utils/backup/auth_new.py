from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import LoginUsuario, RegistroUsuario, UsuarioMostrar
from db.database import obtener_sesion
from services.user import buscar_usuario_por_email, crear_usuario
from utils.security.seguridad import verificar_password, hashear_password
from utils.security.jwt import crear_token, obtener_usuario_actual
from schemas.verification import PhoneVerification, CodeVerification
from services.whatsapp import WhatsAppService
from schemas.user import CambiarPassword, UsuarioActualizar
from models.usuario import Usuario
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/auth", tags=["Autenticación"])

# Constantes
CREDENCIALES_INVALIDAS = "Credenciales inválidas"

#verification de telefono
whatsapp_service = WhatsAppService()

# 🚪 LOGIN - OAuth2 compatible con Swagger
@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(obtener_sesion)
):
    # En OAuth2PasswordRequestForm, el email viene en form_data.username
    usuario = await buscar_usuario_por_email(db, form_data.username)
    
    if not usuario or not verificar_password(form_data.password, usuario.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=CREDENCIALES_INVALIDAS,
            headers={"WWW-Authenticate": "Bearer"},
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

# 🚪 LOGIN ALTERNATIVO - Para usar con JSON (opcional)
@router.post("/login-json")
async def login_json(datos: LoginUsuario, db: AsyncSession = Depends(obtener_sesion)):
    usuario = await buscar_usuario_por_email(db, datos.email)
    
    if not usuario or not verificar_password(datos.password, usuario.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=CREDENCIALES_INVALIDAS
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

# 📝 REGISTRO (mejorado con manejo de errores)
@router.post("/registro", status_code=status.HTTP_201_CREATED)
async def registro(datos: RegistroUsuario, db: AsyncSession = Depends(obtener_sesion)):
    try:
        # Verificar si el usuario ya existe
        usuario_existente = await buscar_usuario_por_email(db, datos.email)
        if usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        # Crear nuevo usuario
        datos_dict = datos.dict()
        nuevo_usuario = await crear_usuario(db, datos_dict)
        return {
            "mensaje": "Usuario registrado exitosamente", 
            "usuario_id": nuevo_usuario.id_usuario,
            "rol": nuevo_usuario.tipo_usuario
        }
        
    except IntegrityError as e:
        await db.rollback()
        if "usuarios_email_key" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        elif "usuarios_num_celular_key" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El número de celular ya está registrado. Usa un número diferente."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )

# 👤 PERFIL
@router.get("/perfil", response_model=UsuarioMostrar)
async def obtener_perfil(usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    return usuario_actual

# ✏️ ACTUALIZAR PERFIL
@router.put("/perfil", response_model=UsuarioMostrar)
async def actualizar_perfil(
    datos: UsuarioActualizar,
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    from services.user import actualizar_usuario
    usuario_actualizado = await actualizar_usuario(db, usuario_actual.id_usuario, datos)
    
    if not usuario_actualizado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return usuario_actualizado

# 🔐 CAMBIAR PASSWORD
@router.post("/cambiar-password")
async def cambiar_password(
    datos: CambiarPassword,
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    if not verificar_password(datos.password_actual, usuario_actual.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password actual incorrecta"
        )
    
    nuevo_password_hash = hashear_password(datos.password_nueva)
    usuario_actual.password = nuevo_password_hash
    
    await db.commit()
    return {"mensaje": "Password actualizada exitosamente"}

#-------------------- VERIFICACION POR WHATSAPP --------------------

# ENDPOINT: Enviar código de verificación por WhatsApp
@router.post("/enviar-codigo")
async def enviar_codigo(phone: PhoneVerification):
    success = await whatsapp_service.send_verification_code(phone.phone_number)
    if success:
        return {"message": "Código enviado exitosamente"}
    else:
        raise HTTPException(status_code=500, detail="Error al enviar el código")

# ENDPOINT: Verificar código de WhatsApp
@router.post("/verificar-codigo")
async def verificar_codigo(verification: CodeVerification):
    is_valid = await whatsapp_service.verify_code(verification.phone_number, verification.code)
    if is_valid:
        return {"message": "Código verificado exitosamente", "verified": True}
    else:
        raise HTTPException(status_code=400, detail="Código inválido o expirado")
