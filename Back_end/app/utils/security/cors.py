from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def aplicar_cors(app: FastAPI) -> None:
    # Lista de orígenes permitidos
    origins = [
        # Agrega tus IPs...
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
