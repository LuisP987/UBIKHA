from fastapi import FastAPI
from api import auth, Confirmacion, base, user as user_router, verification, favorito, inmueble
from api import mensaje, reserva, pago, imagen, resena, notificacion, reporte, whatsapp_auth
from utils.security import cors
from utils.error_handlers import global_exception_handler, database_exception_handler
from sqlalchemy.exc import SQLAlchemyError
import socket
import requests
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="UBIKHA API",
    description="API para el sistema de alquiler de inmuebles UBIKHA",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"  
)

# Aplicar manejadores de errores globales
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)

#aplicar el cors
cors.aplicar_cors(app)
# Routers
app.include_router(base.router)
#app.include_router(verification.router)  
app.include_router(auth.router)
app.include_router(user_router.router)
#app.include_router(Confirmacion.router)
app.include_router(favorito.router)
app.include_router(inmueble.router)
app.include_router(mensaje.router)
app.include_router(reserva.router)
app.include_router(pago.router)
app.include_router(imagen.router)
app.include_router(resena.router)
app.include_router(notificacion.router)
app.include_router(reporte.router)
# WhatsApp Authentication Router
app.include_router(whatsapp_auth.router)

def obtener_ip_local():
    """Obtiene la IP local de la máquina"""
    try:
        # Obtener IP local
        hostname = socket.gethostname()
        ip_local = socket.gethostbyname(hostname)
        return ip_local
    except Exception as e:
        return "127.0.0.1"

def obtener_ip_publica():
    """Obtiene la IP pública (opcional)"""
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=3)
        return response.json()["ip"]
    except:
        return "No disponible"

if __name__ == "__main__":
    import uvicorn
    
    # Obtener IPs
    ip_local = obtener_ip_local()
    ip_publica = obtener_ip_publica()
    
    print("INFORMACIÓN DEL SERVIDOR:")
    print(f"IP Local: {ip_local}")
    print(f"IP Pública: {ip_publica}")
    print(f"URL Local: http://localhost:8000")
    print(f"URL Red: http://{ip_local}:8000")
    print(f"Swagger UI: http://localhost:8000/docs")
    print(f"ReDoc: http://localhost:8000/redoc")
    print("=" * 50)
    
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)