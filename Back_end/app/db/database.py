from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

motor = create_async_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker (
    bind=motor,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def obtener_sesion():
    async with SessionLocal() as sesion:
        yield sesion