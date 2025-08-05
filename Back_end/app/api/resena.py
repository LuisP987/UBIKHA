from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from db.database import obtener_sesion
from models.resena import Resena
from models.inmueble import Inmueble
from models.usuario import Usuario
from schemas.resena import ResenaCreate, ResenaOut, ResenaUpdate
from utils.security.jwt import obtener_usuario_actual

router = APIRouter(prefix="/resenas", tags=["Reseñas"])

# POST /resenas/ - Crear reseña
@router.post("/", response_model=ResenaOut, status_code=status.HTTP_201_CREATED)
async def crear_resena(
    resena_data: ResenaCreate,
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    # Verificar que el inmueble existe
    result = await db.execute(
        select(Inmueble).where(Inmueble.id_inmueble == resena_data.id_inmueble)
    )
    inmueble = result.scalar_one_or_none()
    
    if not inmueble:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inmueble no encontrado"
        )
    
    # Verificar que la calificación esté en el rango válido
    if not (1 <= resena_data.calificacion <= 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La calificación debe estar entre 1 y 5"
        )
    
    # Verificar que el usuario no haya reseñado ya este inmueble
    result = await db.execute(
        select(Resena).where(
            Resena.id_usuario == usuario_actual.id_usuario,
            Resena.id_inmueble == resena_data.id_inmueble
        )
    )
    resena_existente = result.scalar_one_or_none()
    
    if resena_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya has reseñado este inmueble"
        )
    
    # Crear nueva reseña
    nueva_resena = Resena(
        id_usuario=usuario_actual.id_usuario,
        id_inmueble=resena_data.id_inmueble,
        calificacion=resena_data.calificacion,
        comentario=resena_data.comentario
    )
    
    db.add(nueva_resena)
    await db.commit()
    await db.refresh(nueva_resena)
    
    return nueva_resena

# GET /resenas/mis-resenas - Ver reseñas hechas por usuario
@router.get("/mis-resenas", response_model=List[ResenaOut])
async def ver_mis_resenas(
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    result = await db.execute(
        select(Resena).where(Resena.id_usuario == usuario_actual.id_usuario)
    )
    resenas = result.scalars().all()
    
    return resenas

# GET /resenas/{id_inmueble} - Ver reseñas de un inmueble
@router.get("/{id_inmueble}", response_model=List[ResenaOut])
async def ver_resenas_inmueble(
    id_inmueble: int,
    db: AsyncSession = Depends(obtener_sesion)
):
    # Verificar que el inmueble existe
    result = await db.execute(
        select(Inmueble).where(Inmueble.id_inmueble == id_inmueble)
    )
    inmueble = result.scalar_one_or_none()
    
    if not inmueble:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inmueble no encontrado"
        )
    
    # Obtener reseñas visibles del inmueble
    result = await db.execute(
        select(Resena).where(
            Resena.id_inmueble == id_inmueble,
            Resena.estado_resena == "visible"
        )
    )
    resenas = result.scalars().all()
    
    return resenas
