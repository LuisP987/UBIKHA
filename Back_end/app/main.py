from sqlalchemy import text
from fastapi import FastAPI
from app.db.database import motor

app = FastAPI()

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
