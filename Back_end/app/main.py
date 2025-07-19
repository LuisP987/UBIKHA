from fastapi import FastAPI
from api import auth, Confirmacion, base, user as user_router
from utils.security import cors


app = FastAPI()

#aplicar el cors
cors.aplicar_cors(app)
# Routers
app.include_router(auth.router)
app.include_router(user_router.router)
app.include_router(Confirmacion.router)
app.include_router(base.router)
