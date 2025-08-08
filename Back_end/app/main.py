from fastapi import FastAPI
from api import auth, base, user as user_router, favorito, inmueble
from api import mensaje, reserva, pago, imagen, resena, notificacion, reporte, whatsapp_auth
from utils.security import cors
from utils.exceptions.error_handlers import global_exception_handler, database_exception_handler
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from utils.Command.red import imprimir_info_servidor
import uvicorn
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

if __name__ == "__main__":
    imprimir_info_servidor()
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)