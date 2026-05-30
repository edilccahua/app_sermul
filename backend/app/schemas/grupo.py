from pydantic import BaseModel
from datetime import date

from .parada import ParadaResponse
from .usuario import UsuarioResponse


class GrupoResponse(BaseModel):
    id: int
    codigo: str
    nombre: str
    parada_id: int
    descripcion: str | None = None
    circuito_area: str | None = None
    parada: ParadaResponse | None = None

    model_config = {"from_attributes": True}


class GrupoCreate(BaseModel):
    codigo: str
    nombre: str
    parada_id: int
    descripcion: str | None = None
    circuito_area: str | None = None


class GrupoUpdate(BaseModel):
    codigo: str | None = None
    nombre: str | None = None
    descripcion: str | None = None
    parada_id: int | None = None
    circuito_area: str | None = None


class GrupoIntegranteResponse(BaseModel):
    id: int
    usuario: "UsuarioResponse"
    activo: bool
    fecha_ingreso: date
    es_lider_frente: bool = False

    model_config = {"from_attributes": True}


class GrupoConIntegrantesResponse(GrupoResponse):
    integrantes: list[GrupoIntegranteResponse] = []


class IntegranteAddRequest(BaseModel):
    usuario_id: int
    es_lider_frente: bool = False
