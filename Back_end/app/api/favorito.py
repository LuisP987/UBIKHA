from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models import Favorito, inmueble as Inmueble
from db.database import obtener_sesion
from typing import List

router = APIRouter(prefix="/favoritos", tags=["favoritos"])

# POST: Agregar inmueble a favoritos
@router.post("/", response_model=dict)
async def agregar_favorito(id_usuario: int, id_inmueble: int, db: AsyncSession = Depends(obtener_sesion)):
    favorito = Favorito(id_usuario=id_usuario, id_inmueble=id_inmueble)
    db.add(favorito)
    try:
        await db.commit()
        await db.refresh(favorito)
        return {"message": "Inmueble agregado a favoritos"}
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo agregar a favoritos")

# DELETE: Eliminar de favoritos
@router.delete("/{id_inmueble}", response_model=dict)
async def eliminar_favorito(id_inmueble: int, id_usuario: int, db: AsyncSession = Depends(obtener_sesion)):
    favorito = await db.get(Favorito, {"id_inmueble": id_inmueble, "id_usuario": id_usuario})
    if not favorito:
        raise HTTPException(status_code=404, detail="Favorito no encontrado")
    await db.delete(favorito)
    await db.commit()
    return {"message": "Favorito eliminado"}

# GET: Listar favoritos del usuario
@router.get("/", response_model=List[int])
async def listar_favoritos(id_usuario: int, db: AsyncSession = Depends(obtener_sesion)):
    result = await db.execute(
        Favorito.__table__.select().where(Favorito.id_usuario == id_usuario)
    )
    favoritos = result.fetchall()
    return [f["id_inmueble"] for f in favoritos]
