from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from db.database import obtener_sesion
from models.reserva import Reserva
from models.usuario import Usuario
from schemas.reserva import ReservaCreate, ReservaOut, ReservaUpdate
from utils.security.jwt import obtener_usuario_actual

router = APIRouter(prefix="/reservas", tags=["Reservas"])

# POST /reservas/ - Crear reserva
@router.post("/", response_model=ReservaOut, status_code=status.HTTP_201_CREATED)
async def crear_reserva(
    reserva_data: ReservaCreate,
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    # Crear nueva reserva
    nueva_reserva = Reserva(
        id_usuario=usuario_actual.id_usuario,
        id_inmueble=reserva_data.id_inmueble,
        monto_total=reserva_data.monto_total
    )
    
    db.add(nueva_reserva)
    await db.commit()
    await db.refresh(nueva_reserva)
    
    return nueva_reserva

# GET /reservas/ - Listar reservas del usuario
@router.get("/", response_model=List[ReservaOut])
async def listar_reservas_usuario(
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    result = await db.execute(
        select(Reserva).where(Reserva.id_usuario == usuario_actual.id_usuario)
    )
    reservas = result.scalars().all()
    return reservas

# GET /reservas/{id_reserva} - Obtener detalle de reserva
@router.get("/{id_reserva}", response_model=ReservaOut)
async def obtener_detalle_reserva(
    id_reserva: int,
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    result = await db.execute(
        select(Reserva).where(
            Reserva.id_reserva == id_reserva,
            Reserva.id_usuario == usuario_actual.id_usuario
        )
    )
    reserva = result.scalar_one_or_none()
    
    if not reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada"
        )
    
    return reserva

# PATCH /reservas/{id}/estado - Cambiar estado de reserva
@router.patch("/{id_reserva}/estado", response_model=ReservaOut)
async def cambiar_estado_reserva(
    id_reserva: int,
    estado_data: ReservaUpdate,
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    result = await db.execute(
        select(Reserva).where(
            Reserva.id_reserva == id_reserva,
            Reserva.id_usuario == usuario_actual.id_usuario
        )
    )
    reserva = result.scalar_one_or_none()
    
    if not reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada"
        )
    
    reserva.estado = estado_data.estado.value
    await db.commit()
    await db.refresh(reserva)
    
    return reserva
