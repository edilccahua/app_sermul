from datetime import date, datetime
from pydantic import BaseModel

from .parada import ParadaResponse
from .grupo import GrupoConIntegrantesResponse
from .usuario import UsuarioResponse


class ReservaItemCreate(BaseModel):
    catalogo_id: int
    cantidad_solicitada: int = 1


class ReservaCreate(BaseModel):
    parada_id: int
    grupo_id: int
    turno: str | None = None
    fecha_programada: date
    items: list[ReservaItemCreate]


class ReservaItemResponse(BaseModel):
    id: int
    catalogo_id: int
    codigo_interno: str
    nombre: str
    descripcion: str | None = None
    marca: str | None = None
    cantidad_solicitada: int
    cantidad_disponible: int
    cantidad_despachada: int

    model_config = {"from_attributes": True}


class ReservaResponse(BaseModel):
    id: int
    codigo_reserva: str
    turno: str | None = None
    fecha_programada: date
    estado: str
    parada_id: int
    grupo_id: int
    creado_por_id: int
    motivo_rechazo: str | None = None
    fecha_aprobacion: datetime | None = None
    fecha_despacho: datetime | None = None
    aprobado_por: UsuarioResponse | None = None
    despachado_por: UsuarioResponse | None = None
    parada: ParadaResponse | None = None
    grupo: GrupoConIntegrantesResponse | None = None
    detalles: list[ReservaItemResponse] = []
    alertas_stock: list[dict] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class AprobarReservaRequest(BaseModel):
    pass  # sin body, el usuario se toma del token


class RechazarReservaRequest(BaseModel):
    motivo: str


class DespacharReservaRequest(BaseModel):
    items_ids: list[int] | None = None  # None = despachar todos
