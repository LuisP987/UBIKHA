from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from db.database import obtener_sesion
from models.reserva import Reserva
from models.usuario import Usuario
from schemas.reserva import ReservaCreate, ReservaOut, ReservaUpdate, ListaReservasResponse
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

# GET /reservas/ - Listar reservas del usuario con mensaje informativo
@router.get("/", response_model=ListaReservasResponse)
async def listar_reservas_usuario(
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Lista todas las reservas del usuario autenticado.
    Proporciona un mensaje claro cuando no hay reservas.
    """
    result = await db.execute(
        select(Reserva).where(Reserva.id_usuario == usuario_actual.id_usuario)
    )
    reservas = result.scalars().all()
    
    total_reservas = len(reservas)
    
    # Crear mensaje descriptivo basado en el estado de las reservas
    if total_reservas == 0:
        mensaje = "No tienes reservas realizadas aún. ¡Explora nuestros inmuebles y haz tu primera reserva!"
    elif total_reservas == 1:
        mensaje = "Tienes 1 reserva registrada"
    else:
        mensaje = f"Tienes {total_reservas} reservas registradas"
    
    # Agregar información sobre estados si hay reservas
    if total_reservas > 0:
        estados_count = {}
        for reserva in reservas:
            estado = reserva.estado
            estados_count[estado] = estados_count.get(estado, 0) + 1
        
        # Crear descripción detallada
        estados_info = []
        for estado, count in estados_count.items():
            if count == 1:
                estados_info.append(f"1 {estado}")
            else:
                estados_info.append(f"{count} {estado}s")
        
        if len(estados_info) > 1:
            mensaje += f" ({', '.join(estados_info[:-1])} y {estados_info[-1]})"
        else:
            mensaje += f" ({estados_info[0]})"
    
    return ListaReservasResponse(
        mensaje=mensaje,
        total_reservas=total_reservas,
        reservas=reservas
    )

# GET /reservas/simple - Listar reservas formato simple (compatibilidad)
@router.get("/simple", response_model=List[ReservaOut])
async def listar_reservas_simple(
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Lista reservas en formato simple (solo array).
    Mantenido para compatibilidad con clientes existentes.
    """
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
