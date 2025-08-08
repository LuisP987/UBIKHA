from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from db.database import obtener_sesion
from models.reporte import Reporte
from models.inmueble import Inmueble
from models.usuario import Usuario
from schemas.reporte import ReporteCreate, ReporteOut, ReporteUpdate
from utils.security.jwt import obtener_usuario_actual

router = APIRouter(prefix="/reportes", tags=["Reportes"])

# POST /reportes/ - Enviar reporte de anuncio
@router.post("/", response_model=ReporteOut, status_code=status.HTTP_201_CREATED)
async def enviar_reporte(
    reporte_data: ReporteCreate,
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    # Verificar que el inmueble existe
    result = await db.execute(
        select(Inmueble).where(Inmueble.id_inmueble == reporte_data.id_inmueble)
    )
    inmueble = result.scalar_one_or_none()
    
    if not inmueble:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inmueble no encontrado"
        )
    
    # Verificar que el usuario no esté reportando su propio inmueble
    if inmueble.id_propietario == usuario_actual.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes reportar tu propio inmueble"
        )
    
    # Verificar que el usuario no haya reportado ya este inmueble
    result = await db.execute(
        select(Reporte).where(
            Reporte.id_usuario == usuario_actual.id_usuario,
            Reporte.id_inmueble == reporte_data.id_inmueble
        )
    )
    reporte_existente = result.scalar_one_or_none()
    
    if reporte_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya has reportado este inmueble"
        )
    
    # Crear nuevo reporte
    nuevo_reporte = Reporte(
        id_usuario=usuario_actual.id_usuario,
        id_inmueble=reporte_data.id_inmueble,
        tipo_reporte=reporte_data.tipo_reporte,
        descripcion=reporte_data.descripcion
    )
    
    db.add(nuevo_reporte)
    await db.commit()
    await db.refresh(nuevo_reporte)
    
    return nuevo_reporte

# GET /reportes/ - Listar reportes (admin)
@router.get("/", response_model=List[ReporteOut])
async def listar_reportes(
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    # Verificar que el usuario es administrador
    if usuario_actual.tipo_usuario != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden ver todos los reportes"
        )
    
    result = await db.execute(
        select(Reporte).order_by(Reporte.fecha_reporte.desc())
    )
    reportes = result.scalars().all()
    
    return reportes

# PUT /reportes/{id} - Cambiar estado del reporte
@router.put("/{id_reporte}", response_model=ReporteOut)
async def cambiar_estado_reporte(
    id_reporte: int,
    reporte_data: ReporteUpdate,
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    # Verificar que el usuario es administrador
    if usuario_actual.tipo_usuario != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden cambiar el estado de los reportes"
        )
    
    # Verificar que el reporte existe
    result = await db.execute(
        select(Reporte).where(Reporte.id_reporte == id_reporte)
    )
    reporte = result.scalar_one_or_none()
    
    if not reporte:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reporte no encontrado"
        )
    
    reporte.estado_reporte = reporte_data.estado_reporte.value
    await db.commit()
    await db.refresh(reporte)
    
    return reporte

# GET /reportes/mis-reportes - Ver reportes del usuario actual
@router.get("/mis-reportes", response_model=List[ReporteOut])
async def ver_mis_reportes(
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    result = await db.execute(
        select(Reporte).where(Reporte.id_usuario == usuario_actual.id_usuario)
        .order_by(Reporte.fecha_reporte.desc())
    )
    reportes = result.scalars().all()
    
    return reportes
