from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from models import Inmueble, CaracteristicasInmueble
from models.usuario import Usuario
from db.database import obtener_sesion
from typing import List, Optional
from schemas.inmueble import InmuebleCreate, InmuebleOut, InmuebleUpdate, EstadoInmueble
from typing import Dict, Any
from sqlalchemy.future import select
from utils.security.jwt import obtener_usuario_actual  

# Constantes para mensajes
INMUEBLE_NO_ENCONTRADO = "Inmueble no encontrado"
INMUEBLE_CREADO = "Inmueble creado exitosamente"

router = APIRouter(prefix="/inmuebles", tags=["inmuebles"])

# POST: Crear nuevo inmueble
@router.post("/", response_model=Dict[str, Any])
async def crear_inmueble(
    datos: InmuebleCreate, 
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    # Crear el inmueble con el ID del usuario autenticado
    datos_dict = datos.dict()
    datos_dict["id_propietario"] = usuario_actual.id_usuario
    
    inmueble = Inmueble(**datos_dict)
    db.add(inmueble)
    
    # Si es el primer inmueble del usuario, cambiar rol a "arrendador"
    if usuario_actual.tipo_usuario == "arrendatario":
        # Verificar si ya tiene inmuebles
        result = await db.execute(
            select(Inmueble).where(Inmueble.id_propietario == usuario_actual.id_usuario)
        )
        inmuebles_existentes = result.scalars().all()
        
        # Si no tiene inmuebles (este será el primero), cambiar rol
        if not inmuebles_existentes:
            # Actualizar el rol directamente en la base de datos
            await db.execute(
                update(Usuario)
                .where(Usuario.id_usuario == usuario_actual.id_usuario)
                .values(tipo_usuario="arrendador")
            )
            nuevo_rol = "arrendador"
        else:
            nuevo_rol = usuario_actual.tipo_usuario
    else:
        nuevo_rol = usuario_actual.tipo_usuario
    
    await db.commit()
    await db.refresh(inmueble)
    
    return {
        "message": INMUEBLE_CREADO,
        "id_inmueble": inmueble.id_inmueble,
        "nuevo_rol": nuevo_rol
    }

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
        raise HTTPException(status_code=404, detail=INMUEBLE_NO_ENCONTRADO)
    caracteristicas = inmueble.caracteristicas
    return {
        "id_inmueble": inmueble.id_inmueble,
        "id_propietario": inmueble.id_propietario,
        "titulo": inmueble.titulo,
        "descripcion": inmueble.descripcion,
        "precio_mensual": inmueble.precio_mensual,
        "tipo_inmueble": inmueble.tipo_inmueble,
        "estado": inmueble.estado,
        "wifi": caracteristicas.wifi if caracteristicas else False,
        "cocina": caracteristicas.cocina if caracteristicas else False,
        "refrigeradora": caracteristicas.refrigeradora if caracteristicas else False,
        "estacionamiento": caracteristicas.estacionamiento if caracteristicas else False,
        "mascotas_permitidas": caracteristicas.mascotas_permitidas if caracteristicas else False,
        "camaras_seguridad": caracteristicas.camaras_seguridad if caracteristicas else False
    }

# PUT: Editar inmueble
@router.put("/{id_inmueble}", response_model=Dict)
async def editar_inmueble(id_inmueble: int, datos: InmuebleUpdate, db: AsyncSession = Depends(obtener_sesion)):
    inmueble = await db.get(Inmueble, id_inmueble)
    if not inmueble:
        raise HTTPException(status_code=404, detail=INMUEBLE_NO_ENCONTRADO)
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
        raise HTTPException(status_code=404, detail=INMUEBLE_NO_ENCONTRADO)
    await db.delete(inmueble)
    await db.commit()
    return {"message": "Inmueble eliminado"}

# PATCH: Cambiar estado del inmueble
@router.patch("/{id_inmueble}/estado")
async def cambiar_estado_inmueble(id_inmueble: int, datos: EstadoInmueble, db: AsyncSession = Depends(obtener_sesion)):
    inmueble = await db.get(Inmueble, id_inmueble)
    if not inmueble:
        raise HTTPException(status_code=404, detail=INMUEBLE_NO_ENCONTRADO)
    
    # Usar sqlalchemy update para evitar errores de tipo
    await db.execute(
        update(Inmueble)
        .where(Inmueble.id_inmueble == id_inmueble)
        .values(estado=datos.estado.value)
    )
    await db.commit()
    await db.refresh(inmueble)
    return {"message": f"Estado cambiado a {datos.estado.value}"}