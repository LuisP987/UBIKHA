"""
API para autenticación y registro con verificación por WhatsApp
Implementa el flujo completo de registro con verificación por WhatsApp
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from db.database import obtener_sesion
from services.whatsapp import WhatsAppService
from services.user import buscar_usuario_por_email, buscar_usuario_por_telefono, crear_usuario
from schemas.verification import PhoneVerification, CodeVerification, VerificationResponse
from schemas.user import RegistroUsuario, UsuarioMostrar, RegistroCompletarWhatsApp
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
    datos_registro: RegistroCompletarWhatsApp,
    num_celular: str = Query(..., description="Número de celular verificado (debe coincidir con la verificación previa)"),
    db: AsyncSession = Depends(obtener_sesion)
):
    """
    📝 PASO 3: Completar registro después de verificación
    
    Completa el registro del usuario después de que su número de teléfono
    haya sido verificado exitosamente por WhatsApp.
    
    IMPORTANTE: El número de celular debe haber sido verificado previamente 
    usando los endpoints /enviar-codigo y /verificar-codigo.
    
    Args:
        datos_registro: Datos del usuario (sin num_celular)
        num_celular: Número verificado previamente por WhatsApp (query parameter)
        
    Returns:
        dict: Información del usuario registrado y token de acceso
    """
    try:
        # Validar formato del número de celular
        numero_limpio = num_celular.strip().replace(' ', '').replace('-', '')
        if not numero_limpio.isdigit() or len(numero_limpio) != 9 or not numero_limpio.startswith('9'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Número de celular inválido. Debe tener 9 dígitos y empezar con 9"
            )
        
        # Verificar que el teléfono haya sido verificado previamente
        if not whatsapp_service.is_phone_verified(numero_limpio):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este número de teléfono no ha sido verificado. Complete primero el proceso de verificación por WhatsApp."
            )
        
        # Verificar que el email no esté ya registrado
        usuario_email_existente = await buscar_usuario_por_email(db, datos_registro.email)
        if usuario_email_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este email ya está registrado"
            )
        
        # Verificar que el teléfono no esté ya registrado
        usuario_telefono_existente = await buscar_usuario_por_telefono(db, numero_limpio)
        if usuario_telefono_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este número de teléfono ya está registrado"
            )
        
        # Preparar datos para crear el usuario
        datos_usuario = {
            'email': datos_registro.email,
            'nombres': datos_registro.nombres,
            'apellido_paterno': datos_registro.apellido_paterno,
            'apellido_materno': datos_registro.apellido_materno,
            'num_celular': numero_limpio,
            'fecha_nacimiento': datos_registro.fecha_nacimiento,
            'password': hashear_password(datos_registro.password),
            'celular_verificado': True,  # Marcar como verificado (este campo SÍ existe)
            'tipo_usuario': 'arrendatario'  # Siempre inicia como arrendatario
        }
        
        # Crear el usuario
        nuevo_usuario = await crear_usuario(db, datos_usuario)
        
        # Crear token de acceso
        token = crear_token({
            "sub": numero_limpio,
            "id": nuevo_usuario.id_usuario,
            "rol": nuevo_usuario.tipo_usuario
        })
        
        # Enviar mensaje de bienvenida por WhatsApp
        try:
            await whatsapp_service.send_welcome_message(numero_limpio, datos_registro.nombres)
        except Exception as e:
            logger.warning(f"Error al enviar mensaje de bienvenida: {e}")
            # No fallar el registro si no se puede enviar el mensaje de bienvenida
        
        # Limpiar la verificación completada
        whatsapp_service.remove_verified_phone(numero_limpio)
        
        logger.info(f"Usuario registrado exitosamente: {nuevo_usuario.id_usuario}")
        
        return {
            "mensaje": "Usuario registrado exitosamente",
            "usuario": {
                "id": nuevo_usuario.id_usuario,
                "nombres": nuevo_usuario.nombres,
                "apellido_paterno": nuevo_usuario.apellido_paterno,
                "apellido_materno": nuevo_usuario.apellido_materno,
                "email": nuevo_usuario.email,
                "num_celular": nuevo_usuario.num_celular,
                "tipo_usuario": nuevo_usuario.tipo_usuario,
                "celular_verificado": nuevo_usuario.celular_verificado  # Usar el campo que SÍ existe
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
        logger.error(f"Error inesperado en el registro: {str(e)}")
        logger.error(f"Traceback completo: {e.__class__.__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "mensaje": "Error interno del servidor",
                "error_type": e.__class__.__name__,
                "error_details": str(e)
            }
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
