from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.database import obtener_sesion
from models.user import Usuario as User
from schemas.user import UsuarioCrear, UsuarioMostrar
from utils.security.seguridad import hashear_password
from schemas.user import UsuarioEstado

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.get("/", response_model=list[UsuarioMostrar])
async def listar_usuarios(db: AsyncSession = Depends(obtener_sesion)):
    resultado = await db.execute(select(User))
    return resultado.scalars().all()

@router.get("/{email}", response_model=UsuarioMostrar)
async def obtener_usuario(email: str, db: AsyncSession = Depends(obtener_sesion)):
    resultado = await db.execute(select(User).where(User.email == email))
    usuario = resultado.scalars().first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

@router.post("/", response_model=UsuarioMostrar)
async def crear_usuario(datos: UsuarioCrear, db: AsyncSession = Depends(obtener_sesion)):
    nuevo_usuario = User(
        nombres=datos.nombres,
        apellido_paterno=datos.apellido_paterno,
        apellido_materno=datos.apellido_materno,
        num_celular=datos.num_celular,
        fecha_nacimiento=datos.fecha_nacimiento,
        email=datos.email,
        password=hashear_password(datos.password),
    )
    db.add(nuevo_usuario)
    await db.commit()
    await db.refresh(nuevo_usuario)
    return nuevo_usuario

   


@router.put("/{email}/estado", response_model=UsuarioMostrar)
async def cambiar_estado_usuario(email: str, datos: UsuarioEstado, db: AsyncSession = Depends(obtener_sesion)):
    resultado = await db.execute(select(User).where(User.email == email))
    usuario = resultado.scalars().first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.activo = datos.activo
    await db.commit()
    await db.refresh(usuario)
    return usuario

@router.delete("/{email}", response_model=dict)
async def eliminar_usuario(email: str, db: AsyncSession = Depends(obtener_sesion)):
    resultado = await db.execute(select(User).where(User.email == email))
    usuario = resultado.scalars().first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    await db.delete(usuario)
    await db.commit()
    return {"mensaje": "Usuario eliminado correctamente"}