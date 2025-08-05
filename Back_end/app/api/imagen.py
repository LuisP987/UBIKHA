from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import os
from db.database import obtener_sesion
from models.imagen_inmueble import ImagenInmueble
from models.inmueble import Inmueble
from models.usuario import Usuario
from schemas.imagen import ImagenCreate, ImagenOut
from utils.security.jwt import obtener_usuario_actual

router = APIRouter(prefix="/imagenes", tags=["Imágenes del Inmueble"])

# POST /imagenes/ - Subir imagen de inmueble
@router.post("/", response_model=ImagenOut, status_code=status.HTTP_201_CREATED)
async def subir_imagen_inmueble(
    imagen_data: ImagenCreate,
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    # Verificar que el inmueble existe y pertenece al usuario
    result = await db.execute(
        select(Inmueble).where(
            Inmueble.id_inmueble == imagen_data.id_inmueble,
            Inmueble.id_propietario == usuario_actual.id_usuario
        )
    )
    inmueble = result.scalar_one_or_none()
    
    if not inmueble:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inmueble no encontrado o no autorizado"
        )
    
    # Crear registro en la base de datos
    nueva_imagen = ImagenInmueble(
        id_inmueble=imagen_data.id_inmueble,
        url_imagen=imagen_data.url_imagen
    )
    
    db.add(nueva_imagen)
    await db.commit()
    await db.refresh(nueva_imagen)
    
    return nueva_imagen

# DELETE /imagenes/{id_imagen} - Eliminar imagen
@router.delete("/{id_imagen}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_imagen(
    id_imagen: int,
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    # Verificar que la imagen existe y el inmueble pertenece al usuario
    result = await db.execute(
        select(ImagenInmueble)
        .join(Inmueble, ImagenInmueble.id_inmueble == Inmueble.id_inmueble)
        .where(
            ImagenInmueble.id_imagen == id_imagen,
            Inmueble.id_propietario == usuario_actual.id_usuario
        )
    )
    imagen = result.scalar_one_or_none()
    
    if not imagen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imagen no encontrada o no autorizada"
        )
    
    # Eliminar archivo físico si existe
    if imagen.url_imagen and os.path.exists(f".{imagen.url_imagen}"):
        try:
            os.remove(f".{imagen.url_imagen}")
        except OSError:
            pass  # Continuar aunque no se pueda eliminar el archivo
    
    # Eliminar registro de la base de datos
    await db.delete(imagen)
    await db.commit()

# GET /imagenes/{id_inmueble} - Listar imágenes por inmueble
@router.get("/{id_inmueble}", response_model=List[ImagenOut])
async def listar_imagenes_inmueble(
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
    
    # Obtener imágenes del inmueble
    result = await db.execute(
        select(ImagenInmueble).where(ImagenInmueble.id_inmueble == id_inmueble)
    )
    imagenes = result.scalars().all()
    
    return imagenes
