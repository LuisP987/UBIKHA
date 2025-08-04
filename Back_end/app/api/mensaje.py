from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.mensaje import Mensaje
from db.database import obtener_sesion
from typing import List
from schemas.mensaje import MensajeCreate, MensajeOut

router = APIRouter(prefix="/mensajes", tags=["mensajes"])

# GET: Listar conversaciones del usuario
@router.get("/", response_model=List[MensajeOut])
async def listar_conversaciones(id_usuario: int = Query(...), db: AsyncSession = Depends(obtener_sesion)):
    stmt = select(Mensaje).where(
        (Mensaje.id_remitente == id_usuario) | (Mensaje.id_destinatario == id_usuario)
    ).order_by(Mensaje.fecha_envio.desc())
    result = await db.execute(stmt)
    mensajes = result.scalars().all()
    return mensajes

# GET: Obtener mensajes entre dos usuarios
@router.get("/{otro_usuario}", response_model=List[MensajeOut])
async def obtener_mensajes(
    otro_usuario: int,
    id_usuario: int = Query(...),
    db: AsyncSession = Depends(obtener_sesion)
):
    stmt = select(Mensaje).where(
        ((Mensaje.id_remitente == id_usuario) & (Mensaje.id_destinatario == otro_usuario)) |
        ((Mensaje.id_remitente == otro_usuario) & (Mensaje.id_destinatario == id_usuario))
    ).order_by(Mensaje.fecha_envio)
    result = await db.execute(stmt)
    mensajes = result.scalars().all()
    return mensajes

# POST: Enviar nuevo mensaje
@router.post("/", response_model=MensajeOut)
async def enviar_mensaje(mensaje_data: MensajeCreate, db: AsyncSession = Depends(obtener_sesion)):
    nuevo_mensaje = Mensaje(**mensaje_data.dict())
    db.add(nuevo_mensaje)
    await db.commit()
    await db.refresh(nuevo_mensaje)
    return nuevo_mensaje

# PUT: Marcar como leído
@router.put("/{id}/estado", response_model=dict)
async def marcar_leido(id: int, estado: str = Query(...), db: AsyncSession = Depends(obtener_sesion)):
    mensaje = await db.get(Mensaje, id)
    if not mensaje:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    mensaje.estado_mensaje = estado
    await db.commit()
    return {"message": f"Estado del mensaje cambiado a '{estado}'"}
