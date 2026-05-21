from pydantic import BaseModel

from .parada import ParadaResponse
from .usuario import UsuarioResponse


class GrupoResponse(BaseModel):
    id: int
    codigo: str
    nombre: str
    parada_id: int
    lider_id: int
    supervisor_id: int
    estado: str
    descripcion: str | None = None
    parada: ParadaResponse | None = None
    lider: UsuarioResponse | None = None
    supervisor: UsuarioResponse | None = None

    model_config = {"from_attributes": True}
