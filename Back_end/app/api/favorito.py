from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Favorito
from db.database import obtener_sesion
from typing import List
from schemas.favorito import FavoritoCreate, FavoritoOut

router = APIRouter(prefix="/favoritos", tags=["favoritos"])

# POST: Agregar inmueble a favoritos
@router.post("/", response_model=dict)
async def agregar_favorito(
    favorito_data: FavoritoCreate,
    db: AsyncSession = Depends(obtener_sesion)
):
    # Evitar duplicados
    stmt = select(Favorito).where(
        (Favorito.id_usuario == favorito_data.id_usuario) &
        (Favorito.id_inmueble == favorito_data.id_inmueble)
    )
    result = await db.execute(stmt)
    existente = result.scalar_one_or_none()
    if existente:
        raise HTTPException(status_code=400, detail="El inmueble ya está en favoritos")

    nuevo_favorito = Favorito(**favorito_data.dict())
    db.add(nuevo_favorito)
    try:
        await db.commit()
        await db.refresh(nuevo_favorito)
        return {"message": "Inmueble agregado a favoritos"}
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo agregar a favoritos")

# DELETE: Eliminar inmueble de favoritos
@router.delete("/", response_model=dict)
async def eliminar_favorito(
    id_usuario: int = Query(...),
    id_inmueble: int = Query(...),
    db: AsyncSession = Depends(obtener_sesion)
):
    stmt = select(Favorito).where(
        (Favorito.id_usuario == id_usuario) &
        (Favorito.id_inmueble == id_inmueble)
    )
    result = await db.execute(stmt)
    favorito = result.scalar_one_or_none()
    if not favorito:
        raise HTTPException(status_code=404, detail="Favorito no encontrado")
    await db.delete(favorito)
    await db.commit()
    return {"message": "Favorito eliminado"}

# GET: Listar ID de inmuebles favoritos del usuario
@router.get("/", response_model=List[int])
async def listar_favoritos(id_usuario: int, db: AsyncSession = Depends(obtener_sesion)):
    stmt = select(Favorito).where(Favorito.id_usuario == id_usuario)
    result = await db.execute(stmt)
    favoritos = result.scalars().all()
    return [f.id_inmueble for f in favoritos]
