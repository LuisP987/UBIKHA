from fastapi import FastAPI
from sqlalchemy import text
from db.database import motor, Base
from models import user
from api import auth  #Importacion del router
from api import user as user_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS - Dominios Permitidos
origins = [
    "http://localhost:5175",
    #Roy
    "http://26.214.10.51:8000",
    "http://26.214.10.51:5175",
    #Achiri
    "http://26.131.181.67:8000",
    "http://26.131.181.67:5175",
    #Mark
    "http://26.55.199.45:8000",
    "http://26.55.199.45:5175",
    #Luis
    "http://26.249.199.127:8000",
    "http://26.249.199.127:5175"
    
]

# Middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # Orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],            # Métodos permitidos
    allow_headers=["*"],            # Headers permitidos
)

# Routers
app.include_router(auth.router)
app.include_router(user_router.router)

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
