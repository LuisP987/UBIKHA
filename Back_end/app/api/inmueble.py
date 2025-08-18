from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from utils.roles import tiene_rol, agregar_rol, es_arrendatario, es_arrendador
from sqlalchemy import update
from models import Inmueble, CaracteristicasInmueble
from models.usuario import Usuario
from db.database import obtener_sesion
from typing import List, Optional
from schemas.inmueble import (
    InmuebleCreate, InmuebleCreateCompleto, InmuebleOut, 
    InmuebleUpdate, EstadoInmueble, InmuebleCreateResponse
)
from typing import Dict, Any
from sqlalchemy.future import select
from utils.security.jwt import obtener_usuario_actual
from pydantic import ValidationError
import traceback  

# Constantes para mensajes
INMUEBLE_NO_ENCONTRADO = "Inmueble no encontrado"
INMUEBLE_CREADO = "Inmueble creado exitosamente"

router = APIRouter(prefix="/inmuebles", tags=["inmuebles"])

# POST: Crear nuevo inmueble (completo)
@router.post("/", response_model=InmuebleCreateResponse)
async def crear_inmueble(
    datos: InmuebleCreateCompleto, 
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Crear un nuevo inmueble con toda la información completa.
    
    El inmueble se crea con estado 'en revisión' para aprobación administrativa.
    Si es el primer inmueble del usuario, se le otorga el rol de 'arrendador'.
    
    ### Validaciones aplicadas:
    - **Título**: Entre 5 y 100 caracteres
    - **Descripción**: Mínimo 10 caracteres si se proporciona
    - **Precio**: Entre S/1 y S/50,000 por mes
    - **Dirección**: Mínimo 10 caracteres, debe incluir distrito de Lima
    - **Capacidad**: Entre 1 y 20 huéspedes
    - **Habitaciones**: Entre 0 y 10
    - **Baños**: Entre 1 y 10
    - **Camas**: Entre 1 y 15
    
    ### Errores comunes:
    - **422 Validation Error**: Datos no válidos según las validaciones del schema
    - **401 Unauthorized**: Token de autenticación inválido
    - **500 Internal Server Error**: Error del servidor
    """
    try:
        # Calcular precio final con comisión de UBIKHA (10%)
        COMISION_UBIKHA = 0.10
        precio_final = datos.precio_mensual * (1 + COMISION_UBIKHA)
        comision = datos.precio_mensual * COMISION_UBIKHA
        
        # Validar que el usuario actual existe y está activo
        if not usuario_actual or not usuario_actual.activo:
            raise HTTPException(
                status_code=403,
                detail="Usuario no autorizado para crear inmuebles. Verifique que su cuenta esté activa."
            )
        
        # Crear el inmueble principal
        datos_inmueble = {
            "id_propietario": usuario_actual.id_usuario,
            "titulo": datos.titulo,
            "descripcion": datos.descripcion,
            "precio_mensual": datos.precio_mensual,
            "tipo_inmueble": datos.tipo_inmueble.value,
            "estado": "en revisión"  # Estado inicial para revisión administrativa
        }
        
        inmueble = Inmueble(**datos_inmueble)
        db.add(inmueble)
        await db.flush()  # Para obtener el ID sin hacer commit completo
        
        # Crear las características del inmueble (todos los campos restaurados)
        datos_caracteristicas = {
            "id_inmueble": inmueble.id_inmueble,
            "direccion": datos.direccion,
            "referencias": datos.referencias,
            "habitaciones": datos.habitaciones,
            "camas": datos.camas,
            "banos": datos.banos,
            "capacidad": datos.huespedes,
            "wifi": datos.wifi,
            "cocina": datos.cocina,
            "estacionamiento": datos.estacionamiento,
            "television": datos.television,
            "aire_acondicionado": datos.aire_acondicionado,
            "servicio_lavanderia": datos.servicio_lavanderia,
            "mascotas_permitidas": datos.mascotas_permitidas,
            "camaras_seguridad": datos.camaras_seguridad
        }
        
        caracteristicas = CaracteristicasInmueble(**datos_caracteristicas)
        db.add(caracteristicas)
        
        # Verificar si es el primer inmueble del usuario para agregar rol de arrendador
        roles_actuales = usuario_actual.tipo_usuario
        nuevos_roles = roles_actuales
        
        # Verificar si ya tiene el rol de arrendador
        if not es_arrendador(usuario_actual):
            # Verificar si ya tiene otros inmuebles
            result = await db.execute(
                select(Inmueble).where(
                    Inmueble.id_propietario == usuario_actual.id_usuario,
                    Inmueble.id_inmueble != inmueble.id_inmueble
                )
            )
            inmuebles_existentes = result.scalars().all()
            
            # Si no tiene inmuebles (este será el primero), agregar rol de arrendador
            if not inmuebles_existentes:
                # Agregar rol de arrendador manteniendo los existentes
                nuevos_roles = agregar_rol(roles_actuales, "arrendador")
                
                await db.execute(
                    update(Usuario)
                    .where(Usuario.id_usuario == usuario_actual.id_usuario)
                    .values(tipo_usuario=nuevos_roles)
                )
        
        await db.commit()
        await db.refresh(inmueble)
        
        return InmuebleCreateResponse(
            mensaje="Inmueble creado exitosamente y enviado a revisión administrativa",
            id_inmueble=inmueble.id_inmueble,
            estado=inmueble.estado,
            precio_mensual=datos.precio_mensual,
            precio_final=precio_final,
            comision_ubikha=comision,
            nuevo_rol_usuario=nuevos_roles
        )
        
    except ValidationError as ve:
        await db.rollback()
        # Crear un mensaje de error más claro para validaciones
        errores_detallados = []
        for error in ve.errors():
            campo = " -> ".join(str(loc) for loc in error["loc"])
            mensaje = error["msg"]
            errores_detallados.append(f"Campo '{campo}': {mensaje}")
        
        raise HTTPException(
            status_code=422,
            detail={
                "mensaje": "Errores de validación en los datos proporcionados",
                "errores": errores_detallados,
                "sugerencia": "Revise los valores ingresados y asegúrese de que cumplan con los requisitos indicados"
            }
        )
    except HTTPException:
        await db.rollback()
        raise  # Re-lanzar HTTPExceptions sin modificar
    except Exception as e:
        await db.rollback()
        # Log del error completo para debugging
        error_trace = traceback.format_exc()
        print(f"Error inesperado al crear inmueble: {error_trace}")
        
        raise HTTPException(
            status_code=500,
            detail={
                "mensaje": "Error interno del servidor al crear el inmueble",
                "error": str(e),
                "sugerencia": "Verifique que todos los datos estén completos y vuelva a intentar. Si el problema persiste, contacte al soporte técnico."
            }
        )

# POST: Crear inmueble simple (compatibilidad con versión anterior)
@router.post("/simple", response_model=Dict[str, Any])
async def crear_inmueble_simple(
    datos: InmuebleCreate, 
    db: AsyncSession = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Endpoint de compatibilidad para crear inmueble con datos básicos solamente.
    """
    # Crear el inmueble con el ID del usuario autenticado
    datos_dict = datos.dict()
    datos_dict["id_propietario"] = usuario_actual.id_usuario
    datos_dict["estado"] = "en revisión"  # Estado inicial
    
    inmueble = Inmueble(**datos_dict)
    db.add(inmueble)
    
    await db.commit()
    await db.refresh(inmueble)
    
    return {
        "message": INMUEBLE_CREADO,
        "id_inmueble": inmueble.id_inmueble,
        "estado": inmueble.estado,
        "nuevo_rol": "deprecated - usar endpoint principal"
    }

# GET: Listar inmuebles filtrados
@router.get("/", response_model=List[InmuebleOut])
async def listar_inmuebles(tipo_inmueble: Optional[str] = None, db: AsyncSession = Depends(obtener_sesion)):
    try:
        # Usar joinedload para cargar características en una sola consulta
        from sqlalchemy.orm import joinedload
        
        stmt = select(Inmueble).options(joinedload(Inmueble.caracteristicas))
        if tipo_inmueble:
            stmt = stmt.where(Inmueble.tipo_inmueble == tipo_inmueble)
        
        result = await db.execute(stmt)
        inmuebles = result.unique().scalars().all()
        
        # Construir respuesta con características incluidas
        inmuebles_con_caracteristicas = []
        for inmueble in inmuebles:
            caracteristicas = inmueble.caracteristicas
            
            # Calcular precio final con comisión
            COMISION_UBIKHA = 0.10
            precio_final = inmueble.precio_mensual * (1 + COMISION_UBIKHA)
            
            inmueble_data = {
                "id_inmueble": inmueble.id_inmueble,
                "id_propietario": inmueble.id_propietario,
                "titulo": inmueble.titulo,
                "descripcion": inmueble.descripcion,
                "precio_mensual": inmueble.precio_mensual,
                "precio_final": precio_final,
                "tipo_inmueble": inmueble.tipo_inmueble,
                "estado": inmueble.estado,
                # Datos de ubicación y capacidad
                "direccion": caracteristicas.direccion if caracteristicas else None,
                "referencias": caracteristicas.referencias if caracteristicas else None,
                "huespedes": caracteristicas.capacidad if caracteristicas else None,
                "habitaciones": caracteristicas.habitaciones if caracteristicas else None,
                "banos": caracteristicas.banos if caracteristicas else None,
                "camas": caracteristicas.camas if caracteristicas else None,
                # Servicios
                "wifi": caracteristicas.wifi if caracteristicas else False,
                "cocina": caracteristicas.cocina if caracteristicas else False,
                "estacionamiento": caracteristicas.estacionamiento if caracteristicas else False,
                "television": caracteristicas.television if caracteristicas else False,
                "aire_acondicionado": caracteristicas.aire_acondicionado if caracteristicas else False,
                "servicio_lavanderia": caracteristicas.servicio_lavanderia if caracteristicas else False,
                "camaras_seguridad": caracteristicas.camaras_seguridad if caracteristicas else False,
                "mascotas_permitidas": caracteristicas.mascotas_permitidas if caracteristicas else False
            }
            inmuebles_con_caracteristicas.append(inmueble_data)
        
        return inmuebles_con_caracteristicas
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al listar inmuebles: {str(e)}"
        )

