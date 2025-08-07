"""
API para autenticación y registro con verificación por WhatsApp
Implementa el flujo completo de registro con verificación por WhatsApp
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from db.database import obtener_sesion
from services.whatsapp import WhatsAppService
from services.user import buscar_usuario_por_email, buscar_usuario_por_telefono, crear_usuario
from schemas.verification import PhoneVerification, CodeVerification, VerificationResponse
from schemas.user import RegistroUsuario, UsuarioMostrar
from utils.security.seguridad import hashear_password
from utils.security.jwt import crear_token
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Router para WhatsApp Auth
router = APIRouter(prefix="/whatsapp-auth", tags=["WhatsApp Authentication"])

# Instancia del servicio WhatsApp
whatsapp_service = WhatsAppService()

@router.get("/service/status")
async def verificar_estado_whatsapp():
    """
    🔍 Verificar estado del servicio WhatsApp
    
    Endpoint para verificar si el microservicio de WhatsApp está disponible
    """
    try:
        is_connected = await whatsapp_service.check_whatsapp_service_status()
        
        if is_connected:
            return {
                "success": True,
                "message": "Servicio WhatsApp conectado exitosamente",
                "data": {"conectado": True}
            }
        else:
            return {
                "success": False,
                "message": "Servicio WhatsApp no disponible",
                "data": {"conectado": False}
            }
            
    except Exception as e:
        logger.error(f"Error al verificar estado de WhatsApp: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Error al conectar con el servicio WhatsApp"
        )

@router.post("/enviar-codigo-registro", response_model=VerificationResponse)
async def enviar_codigo_registro(
    phone_data: PhoneVerification,
    db: AsyncSession = Depends(obtener_sesion)
):
    """
    📱 PASO 1: Enviar código de verificación para registro
    
    Envía un código de verificación de 6 dígitos al WhatsApp del usuario
    que desea registrarse. Antes verifica que el número no esté ya registrado.
    
    Args:
        phone_data: Datos del teléfono a verificar
        
    Returns:
        VerificationResponse: Respuesta con el estado del envío
    """
    try:
        # Verificar que el número no esté ya registrado
        usuario_existente = await buscar_usuario_por_telefono(db, phone_data.phone_number)
        if usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este número de teléfono ya está registrado. Usa el login en su lugar."
            )
        
        # Verificar estado del servicio WhatsApp
        service_available = await whatsapp_service.check_whatsapp_service_status()
        if not service_available:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="El servicio de WhatsApp no está disponible en este momento"
            )
        
        # Enviar código de verificación
        success = await whatsapp_service.send_verification_code(phone_data.phone_number)
        
        if success:
            logger.info(f"Código de registro enviado a {phone_data.phone_number}")
            return VerificationResponse(
                success=True,
                message="Código de verificación enviado exitosamente",
                data={"telefono": phone_data.phone_number}  # Solo 9 dígitos
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al enviar el código de verificación"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al enviar código: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/verificar-codigo-registro", response_model=VerificationResponse)
async def verificar_codigo_registro(verification: CodeVerification):
    """
    ✅ PASO 2: Verificar código de registro
    
    Verifica que el código de 6 dígitos enviado por WhatsApp sea correcto.
    Si es válido, el usuario puede proceder a completar su registro.
    
    Args:
        verification: Datos de verificación (teléfono y código)
        
    Returns:
        VerificationResponse: Respuesta con el estado de la verificación
    """
    try:
        # Verificar el código
        is_valid = await whatsapp_service.verify_code(
            verification.phone_number, 
            verification.code
        )
        
        if is_valid:
            logger.info(f"Código verificado exitosamente para {verification.phone_number}")
            return VerificationResponse(
                success=True,
                message="Número de teléfono verificado exitosamente",
                verified=True,
                data={
                    "telefono": verification.phone_number,  # Solo 9 dígitos
                    "verificado": True,
                    "siguiente_paso": "completar_registro"
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Código de verificación inválido o expirado"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al verificar código: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/completar-registro", response_model=dict)
async def completar_registro(
    datos_registro: RegistroUsuario,
    db: AsyncSession = Depends(obtener_sesion)
):
    """
    📝 PASO 3: Completar registro después de verificación
    
    Completa el registro del usuario después de que su número de teléfono
    haya sido verificado exitosamente por WhatsApp.
    
    Args:
        datos_registro: Datos completos del usuario para registro
        
    Returns:
        dict: Información del usuario registrado y token de acceso
    """
    try:
        # Verificar que el email no esté ya registrado
        usuario_email_existente = await buscar_usuario_por_email(db, datos_registro.email)
        if usuario_email_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este email ya está registrado"
            )
        
        # Verificar que el teléfono no esté ya registrado
        usuario_telefono_existente = await buscar_usuario_por_telefono(db, datos_registro.num_celular)
        if usuario_telefono_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este número de teléfono ya está registrado"
            )
        
        # Crear el usuario
        datos_dict = datos_registro.dict()
        datos_dict['password'] = hashear_password(datos_dict['password'])
        datos_dict['telefono_verificado'] = True  # Marcar como verificado
        
        nuevo_usuario = await crear_usuario(db, datos_dict)
        
        # Crear token de acceso
        token = crear_token({"sub": str(nuevo_usuario.id_usuario)})
        
        # Enviar mensaje de bienvenida por WhatsApp
        try:
            await whatsapp_service.send_welcome_message(datos_registro.num_celular, datos_registro.nombres)
        except Exception as e:
            logger.warning(f"Error al enviar mensaje de bienvenida: {e}")
            # No fallar el registro si no se puede enviar el mensaje de bienvenida
        
        logger.info(f"Usuario registrado exitosamente: {nuevo_usuario.id_usuario}")
        
        return {
            "mensaje": "Usuario registrado exitosamente",
            "usuario": {
                "id": nuevo_usuario.id_usuario,
                "nombres": nuevo_usuario.nombres,
                "apellidos": nuevo_usuario.apellidos,
                "email": nuevo_usuario.email,
                "num_celular": nuevo_usuario.num_celular,
                "tipo_usuario": nuevo_usuario.tipo_usuario,
                "telefono_verificado": True
            },
            "access_token": token,
            "token_type": "bearer"
        }
        
    except IntegrityError as e:
        await db.rollback()
        if "usuarios_email_key" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este email ya está registrado"
            )
        elif "usuarios_num_celular_key" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este número de teléfono ya está registrado"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error de integridad en la base de datos"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en el registro: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/estadisticas")
async def obtener_estadisticas_verificacion():
    """
    📊 Obtener estadísticas de verificaciones
    
    Endpoint para obtener información sobre el estado de las verificaciones
    """
    try:
        # Limpiar códigos expirados
        expired_count = whatsapp_service.clean_expired_codes()
        
        # Obtener estadísticas
        pending_count = whatsapp_service.get_pending_verifications_count()
        
        return {
            "pending_verifications": pending_count,
            "expired_codes_cleaned": expired_count,
            "service_status": await whatsapp_service.check_whatsapp_service_status()
        }
        
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )
