# Mensajes de error estandarizados para autenticación y autorización

class AuthErrorMessages:
    # Errores de autenticación
    INVALID_CREDENTIALS = "Email o contraseña incorrectos"
    TOKEN_EXPIRED = "Token expirado. Por favor, inicia sesión nuevamente"
    TOKEN_INVALID = "Token inválido o corrupto"
    TOKEN_MISSING_INFO = "Token inválido: falta información del usuario"
    USER_NOT_FOUND = "Usuario no encontrado. El token puede estar vinculado a un usuario eliminado"
    
    # Errores de registro
    EMAIL_ALREADY_EXISTS = "El email ya está registrado"
    PHONE_ALREADY_EXISTS = "El número de celular ya está registrado. Usa un número diferente."
    
    # Errores de contraseña
    CURRENT_PASSWORD_INCORRECT = "La contraseña actual es incorrecta"
    
    # Errores generales
    USER_NOT_FOUND_GENERAL = "Usuario no encontrado"
    INTERNAL_SERVER_ERROR = "Error interno del servidor"
    
    # Errores de verificación
    INVALID_VERIFICATION_CODE = "Código inválido o expirado"
    CODE_SEND_ERROR = "Error al enviar el código"
    
    @staticmethod
    def get_token_error_response(error_type: str) -> dict:
        """
        Retorna el mensaje de error apropiado basado en el tipo de error JWT
        """
        messages = {
            "token_expired": AuthErrorMessages.TOKEN_EXPIRED,
            "token_invalid": AuthErrorMessages.TOKEN_INVALID,
            "user_not_found": AuthErrorMessages.USER_NOT_FOUND,
            "missing_info": AuthErrorMessages.TOKEN_MISSING_INFO
        }
        return {
            "detail": messages.get(error_type, AuthErrorMessages.TOKEN_INVALID),
            "error_type": error_type,
            "requires_login": error_type in ["token_expired", "token_invalid"]
        }
