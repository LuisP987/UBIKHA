from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user import Usuario

async def buscar_usuario_por_email(db: AsyncSession, email: str):
    resultado = await db.execute(select(Usuario).where(Usuario.email == email))
    return resultado.scalars().first()

async def crear_usuario(db: AsyncSession, datos: dict):
    nuevo = Usuario(**datos)
    db.add(nuevo)
    await db.commit()
    await db.refresh(nuevo)
    return nuevo