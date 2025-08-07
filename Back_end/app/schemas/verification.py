from pydantic import BaseModel, Field, validator
from typing import Optional

class PhoneVerification(BaseModel):
    phone_number: str = Field(
        ..., 
        description="Número de celular peruano (9 dígitos empezando con 9)",
        example="950205006",
        min_length=9,
        max_length=9
    )
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        # Remover espacios y caracteres no numéricos
        clean_number = ''.join(filter(str.isdigit, v))
        
        # Validar longitud exacta de 9 dígitos
        if len(clean_number) != 9:
            raise ValueError("El número debe tener exactamente 9 dígitos")
        
        # Validar que empiece con 9 (números móviles peruanos)
        if not clean_number.startswith('9'):
            raise ValueError("El número de celular debe empezar con 9")
        
        # Retornar solo los 9 dígitos (sin código de país)
        return clean_number

class CodeVerification(BaseModel):
    phone_number: str = Field(
        ..., 
        description="Número de celular peruano (9 dígitos empezando con 9)",
        example="950205006",
        min_length=9,
        max_length=9
    )
    code: str = Field(
        ..., 
        description="Código de verificación de 6 dígitos",
        example="123456",
        min_length=6,
        max_length=6
    )
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        # Misma validación que PhoneVerification
        clean_number = ''.join(filter(str.isdigit, v))
        
        if len(clean_number) != 9:
            raise ValueError("El número debe tener exactamente 9 dígitos")
        
        if not clean_number.startswith('9'):
            raise ValueError("El número de celular debe empezar con 9")
        
        return clean_number
    
    @validator('code')
    def validate_code(cls, v):
        if not v.isdigit():
            raise ValueError("El código debe contener solo números")
        if len(v) != 6:
            raise ValueError("El código debe tener exactamente 6 dígitos")
        return v

class WhatsAppServiceStatus(BaseModel):
    """Respuesta del estado del servicio WhatsApp"""
    success: bool
    data: dict
    message: Optional[str] = None

class VerificationResponse(BaseModel):
    """Respuesta estándar para verificaciones"""
    success: bool
    message: str
    verified: Optional[bool] = None
    data: Optional[dict] = None
