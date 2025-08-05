from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.usuario import Usuario
from models.inmueble import Inmueble

class RolService:
    """Servicio para manejar los roles de usuarios"""
    
    @staticmethod
    async def actualizar_rol_a_arrendador(db: AsyncSession, usuario: Usuario) -> str:
        """
        Actualiza el rol del usuario a arrendador cuando publica su primer inmueble
        """
        if usuario.tipo_usuario == "arrendatario":
            # Verificar si ya tiene inmuebles
            result = await db.execute(
                select(Inmueble).where(Inmueble.id_propietario == usuario.id_usuario)
            )
            inmuebles_existentes = result.scalars().all()
            
            # Si no tiene inmuebles, cambiar rol
            if not inmuebles_existentes:
                usuario.tipo_usuario = "arrendador"
                await db.commit()
                return "arrendador"
        
        return usuario.tipo_usuario
    
    @staticmethod
    def obtener_roles_usuario(usuario: Usuario) -> list[str]:
        """
        Obtiene todos los roles que puede tener un usuario
        - Si solo es arrendatario: ["arrendatario"]
        - Si tiene inmuebles: ["arrendatario", "arrendador"]
        """
        roles = ["arrendatario"]  # Todos empiezan como arrendatarios
        
        if usuario.tipo_usuario == "arrendador":
            roles.append("arrendador")
        
        return roles
    
    @staticmethod
    def puede_crear_inmueble(usuario: Usuario) -> bool:
        """Verifica si el usuario puede crear inmuebles"""
        return True  # Cualquier usuario puede crear inmuebles
    
    @staticmethod
    def puede_hacer_reserva(usuario: Usuario) -> bool:
        """Verifica si el usuario puede hacer reservas"""
        return True  # Cualquier usuario puede hacer reservas
