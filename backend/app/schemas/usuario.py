from datetime import datetime

from pydantic import BaseModel


class RolResponse(BaseModel):
    id: int
    codigo: str
    nombre: str

    model_config = {"from_attributes": True}


class UsuarioResponse(BaseModel):
    id: int
    dni: str
    nombre: str
    apellido: str
    email: str | None = None
    telefono: str | None = None
    rol_id: int
    activo: bool
    ultimo_acceso: datetime | None = None
    rol: RolResponse | None = None

    model_config = {"from_attributes": True}
