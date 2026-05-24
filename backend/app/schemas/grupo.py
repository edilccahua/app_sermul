from pydantic import BaseModel
from datetime import date

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


class GrupoCreate(BaseModel):
    codigo: str
    nombre: str
    parada_id: int
    lider_id: int
    supervisor_id: int


class GrupoUpdate(BaseModel):
    nombre: str | None = None
    estado: str | None = None  # Activo, Inactivo, Finalizado
    lider_id: int | None = None
    supervisor_id: int | None = None


class GrupoIntegranteResponse(BaseModel):
    id: int
    usuario: "UsuarioResponse"  # forward reference
    activo: bool
    fecha_ingreso: date

    model_config = {"from_attributes": True}


class GrupoConIntegrantesResponse(GrupoResponse):
    integrantes: list[GrupoIntegranteResponse] = []


class IntegranteAddRequest(BaseModel):
    usuario_id: int