# GET: Ver detalle de inmueble
@router.get("/{id_inmueble}", response_model=InmuebleOut)
async def detalle_inmueble(id_inmueble: int, db: AsyncSession = Depends(obtener_sesion)):
    """
    Obtener los detalles completos de un inmueble específico.
    
    Incluye toda la información del inmueble y sus características.
    """
    try:
        # Buscar el inmueble
        result = await db.execute(
            select(Inmueble).where(Inmueble.id_inmueble == id_inmueble)
        )
        inmueble = result.scalars().first()
        
        if not inmueble:
            raise HTTPException(status_code=404, detail=INMUEBLE_NO_ENCONTRADO)
        
        # Buscar las características del inmueble de forma asíncrona
        result_caracteristicas = await db.execute(
            select(CaracteristicasInmueble).where(CaracteristicasInmueble.id_inmueble == id_inmueble)
        )
        caracteristicas = result_caracteristicas.scalars().first()
        
        # Calcular precio final con comisión
        COMISION_UBIKHA = 0.10
        precio_final = inmueble.precio_mensual * (1 + COMISION_UBIKHA)
        
        return {
            "id_inmueble": inmueble.id_inmueble,
            "id_propietario": inmueble.id_propietario,
            "titulo": inmueble.titulo,
            "descripcion": inmueble.descripcion,
            "precio_mensual": inmueble.precio_mensual,
            "precio_final": precio_final,
            "tipo_inmueble": inmueble.tipo_inmueble,
            "estado": inmueble.estado,
            # Datos de ubicación y capacidad (valores por defecto si no hay características)
            "direccion": caracteristicas.direccion if caracteristicas else "Dirección no especificada",
            "referencias": caracteristicas.referencias if caracteristicas else None,
            "huespedes": caracteristicas.capacidad if caracteristicas else 1,
            "habitaciones": caracteristicas.habitaciones if caracteristicas else 1,
            "banos": caracteristicas.banos if caracteristicas else 1,
            "camas": caracteristicas.camas if caracteristicas else 1,
            # Servicios (valores por defecto False si no hay características)
            "wifi": caracteristicas.wifi if caracteristicas else False,
            "cocina": caracteristicas.cocina if caracteristicas else False,
            "estacionamiento": caracteristicas.estacionamiento if caracteristicas else False,
            "television": caracteristicas.television if caracteristicas else False,
            "aire_acondicionado": caracteristicas.aire_acondicionado if caracteristicas else False,
            "servicio_lavanderia": caracteristicas.servicio_lavanderia if caracteristicas else False,
            "camaras_seguridad": caracteristicas.camaras_seguridad if caracteristicas else False,
            "mascotas_permitidas": caracteristicas.mascotas_permitidas if caracteristicas else False
        }
        
    except HTTPException:
        raise  # Re-lanzar HTTPExceptions sin modificar
    except Exception as e:
        # Log del error completo para debugging
        error_trace = traceback.format_exc()
        print(f"Error inesperado al obtener detalle del inmueble {id_inmueble}: {error_trace}")
        
        raise HTTPException(
            status_code=500,
            detail={
                "mensaje": "Error interno del servidor al obtener el detalle del inmueble",
                "error": str(e),
                "sugerencia": "Verifique que el inmueble existe y vuelva a intentar."
            }
        )

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