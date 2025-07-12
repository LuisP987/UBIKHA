from fastapi import FastAPI
from sqlalchemy import text
from db.database import motor, Base
from db.models import user
from api import auth  # 👈 Importa el router

app = FastAPI()

# 👇 Incluye el router de autenticación
app.include_router(auth.router)

@app.on_event("startup")
async def on_startup():
    async with motor.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tablas creadas en la base de datos.")

@app.get("/")
async def root():
    return {"mensaje": "Bienvenido a la API de Ubikha"}

@app.get("/conexion-db")
async def probar_conexion():
    try:
        async with motor.connect() as conexion:
            await conexion.execute(text("SELECT 1"))
        return {"estado": "CONEXIÓN EXITOSA A LA BASE DE DATOS"}
    except Exception as errores:
        return {"estado": "CONEXIÓN FALLIDA A LA BASE DE DATOS", "detalles": str(errores)}
