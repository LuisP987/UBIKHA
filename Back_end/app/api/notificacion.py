from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from db.database import obtener_sesion
from models.notificacion import Notificacion
from models.usuario import Usuario
from schemas.notificacion import NotificacionOut, NotificacionUpdate
from utils.security.jwt import obtener_usuario_actual

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])

# GET /notificaciones/ - Ver notificaciones del usuario
@router.get("/", response_model=List[NotificacionOut])
async def ver_notificaciones(
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    result = await db.execute(
        select(Notificacion)
        .where(Notificacion.id_usuario == usuario_actual.id_usuario)
        .order_by(Notificacion.fecha_notificacion.desc())
    )
    notificaciones = result.scalars().all()
    
    return notificaciones

# PUT /notificaciones/{id} - Marcar como leída
@router.put("/{id_notificacion}", response_model=NotificacionOut)
async def marcar_como_leida(
    id_notificacion: int,
    notificacion_data: NotificacionUpdate,
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    # Verificar que la notificación existe y pertenece al usuario
    result = await db.execute(
        select(Notificacion).where(
            Notificacion.id_notificacion == id_notificacion,
            Notificacion.id_usuario == usuario_actual.id_usuario
        )
    )
    notificacion = result.scalar_one_or_none()
    
    if not notificacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada"
        )
    
    notificacion.estado_notificacion = notificacion_data.estado_notificacion.value
    await db.commit()
    await db.refresh(notificacion)
    
    return notificacion

# GET /notificaciones/no-leidas - Contar notificaciones no leídas
@router.get("/no-leidas/count")
async def contar_no_leidas(
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    result = await db.execute(
        select(Notificacion)
        .where(
            Notificacion.id_usuario == usuario_actual.id_usuario,
            Notificacion.estado_notificacion == "no_leida"
        )
    )
    count = len(result.scalars().all())
    
    return {"count": count}
