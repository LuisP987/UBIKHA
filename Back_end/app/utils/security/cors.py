from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def aplicar_cors(app: FastAPI) -> None:
    # Lista de orígenes permitidos
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
        "http://26.249.199.127:5175",
        #Alexander - Nuevo servidor
        "http://26.196.154.46:8000",
        "http://26.196.154.46:5175"
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
