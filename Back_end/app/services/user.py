from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.usuario import Usuario
from schemas.user import UsuarioActualizar
from datetime import datetime
from typing import Optional

async def buscar_usuario_por_email(db: AsyncSession, email: str):
    resultado = await db.execute(select(Usuario).where(Usuario.email == email))
    return resultado.scalars().first()

async def crear_usuario(db: AsyncSession, datos: dict):
    nuevo = Usuario(**datos)
    db.add(nuevo)
    await db.commit()
    await db.refresh(nuevo)
    return nuevo

async def actualizar_usuario(db: AsyncSession, id_usuario: int, datos_usuario: dict) -> Optional[Usuario]:
    """
    Actualiza los datos de un usuario específico.
    Solo actualiza los campos que se proporcionan (no None).
    """
    try:
        # Verificar si el usuario existe
        stmt = select(Usuario).where(Usuario.id_usuario == id_usuario)
        result = await db.execute(stmt)
        usuario = result.scalar_one_or_none()
        
        if not usuario:
            return None
        
        # Si se intenta cambiar el email, verificar que no exista ya
        if 'email' in datos_usuario and datos_usuario['email'] != usuario.email:
            stmt_email = select(Usuario).where(
                Usuario.email == datos_usuario['email'],
                Usuario.id_usuario != id_usuario  # Excluir al usuario actual
            )
            result_email = await db.execute(stmt_email)
            email_existente = result_email.scalar_one_or_none()
            
            if email_existente:
                raise ValueError(f"El email {datos_usuario['email']} ya está siendo usado por otro usuario")
        
        # Lista de campos que se pueden actualizar (excluye num_celular por seguridad)
        campos_actualizables = [
            'nombres', 'apellido_paterno', 'apellido_materno', 
            'email', 'fecha_nacimiento'
        ]
        
        # Actualizar solo los campos permitidos que no son None
        campos_actualizados = []
        for campo, valor in datos_usuario.items():
            if campo in campos_actualizables and valor is not None:
                setattr(usuario, campo, valor)
                campos_actualizados.append(campo)
        
        if not campos_actualizados:
            raise ValueError("No se proporcionaron campos válidos para actualizar")
        
        # Actualizar fecha de modificación
        usuario.fecha_actualizacion = datetime.now()
        
        await db.commit()
        await db.refresh(usuario)
        
        print(f"Campos actualizados: {campos_actualizados}")  # Para debug
        return usuario
        
    except ValueError as e:
        # Re-lanzar errores de validación de negocio
        raise e
    except Exception as e:
        await db.rollback()
        raise Exception(f"Error al actualizar usuario: {str(e)}")