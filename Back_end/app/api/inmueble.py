from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models import Inmueble, CaracteristicasInmueble
from db.database import obtener_sesion
from typing import List, Optional
from schemas.inmueble import InmuebleCreate, InmuebleOut, InmuebleUpdate, EstadoInmueble
from typing import Dict, Any
from sqlalchemy.future import select  


router = APIRouter(prefix="/inmuebles", tags=["inmuebles"])

# POST: Crear nuevo inmueble
@router.post("/", response_model=Dict[str, Any])
async def crear_inmueble(datos: InmuebleCreate, db: AsyncSession = Depends(obtener_sesion)):
    inmueble = Inmueble(**datos.dict())
    db.add(inmueble)
    await db.commit()
    await db.refresh(inmueble)
    return {"message": "Inmueble creado", "id_inmueble": inmueble.id_inmueble}

# GET: Listar inmuebles filtrados
@router.get("/", response_model=List[InmuebleOut])
async def listar_inmuebles(tipo_inmueble: Optional[str] = None, db: AsyncSession = Depends(obtener_sesion)):
    stmt = select(Inmueble)
    if tipo_inmueble:
        stmt = stmt.where(Inmueble.tipo_inmueble == tipo_inmueble)
    result = await db.execute(stmt)
    inmuebles = result.scalars().all()
    return inmuebles

# GET: Ver detalle de inmueble
@router.get("/{id_inmueble}", response_model=InmuebleOut)
async def detalle_inmueble(id_inmueble: int, db: AsyncSession = Depends(obtener_sesion)):
    inmueble = await db.get(Inmueble, id_inmueble)
    if not inmueble:
        raise HTTPException(status_code=404, detail="Inmueble no encontrado")
    return inmueble

# PUT: Editar inmueble
@router.put("/{id_inmueble}", response_model=Dict)
async def editar_inmueble(id_inmueble: int, datos: InmuebleUpdate, db: AsyncSession = Depends(obtener_sesion)):
    inmueble = await db.get(Inmueble, id_inmueble)
    if not inmueble:
        raise HTTPException(status_code=404, detail="Inmueble no encontrado")
    for key, value in datos.dict(exclude_unset=True).items():
        setattr(inmueble, key, value)
    await db.commit()
    await db.refresh(inmueble)
    return {"message": "Inmueble actualizado"}


# DELETE: Eliminar inmueble
@router.delete("/{id_inmueble}", response_model=Dict)
async def eliminar_inmueble(id_inmueble: int, db: AsyncSession = Depends(obtener_sesion)):
    inmueble = await db.get(Inmueble, id_inmueble)
    if not inmueble:
        raise HTTPException(status_code=404, detail="Inmueble no encontrado")
    await db.delete(inmueble)
    await db.commit()
    return {"message": "Inmueble eliminado"}

# PATCH: Cambiar estado del inmueble
@router.patch("/{id_inmueble}/estado")
async def cambiar_estado_inmueble(id_inmueble: int, datos: EstadoInmueble, db: AsyncSession = Depends(obtener_sesion)):
    inmueble = await db.get(Inmueble, id_inmueble)
    if not inmueble:
        raise HTTPException(status_code=404, detail="Inmueble no encontrado")
    inmueble.estado = datos.estado
    await db.commit()
    await db.refresh(inmueble)
    return {"message": f"Estado cambiado a {datos.estado}"}