from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models import mensaje as Mensaje
from db.database import obtener_sesion
from typing import List

router = APIRouter(prefix="/mensajes", tags=["mensajes"])

# GET: Listar conversaciones del usuario
@router.get("/", response_model=List[dict])
async def listar_conversaciones(id_usuario: int, db: AsyncSession = Depends(obtener_sesion)):
    result = await db.execute(
        Mensaje.__table__.select().where((Mensaje.id_remitente == id_usuario) | (Mensaje.id_destinatario == id_usuario))
    )
    mensajes = result.fetchall()
    return [dict(row) for row in mensajes]

# GET: Obtener mensajes con otro usuario
@router.get("/{id_usuario}", response_model=List[dict])
async def obtener_mensajes(id_usuario: int, otro_usuario: int, db: AsyncSession = Depends(obtener_sesion)):
    result = await db.execute(
        Mensaje.__table__.select().where(
            ((Mensaje.id_remitente == id_usuario) & (Mensaje.id_destinatario == otro_usuario)) |
            ((Mensaje.id_remitente == otro_usuario) & (Mensaje.id_destinatario == id_usuario))
        )
    )
    mensajes = result.fetchall()
    return [dict(row) for row in mensajes]

# POST: Enviar nuevo mensaje
@router.post("/", response_model=dict)
async def enviar_mensaje(id_remitente: int, id_destinatario: int, contenido: str, db: AsyncSession = Depends(obtener_sesion)):
    mensaje = Mensaje(id_remitente=id_remitente, id_destinatario=id_destinatario, contenido=contenido)
    db.add(mensaje)
    await db.commit()
    await db.refresh(mensaje)
    return {"message": "Mensaje enviado", "id_mensaje": mensaje.id_mensaje}

# PUT: Marcar como leído
@router.put("/{id}/estado", response_model=dict)
async def marcar_leido(id: int, estado: str, db: AsyncSession = Depends(obtener_sesion)):
    mensaje = await db.get(Mensaje, id)
    if not mensaje:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    mensaje.estado_mensaje = estado
    await db.commit()
    await db.refresh(mensaje)
    return {"message": f"Estado del mensaje cambiado a {estado}"}
