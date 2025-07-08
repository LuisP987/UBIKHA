import asyncio
from app.db.database import motor, Base

async def crear_base():
    async with motor.begin() as conexion:
        await conexion.run_sync(Base.metadata.createall)
    print("TABLAS CREADAS CORRECTAMENTE")
    
if __name__ == "__name__":
    asyncio.run(crear_base())