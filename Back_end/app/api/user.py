from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from db.database import obtener_sesion
from models.usuario import Usuario as User
from models.reporte import Reporte
from models.inmueble import Inmueble, CaracteristicasInmueble
from models.reserva import Reserva
from models.resena import Resena
from models.imagen_inmueble import ImagenInmueble
from models.favorito import Favorito
from models.mensaje import Mensaje
from models.notificacion import Notificacion
from schemas.user import UsuarioCrear, UsuarioMostrar
from utils.security.seguridad import hashear_password
from schemas.user import UsuarioEstado
import traceback

# Constantes
USUARIO_NO_ENCONTRADO = "Usuario no encontrado"


router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.get("/", response_model=list[UsuarioMostrar])
async def listar_usuarios(db: AsyncSession = Depends(obtener_sesion)):
    resultado = await db.execute(select(User))
    return resultado.scalars().all()

@router.get("/{email}", response_model=UsuarioMostrar)
async def obtener_usuario(email: str, db: AsyncSession = Depends(obtener_sesion)):
    resultado = await db.execute(select(User).where(User.email == email))
    usuario = resultado.scalars().first()
    if not usuario:
        raise HTTPException(status_code=404, detail=USUARIO_NO_ENCONTRADO)
    return usuario

@router.post("/", response_model=UsuarioMostrar)
async def crear_usuario(datos: UsuarioCrear, db: AsyncSession = Depends(obtener_sesion)):
    nuevo_usuario = User(
        nombres=datos.nombres,
        apellido_paterno=datos.apellido_paterno,
        apellido_materno=datos.apellido_materno,
        num_celular=datos.num_celular,
        fecha_nacimiento=datos.fecha_nacimiento,
        email=datos.email,
        password=hashear_password(datos.password),
    )
    db.add(nuevo_usuario)
    await db.commit()
    await db.refresh(nuevo_usuario)
    return nuevo_usuario

   


@router.put("/{email}/estado", response_model=UsuarioMostrar)
async def cambiar_estado_usuario(email: str, datos: UsuarioEstado, db: AsyncSession = Depends(obtener_sesion)):
    resultado = await db.execute(select(User).where(User.email == email))
    usuario = resultado.scalars().first()
    if not usuario:
        raise HTTPException(status_code=404, detail=USUARIO_NO_ENCONTRADO)
    usuario.activo = datos.activo
    await db.commit()
    await db.refresh(usuario)
    return usuario

