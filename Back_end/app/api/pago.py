from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from db.database import obtener_sesion
from models.reserva import Pago, Reserva
from models.usuario import Usuario
from schemas.reserva import PagoCreate, PagoOut, PagoUpdate
from utils.security.jwt import obtener_usuario_actual

router = APIRouter(prefix="/pagos", tags=["Pagos"])

# POST /pagos/ - Registrar nuevo pago
@router.post("/", response_model=PagoOut, status_code=status.HTTP_201_CREATED)
async def registrar_pago(
    id_reserva: int,
    pago_data: PagoCreate,
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    # Verificar que la reserva existe y pertenece al usuario
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
    
    # Crear nuevo pago
    nuevo_pago = Pago(
        id_reserva=id_reserva,
        monto=pago_data.monto,
        metodo_pago=pago_data.metodo_pago
    )
    
    db.add(nuevo_pago)
    await db.commit()
    await db.refresh(nuevo_pago)
    
    return nuevo_pago

# GET /pagos/{id_reserva} - Listar pagos de una reserva
@router.get("/{id_reserva}", response_model=List[PagoOut])
async def listar_pagos_reserva(
    id_reserva: int,
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    # Verificar que la reserva pertenece al usuario
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
    
    # Obtener pagos de la reserva
    result = await db.execute(
        select(Pago).where(Pago.id_reserva == id_reserva)
    )
    pagos = result.scalars().all()
    
    return pagos

# PUT /pagos/{id_pago} - Actualizar estado del pago
@router.put("/{id_pago}", response_model=PagoOut)
async def actualizar_estado_pago(
    id_pago: int,
    pago_data: PagoUpdate,
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    # Obtener el pago y verificar que pertenece al usuario
    result = await db.execute(
        select(Pago)
        .join(Reserva, Pago.id_reserva == Reserva.id_reserva)
        .where(
            Pago.id_pago == id_pago,
            Reserva.id_usuario == usuario_actual.id_usuario
        )
    )
    pago = result.scalar_one_or_none()
    
    if not pago:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pago no encontrado"
        )
    
    pago.estado_pago = pago_data.estado_pago.value
    await db.commit()
    await db.refresh(pago)
    
    return pago
