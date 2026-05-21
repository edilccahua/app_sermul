from pydantic import BaseModel, Field

from .historial import HistorialResponse
from .inventario import InventarioResponse


class CheckOutRequest(BaseModel):
    short_code: str = Field(max_length=15)
    grupo_id: int
    parada_id: int


class CheckInRequest(BaseModel):
    inventario_id: int
    buen_estado: bool = True
    dano: str | None = None


class CheckResponse(BaseModel):
    movimiento: HistorialResponse
    unidad: InventarioResponse
