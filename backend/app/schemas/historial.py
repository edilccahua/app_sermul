import uuid
from datetime import datetime

from pydantic import BaseModel


class HistorialResponse(BaseModel):
    id: uuid.UUID
    timestamp: datetime
    tipo_movimiento: str
    inventario_fisico_id: int | None = None
    catalogo_id: int
    parada_id: int
    cantidad: int
    usuario_ejecuta_id: int | None = None
    grupo_destino_id: int | None = None
    usuario_receptor_id: int | None = None
    estado_origen: str | None = None
    estado_destino: str | None = None
    observaciones: str | None = None

    model_config = {"from_attributes": True}


class HistorialFilter(BaseModel):
    parada_id: int | None = None
    tipo: str | None = None
    fecha_desde: datetime | None = None
    fecha_hasta: datetime | None = None
