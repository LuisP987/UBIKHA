from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.models.user import User

async def buscar_usuario_por_email(db: AsyncSession, email: str):
    resultado = await db.execute(select(User).where(User.email == email))
    return resultado.scalars().first()
