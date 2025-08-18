from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from sqlalchemy.orm import joinedload
from typing import List
from datetime import datetime
from db.database import obtener_sesion
from models.reporte import Reporte
from models.inmueble import Inmueble
from models.usuario import Usuario
from schemas.reporte import (
    ReporteCreate, ReporteCreateCompleto, ReporteCreateResponse,
    ReporteOut, ReporteUpdate, TipoReporteEnum
)
from utils.security.jwt import obtener_usuario_actual

router = APIRouter(prefix="/reportes", tags=["Reportes"])

# GET /reportes/tipos - Obtener tipos de reporte disponibles
@router.get("/tipos")
async def obtener_tipos_reporte():
    """
    Obtener la lista de tipos de reporte disponibles
    """
    return {
        "tipos_reporte": [
            {
                "valor": tipo.value,
                "codigo": tipo.name,
                "descripcion": _get_descripcion_tipo(tipo)
            }
            for tipo in TipoReporteEnum
        ]
    }

def _get_descripcion_tipo(tipo: TipoReporteEnum) -> str:
    """Obtener descripciones más detalladas para cada tipo"""
    descripciones = {
        TipoReporteEnum.incorrecto_impreciso: "La información del inmueble no es correcta o es engañosa",
        TipoReporteEnum.no_alojamiento_real: "El anuncio no representa un alojamiento real o existente", 
        TipoReporteEnum.estafa: "Sospecha de actividad fraudulenta o estafa",
        TipoReporteEnum.ofensivo: "Contenido ofensivo, discriminatorio o inapropiado",
        TipoReporteEnum.otra_cosa: "Otro motivo no especificado en las categorías anteriores"
    }
    return descripciones.get(tipo, tipo.value)

