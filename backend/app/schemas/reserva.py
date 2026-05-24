from datetime import date, datetime
from pydantic import BaseModel, Field

from .parada import ParadaResponse
from .grupo import GrupoConIntegrantesResponse


class ReservaItemCreate(BaseModel):
    catalogo_id: int
    cantidad_solicitada: int = 1


class ReservaCreate(BaseModel):
    parada_id: int
    grupo_id: int
    turno: str = Field(pattern=r"^(Dia|Noche)$")
    fecha_programada: date
    tarea_id: int | None = None
    items: list[ReservaItemCreate]


class ReservaItemResponse(BaseModel):
    catalogo_id: int
    codigo_interno: str
    nombre: str
    cantidad_solicitada: int
    cantidad_disponible: int
    cantidad_despachada: int

    model_config = {"from_attributes": True}


class ReservaResponse(BaseModel):
    id: int
    codigo_reserva: str
    turno: str
    fecha_programada: date
    estado: str
    parada_id: int
    grupo_id: int
    creado_por_id: int
    tarea_id: int | None = None
    motivo_rechazo: str | None = None
    fecha_aprobacion: datetime | None = None
    fecha_despacho: datetime | None = None
    parada: ParadaResponse | None = None
    grupo: GrupoConIntegrantesResponse | None = None
    items: list[ReservaItemResponse] = []
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
