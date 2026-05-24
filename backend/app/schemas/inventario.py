from pydantic import BaseModel

from .categoria import CategoriaResponse


class StockResponse(BaseModel):
    """Material del catálogo con sus contadores de stock"""
    id: int
    codigo_interno: str
    nombre: str
    categoria_id: int
    tipo_material: str
    costo_reposicion: float | None = None
    moneda: str
    cantidad: int = 0
    cant_disponible: int = 0
    cant_en_uso: int = 0
    cant_malograda: int = 0
    cant_perdida: int = 0
    categoria: CategoriaResponse | None = None

    model_config = {"from_attributes": True}
