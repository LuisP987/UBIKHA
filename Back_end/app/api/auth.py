from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import LoginUsuario, RegistroUsuario, UsuarioMostrar, UsuarioPerfilCompleto
from schemas.user import CambiarPassword, UsuarioActualizar, CambiarCelular
from db.database import obtener_sesion
from services.user import buscar_usuario_por_email, buscar_usuario_por_celular, crear_usuario, actualizar_usuario
from utils.security.seguridad import verificar_password, hashear_password, es_password_hasheada
from utils.security.jwt import crear_token, obtener_usuario_actual
from utils.security.error_messages import AuthErrorMessages
from schemas.verification import PhoneVerification, CodeVerification
from services.whatsapp import WhatsAppService
from schemas.user import CambiarPassword, UsuarioActualizar, CambiarCelular
from models.usuario import Usuario
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/auth", tags=["Autenticación"])

#verification de telefono
whatsapp_service = WhatsAppService()

# 🚪 LOGIN - OAuth2 compatible con Swagger
@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(obtener_sesion)
):
    # En OAuth2PasswordRequestForm, el número de celular viene en form_data.username
    usuario = await buscar_usuario_por_celular(db, form_data.username)
    
    if not usuario or not verificar_password(form_data.password, usuario.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AuthErrorMessages.INVALID_CREDENTIALS,
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = crear_token({
        "sub": usuario.num_celular,
        "id": usuario.id_usuario,
        "rol": usuario.tipo_usuario
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": usuario.num_celular,
        "rol": usuario.tipo_usuario
    }

# 🚪 LOGIN ALTERNATIVO - Para usar con JSON (opcional)
@router.post("/login-json")
async def login_json(datos: LoginUsuario, db: AsyncSession = Depends(obtener_sesion)):
    usuario = await buscar_usuario_por_celular(db, datos.num_celular)
    
    if not usuario or not verificar_password(datos.password, usuario.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AuthErrorMessages.INVALID_CREDENTIALS
        )

    token = crear_token({
        "sub": usuario.num_celular,
        "id": usuario.id_usuario,
        "rol": usuario.tipo_usuario
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": usuario.num_celular,
        "rol": usuario.tipo_usuario
    }

# 📝 REGISTRO (mejorado con manejo de errores)
@router.post("/registro", status_code=status.HTTP_201_CREATED)
async def registro(datos: RegistroUsuario, db: AsyncSession = Depends(obtener_sesion)):
    try:
        # Verificar si el email ya existe
        usuario_existente_email = await buscar_usuario_por_email(db, datos.email)
        if usuario_existente_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=AuthErrorMessages.EMAIL_ALREADY_EXISTS
            )
        
        # Verificar si el número de celular ya existe
        usuario_existente_celular = await buscar_usuario_por_celular(db, datos.num_celular)
        if usuario_existente_celular:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El número de celular ya está registrado"
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
                detail=AuthErrorMessages.EMAIL_ALREADY_EXISTS
            )
        elif "usuarios_num_celular_key" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=AuthErrorMessages.PHONE_ALREADY_EXISTS
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=AuthErrorMessages.INTERNAL_SERVER_ERROR
            )

