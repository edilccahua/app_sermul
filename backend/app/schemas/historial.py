import uuid
from datetime import datetime

from pydantic import BaseModel

from .catalogo import CatalogoResponse
from .parada import ParadaResponse
from .grupo import GrupoResponse
from .usuario import UsuarioResponse


class HistorialResponse(BaseModel):
    id: uuid.UUID
    timestamp: datetime
    tipo_movimiento: str
    catalogo_id: int
    parada_id: int
    cantidad: int = 1
    usuario_ejecuta_id: int | None = None
    grupo_destino_id: int | None = None
    usuario_receptor_id: int | None = None
    estado_origen: str | None = None
    estado_destino: str | None = None
    observaciones: str | None = None
    observacion_entrega: str | None = None
    observacion_recepcion: str | None = None
    catalogo: CatalogoResponse | None = None
    parada: ParadaResponse | None = None
    grupo_destino: GrupoResponse | None = None
    usuario_ejecuta: UsuarioResponse | None = None
    usuario_receptor: UsuarioResponse | None = None

    model_config = {"from_attributes": True}


class HistorialFilter(BaseModel):
    parada_id: int | None = None
    tipo: str | None = None
    fecha_desde: datetime | None = None
    fecha_hasta: datetime | None = None
    catalogo_id: int | None = None