# POST /reportes/ - Enviar reporte completo (nuevo flujo)
@router.post("/", response_model=ReporteCreateResponse, status_code=status.HTTP_201_CREATED)
async def enviar_reporte_completo(
    reporte_data: ReporteCreateCompleto,
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Enviar un reporte completo de inmueble.
    
    Flujo del modal:
    1. Usuario selecciona tipo de reporte
    2. Usuario escribe comentario detallado
    3. Se envía el reporte para revisión administrativa
    """
    try:
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
                detail="Ya has reportado este inmueble anteriormente"
            )
        
        # Crear el nuevo reporte
        nuevo_reporte = Reporte(
            id_usuario=usuario_actual.id_usuario,
            id_inmueble=reporte_data.id_inmueble,
            tipo_reporte=reporte_data.tipo_reporte.value,
            descripcion=reporte_data.comentario,
            estado_reporte="pendiente"
        )
        
        db.add(nuevo_reporte)
        await db.commit()
        await db.refresh(nuevo_reporte)
        
        return ReporteCreateResponse(
            mensaje="Reporte enviado exitosamente. Será revisado por nuestro equipo administrativo.",
            id_reporte=nuevo_reporte.id_reporte,
            tipo_reporte=nuevo_reporte.tipo_reporte,
            estado=nuevo_reporte.estado_reporte,
            fecha_reporte=nuevo_reporte.fecha_reporte
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

# POST /reportes/legacy - Enviar reporte (endpoint legacy para compatibilidad)
@router.post("/legacy", response_model=ReporteOut, status_code=status.HTTP_201_CREATED)
async def enviar_reporte_legacy(
    reporte_data: ReporteCreate,
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Endpoint legacy para compatibilidad con versión anterior
    """
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
    
    # Actualizar estado y agregar comentario de admin si se proporciona
    reporte.estado_reporte = reporte_data.estado_reporte.value
    if reporte_data.comentario_admin:
        reporte.comentario_admin = reporte_data.comentario_admin
    reporte.fecha_revision = datetime.now()
    
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

# ==================== ENDPOINTS PARA ADMINISTRADORES ====================

# GET /reportes/admin/pendientes - Ver reportes pendientes (solo admin)
@router.get("/admin/pendientes", response_model=List[ReporteOut])
async def ver_reportes_pendientes_admin(
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Ver todos los reportes pendientes de revisión.
    Solo accesible para administradores.
    """
    # Verificar que el usuario sea administrador
    if usuario_actual.tipo_usuario != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información"
        )
    
    # Obtener reportes pendientes con información del inmueble y usuario
    result = await db.execute(
        select(Reporte)
        .options(joinedload(Reporte.inmueble), joinedload(Reporte.usuario))
        .where(Reporte.estado_reporte == "pendiente")
        .order_by(Reporte.fecha_reporte.desc())
    )
    reportes = result.unique().scalars().all()
    
    # Construir respuesta con información adicional
    reportes_detallados = []
    for reporte in reportes:
        reporte_data = {
            "id_reporte": reporte.id_reporte,
            "id_usuario": reporte.id_usuario,
            "id_inmueble": reporte.id_inmueble,
            "tipo_reporte": reporte.tipo_reporte,
            "descripcion": reporte.descripcion,
            "fecha_reporte": reporte.fecha_reporte,
            "estado_reporte": reporte.estado_reporte,
            "titulo_inmueble": reporte.inmueble.titulo if reporte.inmueble else None,
            "propietario_inmueble": f"{reporte.inmueble.propietario.nombres} {reporte.inmueble.propietario.apellido_paterno}" if reporte.inmueble and reporte.inmueble.propietario else None
        }
        reportes_detallados.append(reporte_data)
    
    return reportes_detallados

# GET /reportes/admin/todos - Ver todos los reportes (solo admin)
@router.get("/admin/todos", response_model=List[ReporteOut])
async def ver_todos_reportes_admin(
    estado: str = None,
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Ver todos los reportes, opcionalmente filtrados por estado.
    Solo accesible para administradores.
    """
    # Verificar que el usuario sea administrador
    if usuario_actual.tipo_usuario != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información"
        )
    
    # Construir query con filtro opcional
    query = select(Reporte).options(joinedload(Reporte.inmueble), joinedload(Reporte.usuario))
    
    if estado:
        query = query.where(Reporte.estado_reporte == estado)
    
    query = query.order_by(Reporte.fecha_reporte.desc())
    
    result = await db.execute(query)
    reportes = result.unique().scalars().all()
    
    # Construir respuesta con información adicional
    reportes_detallados = []
    for reporte in reportes:
        reporte_data = {
            "id_reporte": reporte.id_reporte,
            "id_usuario": reporte.id_usuario,
            "id_inmueble": reporte.id_inmueble,
            "tipo_reporte": reporte.tipo_reporte,
            "descripcion": reporte.descripcion,
            "fecha_reporte": reporte.fecha_reporte,
            "estado_reporte": reporte.estado_reporte,
            "titulo_inmueble": reporte.inmueble.titulo if reporte.inmueble else None,
            "propietario_inmueble": f"{reporte.inmueble.propietario.nombres} {reporte.inmueble.propietario.apellido_paterno}" if reporte.inmueble and reporte.inmueble.propietario else None
        }
        reportes_detallados.append(reporte_data)
    
    return reportes_detallados

# PUT /reportes/admin/{id_reporte}/resolver - Resolver reporte (solo admin)
@router.put("/admin/{id_reporte}/resolver")
async def resolver_reporte_admin(
    id_reporte: int,
    reporte_update: ReporteUpdate,
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Resolver un reporte marcándolo como resuelto, rechazado, etc.
    Solo accesible para administradores.
    """
    # Verificar que el usuario sea administrador
    if usuario_actual.tipo_usuario != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción"
        )
    
    # Buscar el reporte
    result = await db.execute(
        select(Reporte).where(Reporte.id_reporte == id_reporte)
    )
    reporte = result.scalar_one_or_none()
    
    if not reporte:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reporte no encontrado"
        )
    
    # Actualizar el reporte
    reporte.estado_reporte = reporte_update.estado_reporte.value
    if reporte_update.comentario_admin:
        reporte.comentario_admin = reporte_update.comentario_admin
    reporte.fecha_revision = datetime.now()
    
    await db.commit()
    await db.refresh(reporte)
    
    return {
        "mensaje": f"Reporte {reporte_update.estado_reporte.value} exitosamente",
        "id_reporte": reporte.id_reporte,
        "nuevo_estado": reporte.estado_reporte,
        "fecha_revision": reporte.fecha_revision
    }

# GET /reportes/estadisticas - Estadísticas de reportes (solo admin)
@router.get("/admin/estadisticas")
async def obtener_estadisticas_reportes(
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Obtener estadísticas de reportes para el panel administrativo.
    """
    # Verificar que el usuario sea administrador
    if usuario_actual.tipo_usuario != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información"
        )
    
    # Contar reportes por estado
    from sqlalchemy import func
    
    result = await db.execute(
        select(Reporte.estado_reporte, func.count(Reporte.id_reporte))
        .group_by(Reporte.estado_reporte)
    )
    conteos_estado = dict(result.fetchall())
    
    # Contar reportes por tipo
    result = await db.execute(
        select(Reporte.tipo_reporte, func.count(Reporte.id_reporte))
        .group_by(Reporte.tipo_reporte)
    )
    conteos_tipo = dict(result.fetchall())
    
    # Total de reportes
    result = await db.execute(select(func.count(Reporte.id_reporte)))
    total_reportes = result.scalar()
    
    return {
        "total_reportes": total_reportes,
        "reportes_por_estado": conteos_estado,
        "reportes_por_tipo": conteos_tipo,
        "reportes_pendientes": conteos_estado.get("pendiente", 0),
        "reportes_resueltos": conteos_estado.get("resuelto", 0)
    }
