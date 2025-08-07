from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime, date

class LoginUsuario(BaseModel):
    num_celular: str = Field(..., description="Número de celular para el login")
    password: str

class UsuarioCrear(BaseModel):
    nombres: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    num_celular: str = Field(..., pattern=r"^9\d{8}$", description="Número de celular peruano (9 dígitos, empieza con 9)")
    fecha_nacimiento: Optional[date] = None
    email: EmailStr
    password: str  # Esto luego lo puedes hashear

class UsuarioMostrar(BaseModel):
    id_usuario: int
    nombres: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    email: EmailStr
    num_celular: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    tipo_usuario: str
    activo: bool
    celular_verificado: bool
    fecha_registro: Optional[datetime] = None

    class Config:
        from_attributes = True

class UsuarioPerfilCompleto(BaseModel):
    """Esquema completo para mostrar el perfil del usuario con toda la información disponible"""
    id_usuario: int
    nombres: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    email: EmailStr
    num_celular: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    tipo_usuario: str
    activo: bool
    celular_verificado: bool
    fecha_registro: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    
    class Config:
        from_attributes = True 
        
class RegistroUsuario(BaseModel):
    email: EmailStr
    nombres: str = Field(..., min_length=2, max_length=100, description="Nombres del usuario")
    apellido_paterno: str = Field(..., min_length=2, max_length=50, description="Apellido paterno")
    apellido_materno: Optional[str] = Field(None, max_length=50, description="Apellido materno (opcional)")
    num_celular: str = Field(..., pattern=r"^9\d{8}$", description="Número de celular peruano (9 dígitos, empieza con 9)")
    fecha_nacimiento: Optional[date] = Field(None, description="Fecha de nacimiento (solo fecha, sin hora)")
    password: str = Field(..., min_length=8, description="Contraseña (mínimo 8 caracteres)")
    
    @field_validator('fecha_nacimiento')
    @classmethod
    def validar_fecha_nacimiento(cls, v):
        if v is not None:
            # Verificar que la fecha no sea futura
            if v > date.today():
                raise ValueError('La fecha de nacimiento no puede ser futura')
            
            # Verificar que la persona tenga al menos 13 años
            edad_minima = date.today().replace(year=date.today().year - 13)
            if v > edad_minima:
                raise ValueError('Debes tener al menos 13 años para registrarte')
                
            # Verificar que la fecha no sea demasiado antigua (máximo 120 años)
            edad_maxima = date.today().replace(year=date.today().year - 120)
            if v < edad_maxima:
                raise ValueError('La fecha de nacimiento no es válida')
        
        return v
    
    @field_validator('num_celular')
    @classmethod
    def validar_num_celular(cls, v):
        if v is not None and v.strip():
            # Eliminar espacios y caracteres especiales
            numero_limpio = v.strip().replace(' ', '').replace('-', '')
            
            # Verificar que sea exactamente 9 dígitos y empiece con 9
            if not numero_limpio.isdigit() or len(numero_limpio) != 9 or not numero_limpio.startswith('9'):
                raise ValueError('El número de celular debe tener 9 dígitos y empezar con 9 (formato peruano)')
            
            return numero_limpio
        return v
    
    @field_validator('nombres', 'apellido_paterno', 'apellido_materno')
    @classmethod
    def validar_nombres(cls, v):
        if v is not None and v.strip():
            # Verificar que solo contenga letras, espacios y algunos caracteres especiales
            import re
            if not re.match(r"^[a-zA-ZÀ-ÿ\s'-]+$", v.strip()):
                raise ValueError('Los nombres solo pueden contener letras, espacios, apostrofes y guiones')
            return v.strip().title()  # Capitalizar primera letra de cada palabra
        return v

class UsuarioActualizar(BaseModel):
    """Esquema para actualizar datos del usuario. Todos los campos son opcionales."""
    nombres: Optional[str] = Field(None, min_length=2, max_length=100, description="Nombres del usuario")
    apellido_paterno: Optional[str] = Field(None, min_length=2, max_length=50, description="Apellido paterno")
    apellido_materno: Optional[str] = Field(None, max_length=50, description="Apellido materno")
    email: Optional[EmailStr] = Field(None, description="Nuevo email del usuario")
    fecha_nacimiento: Optional[date] = Field(None, description="Fecha de nacimiento")
    # NOTA: num_celular NO está incluido intencionalmente por seguridad
    
    @field_validator('fecha_nacimiento')
    @classmethod
    def validar_fecha_nacimiento(cls, v):
        if v is not None:
            # Verificar que la fecha no sea futura
            if v > date.today():
                raise ValueError("La fecha de nacimiento no puede ser futura")
            
            # Verificar que la persona tenga al menos 13 años
            edad_minima = date.today().replace(year=date.today().year - 13)
            if v > edad_minima:
                raise ValueError("Debes tener al menos 13 años")
            
            # Verificar que no sea muy antigua (máximo 120 años)
            edad_maxima = date.today().replace(year=date.today().year - 120)
            if v < edad_maxima:
                raise ValueError("La fecha de nacimiento no puede ser mayor a 120 años")
        
        return v
    
    @field_validator('nombres', 'apellido_paterno', 'apellido_materno')
    @classmethod
    def validar_nombres(cls, v):
        if v is not None and v.strip():
            # Solo letras, espacios, apostrofes y guiones
            import re
            if not re.match(r"^[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ\s'\-]+$", v.strip()):
                raise ValueError("Solo se permiten letras, espacios, apostrofes y guiones")
            # Capitalizar automáticamente
            return v.strip().title()
        return v

class CambiarPassword(BaseModel):
    password_actual: str
    password_nueva: str = Field(..., min_length=8, description="Nueva contraseña (mínimo 8 caracteres)")
    
    @field_validator('password_nueva')
    @classmethod
    def validar_password_nueva(cls, v):
        # Validar que la contraseña tenga al menos 8 caracteres
        if len(v) < 8:
            raise ValueError('La nueva contraseña debe tener al menos 8 caracteres')
        
        # Validar que contenga al menos una letra mayúscula
        if not any(c.isupper() for c in v):
            raise ValueError('La nueva contraseña debe contener al menos una letra mayúscula')
        
        # Validar que contenga al menos una letra minúscula
        if not any(c.islower() for c in v):
            raise ValueError('La nueva contraseña debe contener al menos una letra minúscula')
        
        # Validar que contenga al menos un número
        if not any(c.isdigit() for c in v):
            raise ValueError('La nueva contraseña debe contener al menos un número')
        
        return v

class CambiarCelular(BaseModel):
    """Esquema para cambiar número de celular con validación de contraseña"""
    nuevo_celular: str = Field(..., pattern=r"^9\d{8}$", description="Nuevo número de celular (9 dígitos, empieza con 9)")
    password: str = Field(..., description="Contraseña actual para confirmar el cambio")
    
    @field_validator('nuevo_celular')
    @classmethod
    def validar_nuevo_celular(cls, v):
        if v is not None and v.strip():
            # Eliminar espacios y caracteres especiales
            numero_limpio = v.strip().replace(' ', '').replace('-', '')
            
            # Verificar que sea exactamente 9 dígitos y empiece con 9
            if not numero_limpio.isdigit() or len(numero_limpio) != 9 or not numero_limpio.startswith('9'):
                raise ValueError('El número de celular debe tener 9 dígitos y empezar con 9 (formato peruano)')
            
            return numero_limpio
        return v

class UsuarioEstado(BaseModel):
    activo: bool