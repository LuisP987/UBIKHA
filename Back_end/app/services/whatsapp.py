import random
from typing import Dict, Optional
import requests
import httpx
from dotenv import load_dotenv
import os
import logging
from datetime import datetime, timedelta

load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        # Almacenar códigos con timestamp para expiración (5 minutos)
        self.verification_codes: Dict[str, Dict[str, any]] = {}
        
        # Configuración de la API de WhatsApp (Node.js)
        self.WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL", "http://localhost:3000")
        self.WHATSAPP_API_TOKEN = os.getenv("WHATSAPP_API_TOKEN", "ubikha_whatsapp_2024_secure_token_123")
        
        # Headers para autenticación con el microservicio WhatsApp
        self.headers = {
            "Content-Type": "application/json",
            "x-system-token": self.WHATSAPP_API_TOKEN
        }

    def generate_code(self, phone_number: str) -> str:
        """Genera un código de 6 dígitos y lo almacena con timestamp"""
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        self.verification_codes[phone_number] = {
            "code": code,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(minutes=5)
        }
        logger.info(f"Código generado para {phone_number}: {code}")
        return code

    async def send_verification_code(self, phone_number: str) -> bool:
        """
        Envía código de verificación a través del microservicio WhatsApp (Node.js)
        
        Args:
            phone_number: Número de teléfono en formato internacional (ej: 51987654321)
        
        Returns:
            bool: True si se envió exitosamente, False en caso contrario
        """
        try:
            # Generar código
            code = self.generate_code(phone_number)
            
            # Formatear número de teléfono (asegurar formato correcto)
            formatted_phone = self._format_phone_number(phone_number)
            
            # Mensaje del código de verificación
            mensaje = f"""🔐 UBIKHA - Código de Verificación

Tu código de verificación es: *{code}*

⚠️ Por seguridad:
• No compartas este código con nadie
• Válido por 5 minutos únicamente

¡Gracias por usar UBIKHA! 🚀"""
            
            # Payload para el microservicio WhatsApp
            payload = {
                "phone": formatted_phone,
                "message": mensaje
            }
            
            # Realizar petición HTTP al microservicio WhatsApp
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.WHATSAPP_API_URL}/api/whatsapp/send-message",
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success", False):
                        logger.info(f"Código enviado exitosamente a {formatted_phone}")
                        return True
                    else:
                        logger.error(f"Error en respuesta: {result}")
                        return False
                else:
                    logger.error(f"Error al enviar código: {response.status_code} - {response.text}")
                    return False
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout al enviar código a {phone_number}")
            return False
        except httpx.RequestError as e:
            logger.error(f"Error de conexión al enviar código: {e}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado al enviar código: {e}")
            return False

    async def verify_code(self, phone_number: str, code: str) -> bool:
        """
        Verifica si el código proporcionado es válido y no ha expirado
        
        Args:
            phone_number: Número de teléfono
            code: Código a verificar
            
        Returns:
            bool: True si el código es válido, False en caso contrario
        """
        try:
            stored_data = self.verification_codes.get(phone_number)
            
            if not stored_data:
                logger.warning(f"No se encontró código para {phone_number}")
                return False
            
            # Verificar si el código ha expirado
            if datetime.now() > stored_data["expires_at"]:
                logger.warning(f"Código expirado para {phone_number}")
                del self.verification_codes[phone_number]
                return False
            
            # Verificar si el código es correcto
            if stored_data["code"] == code:
                logger.info(f"Código verificado exitosamente para {phone_number}")
                # Marcar como verificado en lugar de eliminar
                self.verification_codes[phone_number]["verified"] = True
                self.verification_codes[phone_number]["verified_at"] = datetime.now()
                return True
            else:
                logger.warning(f"Código incorrecto para {phone_number}")
                return False
                
        except Exception as e:
            logger.error(f"Error al verificar código: {e}")
            return False

    async def check_whatsapp_service_status(self) -> bool:
        """
        Verifica el estado del microservicio WhatsApp
        
        Returns:
            bool: True si el servicio está disponible y WhatsApp conectado, False en caso contrario
        """
        try:
            # Verificar el estado de WhatsApp Web directamente
            async with httpx.AsyncClient(timeout=10.0) as client:
                status_response = await client.get(f"{self.WHATSAPP_API_URL}/api/whatsapp/status")
                
                if status_response.status_code == 200:
                    data = status_response.json()
                    is_connected = data.get("connected", False)
                    is_authenticated = data.get("authenticated", False)
                    
                    logger.info(f"WhatsApp status - Connected: {is_connected}, Authenticated: {is_authenticated}")
                    return is_connected and is_authenticated
                else:
                    logger.error(f"Error al verificar estado de WhatsApp: {status_response.status_code}")
                    return False
                    
        except httpx.TimeoutException:
            logger.error("Timeout al verificar estado de WhatsApp")
            return False
        except Exception as e:
            logger.error(f"Error al verificar estado del servicio WhatsApp: {e}")
            return False

    def _format_phone_number(self, phone_number: str) -> str:
        """
        Formatea el número de teléfono peruano al formato internacional
        
        Args:
            phone_number: Número de teléfono peruano (9 dígitos)
            
        Returns:
            str: Número en formato internacional (51XXXXXXXXX)
        """
        # Remover caracteres no numéricos
        clean_number = ''.join(filter(str.isdigit, phone_number))
        
        # Si ya tiene 11 dígitos y empieza con 51, devolver tal como está
        if len(clean_number) == 11 and clean_number.startswith('51'):
            return clean_number
        
        # Si tiene 9 dígitos y empieza con 9, agregar código de país peruano
        if len(clean_number) == 9 and clean_number.startswith('9'):
            return f"51{clean_number}"
        
        # Si tiene formato diferente, intentar extraer los últimos 9 dígitos
        if len(clean_number) > 9:
            last_nine = clean_number[-9:]
            if last_nine.startswith('9'):
                return f"51{last_nine}"
        
        # Fallback: devolver el número limpio
        logger.warning(f"Formato de número no estándar: {phone_number}")
        return clean_number

    def get_pending_verifications_count(self) -> int:
        """
        Obtiene el número de verificaciones pendientes
        
        Returns:
            int: Número de verificaciones pendientes
        """
        return len(self.verification_codes)

    def clean_expired_codes(self) -> int:
        """
        Limpia códigos expirados del almacén
        
        Returns:
            int: Número de códigos eliminados
        """
        current_time = datetime.now()
        expired_phones = [
            phone for phone, data in self.verification_codes.items()
            if current_time > data["expires_at"]
        ]
        
        for phone in expired_phones:
            del self.verification_codes[phone]
            
        logger.info(f"Códigos expirados eliminados: {len(expired_phones)}")
        return len(expired_phones)

    async def send_welcome_message(self, phone_number: str, nombre: str) -> bool:
        """
        Envía mensaje de bienvenida después del registro exitoso
        
        Args:
            phone_number: Número de teléfono
            nombre: Nombre del usuario
            
        Returns:
            bool: True si se envió exitosamente, False en caso contrario
        """
        try:
            formatted_phone = self._format_phone_number(phone_number)
            
            mensaje_bienvenida = f"""🎉 ¡Bienvenido/a a UBIKHA, {nombre}!

Tu cuenta ha sido creada exitosamente.

Con UBIKHA puedes:
✅ Buscar y alquilar inmuebles
✅ Gestionar tus reservas
✅ Contactar propietarios fácilmente
✅ Dejar reseñas y valoraciones

¡Gracias por confiar en nosotros! 🏠✨"""
            
            payload = {
                "phone": formatted_phone,
                "message": mensaje_bienvenida
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.WHATSAPP_API_URL}/api/whatsapp/send-message",
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success", False):
                        logger.info(f"Mensaje de bienvenida enviado a {formatted_phone}")
                        return True
                    else:
                        logger.error(f"Error en respuesta de bienvenida: {result}")
                        return False
                else:
                    logger.error(f"Error al enviar mensaje de bienvenida: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error al enviar mensaje de bienvenida: {e}")
            return False

    def is_phone_verified(self, phone_number: str) -> bool:
        """
        Verifica si un número de teléfono ha sido verificado recientemente
        
        Args:
            phone_number: Número de teléfono a verificar
            
        Returns:
            bool: True si el teléfono fue verificado recientemente
        """
        # Verificar si existe en los códigos verificados
        if phone_number in self.verification_codes:
            verification_data = self.verification_codes[phone_number]
            # Verificar si el código fue verificado y no ha expirado
            if verification_data.get("verified", False):
                # Considerar verificado si fue validado en los últimos 10 minutos
                verified_at = verification_data.get("verified_at")
                if verified_at and datetime.now() - verified_at < timedelta(minutes=10):
                    return True
        return False

    def remove_verified_phone(self, phone_number: str) -> bool:
        """
        Remueve un teléfono verificado del cache después del registro exitoso
        
        Args:
            phone_number: Número de teléfono a remover
            
        Returns:
            bool: True si se removió exitosamente
        """
        try:
            if phone_number in self.verification_codes:
                del self.verification_codes[phone_number]
                logger.info(f"Teléfono {phone_number} removido del cache de verificación")
                return True
            return False
        except Exception as e:
            logger.error(f"Error al remover teléfono verificado: {e}")
            return False