@router.delete("/{email}", response_model=dict)
async def eliminar_usuario(email: str, db: AsyncSession = Depends(obtener_sesion)):
    """
    Eliminar usuario de forma segura, manejando las relaciones de base de datos.
    
    Este endpoint elimina en el orden correcto para evitar violaciones de llaves foráneas:
    1. Mensajes (enviados y recibidos por el usuario)
    2. Notificaciones (del usuario)
    3. Características de inmuebles (de los inmuebles del usuario)
    4. Reportes (del usuario y sobre sus inmuebles)
    5. Reservas (del usuario y de sus inmuebles)
    6. Reseñas (del usuario y sobre sus inmuebles)
    7. Imágenes de inmuebles (de los inmuebles del usuario)
    8. Favoritos (del usuario y de sus inmuebles)
    9. Inmuebles (del usuario)
    10. Usuario
    """
    try:
        # Buscar el usuario
        resultado = await db.execute(select(User).where(User.email == email))
        usuario = resultado.scalars().first()
        
        if not usuario:
            raise HTTPException(status_code=404, detail=USUARIO_NO_ENCONTRADO)
        
        user_id = usuario.id_usuario
        
        # Obtener IDs de inmuebles del usuario
        inmuebles_resultado = await db.execute(select(Inmueble.id_inmueble).where(Inmueble.id_propietario == user_id))
        inmuebles_ids = [row[0] for row in inmuebles_resultado.fetchall()]
        
        eliminados = {
            "mensajes": 0,
            "notificaciones": 0,
            "caracteristicas_inmueble": 0,
            "reportes": 0,
            "reservas": 0,
            "resenas": 0,
            "imagenes": 0,
            "favoritos": 0,
            "inmuebles": 0
        }
        
        # 1. PRIMERO: Eliminar mensajes (enviados y recibidos por el usuario)
        result = await db.execute(delete(Mensaje).where(Mensaje.id_remitente == user_id))
        eliminados["mensajes"] += result.rowcount
        
        result = await db.execute(delete(Mensaje).where(Mensaje.id_destinatario == user_id))
        eliminados["mensajes"] += result.rowcount
        
        # 2. SEGUNDO: Eliminar notificaciones del usuario
        result = await db.execute(delete(Notificacion).where(Notificacion.id_usuario == user_id))
        eliminados["notificaciones"] = result.rowcount
        
        # 3. TERCERO: Eliminar características de inmuebles
        if inmuebles_ids:
            result = await db.execute(delete(CaracteristicasInmueble).where(CaracteristicasInmueble.id_inmueble.in_(inmuebles_ids)))
            eliminados["caracteristicas_inmueble"] = result.rowcount
        
        # 4. CUARTO: Eliminar reportes (del usuario y sobre sus inmuebles)
        if inmuebles_ids:
            result = await db.execute(delete(Reporte).where(Reporte.id_inmueble.in_(inmuebles_ids)))
            eliminados["reportes"] += result.rowcount
        
        result = await db.execute(delete(Reporte).where(Reporte.id_usuario == user_id))
        eliminados["reportes"] += result.rowcount
        
        # 5. QUINTO: Eliminar reservas (del usuario y de sus inmuebles)
        if inmuebles_ids:
            result = await db.execute(delete(Reserva).where(Reserva.id_inmueble.in_(inmuebles_ids)))
            eliminados["reservas"] += result.rowcount
        
        result = await db.execute(delete(Reserva).where(Reserva.id_usuario == user_id))
        eliminados["reservas"] += result.rowcount
        
        # 6. SEXTO: Eliminar reseñas (del usuario y sobre sus inmuebles)
        if inmuebles_ids:
            result = await db.execute(delete(Resena).where(Resena.id_inmueble.in_(inmuebles_ids)))
            eliminados["resenas"] += result.rowcount
        
        result = await db.execute(delete(Resena).where(Resena.id_usuario == user_id))
        eliminados["resenas"] += result.rowcount
        
        # 7. SÉPTIMO: Eliminar imágenes de inmuebles
        if inmuebles_ids:
            result = await db.execute(delete(ImagenInmueble).where(ImagenInmueble.id_inmueble.in_(inmuebles_ids)))
            eliminados["imagenes"] = result.rowcount
        
        # 8. OCTAVO: Eliminar favoritos (del usuario y de sus inmuebles)
        if inmuebles_ids:
            result = await db.execute(delete(Favorito).where(Favorito.id_inmueble.in_(inmuebles_ids)))
            eliminados["favoritos"] += result.rowcount
        
        result = await db.execute(delete(Favorito).where(Favorito.id_usuario == user_id))
        eliminados["favoritos"] += result.rowcount
        
        # 9. NOVENO: Eliminar inmuebles del usuario
        if inmuebles_ids:
            result = await db.execute(delete(Inmueble).where(Inmueble.id_propietario == user_id))
            eliminados["inmuebles"] = result.rowcount
        
        # 10. FINALMENTE: Eliminar el usuario
        await db.delete(usuario)
        await db.commit()
        
        return {
            "mensaje": f"Usuario '{email}' eliminado correctamente",
            "usuario_eliminado": {
                "id": user_id,
                "email": email,
                "nombres": f"{usuario.nombres} {usuario.apellido_paterno}"
            },
            "registros_eliminados": eliminados,
            "total_inmuebles_del_usuario": len(inmuebles_ids) if inmuebles_ids else 0
        }
        
    except HTTPException:
        await db.rollback()
        raise  # Re-lanzar HTTPExceptions sin modificar
        
    except Exception as e:
        await db.rollback()
        # Log del error completo para debugging
        error_trace = traceback.format_exc()
        print(f"Error inesperado al eliminar usuario '{email}': {error_trace}")
        
        raise HTTPException(
            status_code=500,
            detail={
                "mensaje": "Error interno del servidor al eliminar el usuario",
                "error": str(e),
                "sugerencia": "El usuario puede tener datos relacionados que impiden su eliminación. Contacte al administrador.",
                "debug": error_trace[:500]  # Primeros 500 caracteres del traceback
            }
        )