# 👤 PERFIL
@router.get("/perfil", response_model=UsuarioPerfilCompleto)
async def obtener_perfil(usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    """
    Obtiene el perfil completo del usuario autenticado.
    Retorna toda la información disponible del usuario excepto la contraseña.
    """
    return usuario_actual

# 👤 PERFIL BÁSICO (información mínima)
@router.get("/perfil-basico", response_model=UsuarioMostrar)
async def obtener_perfil_basico(usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    """
    Obtiene información básica del perfil del usuario autenticado.
    Para casos donde no se necesita toda la información.
    """
    return usuario_actual

# 🔍 VERIFICAR TOKEN (nuevo endpoint)
@router.get("/verificar-token")
async def verificar_token_estado(usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    """
    Endpoint para verificar si el token actual es válido y no ha expirado.
    Útil para el frontend para verificar el estado de autenticación.
    """
    return {
        "valid": True,
        "user_id": usuario_actual.id_usuario,
        "email": usuario_actual.email,
        "role": usuario_actual.tipo_usuario,
        "message": "Token válido"
    }

# ✏️ ACTUALIZAR PERFIL
@router.put("/perfil", response_model=UsuarioPerfilCompleto)
async def actualizar_perfil(
    datos: UsuarioActualizar,
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Actualiza los datos del perfil del usuario autenticado.
    
    - Solo actualiza los campos que se envían (campos no incluidos se mantienen igual)
    - El número de celular NO se puede cambiar por seguridad (usar /auth/cambiar-celular)
    - Para cambiar número de celular, usar el endpoint específico
    
    Campos actualizables:
    - nombres
    - apellido_paterno  
    - apellido_materno
    - email
    - fecha_nacimiento
    """
    try:
        # Convertir a diccionario solo con campos que fueron enviados
        datos_enviados = datos.model_dump(exclude_unset=True)
        
        # Filtrar solo valores que no son None
        datos_actualizacion = {
            campo: valor 
            for campo, valor in datos_enviados.items() 
            if valor is not None
        }
        
        if not datos_actualizacion:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se proporcionaron datos para actualizar"
            )
        
        # Log para debug
        print(f"Datos a actualizar: {datos_actualizacion}")
        
        usuario_actualizado = await actualizar_usuario(db, usuario_actual.id_usuario, datos_actualizacion)
        
        if not usuario_actualizado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=AuthErrorMessages.USER_NOT_FOUND_GENERAL
            )
        
        return usuario_actualizado
        
    except ValueError as e:
        # Error de validación de negocio (email duplicado, etc.)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,  # Conflict
            detail=str(e)
        )
    except IntegrityError as e:
        await db.rollback()
        if "usuarios_email_key" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=AuthErrorMessages.EMAIL_ALREADY_EXISTS
            )
        elif "usuarios_num_celular_key" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=AuthErrorMessages.PHONE_ALREADY_EXISTS
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error de integridad en la base de datos: {str(e)}"
            )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

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
            detail=AuthErrorMessages.CURRENT_PASSWORD_INCORRECT
        )
    
    nuevo_password_hash = hashear_password(datos.password_nueva)
    usuario_actual.password = nuevo_password_hash
    
    await db.commit()
    return {"mensaje": "Password actualizada exitosamente"}

# 📱 CAMBIAR CELULAR
@router.put("/cambiar-celular", response_model=UsuarioPerfilCompleto)
async def cambiar_celular(
    datos: CambiarCelular,
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Cambia el número de celular del usuario.
    
    ⚠️ IMPORTANTE: Esto puede afectar tu forma de login si usas el celular para autenticarte.
    
    Requiere:
    - Contraseña actual para confirmar
    - Número de celular peruano válido (9 dígitos, empieza con 9)
    """
    try:
        # Verificar contraseña actual
        if not verificar_password(datos.password, usuario_actual.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contraseña incorrecta"
            )
        
        # Verificar que el nuevo celular no exista (si lo usas para login)
        from sqlalchemy.future import select
        stmt = select(Usuario).where(
            Usuario.num_celular == datos.nuevo_celular,
            Usuario.id_usuario != usuario_actual.id_usuario
        )
        result = await db.execute(stmt)
        celular_existente = result.scalar_one_or_none()
        
        if celular_existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este número de celular ya está siendo usado por otro usuario"
            )
        
        # Verificar que el nuevo celular no sea el mismo que el actual
        if datos.nuevo_celular == usuario_actual.num_celular:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nuevo número de celular es igual al actual"
            )
        
        # Actualizar el celular
        usuario_actual.num_celular = datos.nuevo_celular
        usuario_actual.celular_verificado = False  # Marcar como no verificado
        from datetime import datetime
        usuario_actual.fecha_actualizacion = datetime.now()
        
        await db.commit()
        await db.refresh(usuario_actual)
        
        return usuario_actual
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

#-------------------- VERIFICACION POR WHATSAPP --------------------

# ENDPOINT: Enviar código de verificación por WhatsApp
@router.post("/enviar-codigo")
async def enviar_codigo(phone: PhoneVerification):
    success = await whatsapp_service.send_verification_code(phone.phone_number)
    if success:
        return {"message": "Código enviado exitosamente"}
    else:
        raise HTTPException(status_code=500, detail=AuthErrorMessages.CODE_SEND_ERROR)

# ENDPOINT: Verificar código de WhatsApp
@router.post("/verificar-codigo")
async def verificar_codigo(verification: CodeVerification):
    is_valid = await whatsapp_service.verify_code(verification.phone_number, verification.code)
    if is_valid:
        return {"message": "Código verificado exitosamente", "verified": True}
    else:
        raise HTTPException(status_code=400, detail=AuthErrorMessages.INVALID_VERIFICATION_CODE)

# ENDPOINT: Corregir contraseñas no hasheadas (TEMPORAL - SOLO PARA DESARROLLO)
@router.post("/corregir-passwords")
async def corregir_passwords(db: AsyncSession = Depends(obtener_sesion)):
    """
    Endpoint temporal para corregir contraseñas que no están hasheadas correctamente.
    SOLO USAR EN DESARROLLO.
    """
    try:
        from sqlalchemy import select, update
        from models.usuario import Usuario
        
        # Buscar todos los usuarios
        resultado = await db.execute(select(Usuario))
        usuarios = resultado.scalars().all()
        
        usuarios_corregidos = 0
        
        for usuario in usuarios:
            # Verificar si la contraseña no está hasheada
            if not es_password_hasheada(usuario.password):
                # Hashear la contraseña en texto plano
                nuevo_hash = hashear_password(usuario.password)
                
                # Actualizar en la base de datos
                await db.execute(
                    update(Usuario)
                    .where(Usuario.id_usuario == usuario.id_usuario)
                    .values(password=nuevo_hash)
                )
                usuarios_corregidos += 1
        
        await db.commit()
        
        return {
            "message": f"Se corrigieron {usuarios_corregidos} contraseñas",
            "usuarios_procesados": len(usuarios),
            "usuarios_corregidos": usuarios_corregidos
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al corregir contraseñas: {str(e)}"
        )
