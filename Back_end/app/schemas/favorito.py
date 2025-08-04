from pydantic import BaseModel

class FavoritoCreate(BaseModel):
    id_usuario: int
    id_inmueble: int

class FavoritoOut(BaseModel):
    id_usuario: int
    id_inmueble: int

    class Config:
        orm_mode = True
