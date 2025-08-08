from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback
import logging
from typing import Union

# Configurar logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Manejador global de excepciones para proporcionar respuestas de error más informativas
    """
    
    # Si es una HTTPException de FastAPI, mantener el comportamiento original pero log el error
    if isinstance(exc, (HTTPException, StarletteHTTPException)):
        logger.error(f"HTTP Exception en {request.url}: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "status_code": exc.status_code,
                "path": str(request.url.path)
            }
        )
    
    # Si es un error de validación, proporcionar más detalles
    if isinstance(exc, RequestValidationError):
        logger.error(f"Validation Error en {request.url}: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Error de validación en los datos enviados",
                "errors": exc.errors(),
                "status_code": 422,
                "path": str(request.url.path)
            }
        )
    
    # Para cualquier otra excepción no manejada
    logger.error(f"Error no manejado en {request.url}: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"Error interno del servidor: {str(exc)}",
            "type": type(exc).__name__,
            "status_code": 500,
            "path": str(request.url.path),
            "traceback": traceback.format_exc() if logger.level <= logging.DEBUG else None
        }
    )

async def database_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Manejador específico para errores de base de datos
    """
    logger.error(f"Database Error en {request.url}: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error en la base de datos. Por favor, inténtalo de nuevo.",
            "error_type": "database_error",
            "status_code": 500,
            "path": str(request.url.path),
            "technical_details": str(exc) if logger.level <= logging.DEBUG else None
        }
    )
