from sqlalchemy import text
from fastapi import FastAPI
from db.database import motor, Base
from db.models import user

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    async with motor.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)  # Solo si quieres resetear la DB
        await conn.run_sync(Base.metadata.create_all)
    print("Tablas creadas en la base de datos.")

@app.get("/")
async def root():
    return {"mensaje": "Bienevenido a la API de Ubikha"}

@app.get("/conexion-db")
async def probar_conexion():
    try:
        async with motor.connect() as conexion:
            await conexion.execute(text("SELECT 1"))
        return {"estado": "CONEXION EXITOSA A LA BASE DE DATOS"}
    except Exception as errores:
        return {"estado": "CONEXION FALLIDA A LA BASE DE DATOS", "detalles": str(errores)}   
