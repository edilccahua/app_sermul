from datetime import date

from pydantic import BaseModel, Field

from .catalogo import CatalogoResponse


class UbicacionUpdate(BaseModel):
    ubicacion_macro: str = Field(max_length=20)


class InventarioResponse(BaseModel):
    id: int
    codigo_barras: str | None = None
    catalogo_id: int
    numero_serie: str | None = None
    estado: str
    ubicacion_fisica: str | None = None
    ubicacion_macro: str
    fecha_adquisicion: date | None = None
    observaciones: str | None = None
    catalogo: CatalogoResponse | None = None

    model_config = {"from_attributes": True}
