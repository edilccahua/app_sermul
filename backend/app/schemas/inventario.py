from datetime import datetime

from pydantic import BaseModel

from .categoria import CategoriaResponse


class StockResponse(BaseModel):
    """Material del catálogo con sus contadores de stock"""
    id: int
    codigo_interno: str
    nombre: str
    descripcion: str | None = None
    marca: str | None = None
    categoria_id: int
    tipo_material: str
    costo_reposicion: float | None = None
    moneda: str
    cant_disponible: int = 0
    cant_en_uso: int = 0
    cant_malograda: int = 0
    cant_perdida: int = 0
    categoria: CategoriaResponse | None = None

    model_config = {"from_attributes": True}


class HerramientaEnUsoResponse(BaseModel):
    catalogo_id: int
    codigo_interno: str
    nombre_herramienta: str
    descripcion: str | None = None
    marca: str | None = None
    costo_reposicion: float | None = None
    cantidad_en_uso: int
    ultima_entrega: datetime
    dias_en_uso: int
    parada_id: int
    codigo_grupo: str

    model_config = {"from_attributes": True}


class AjusteStockRequest(BaseModel):
    catalogo_id: int
    tipo_ajuste: str  # "INGRESO_COMPRA" o "PASE_MALOGRADO"
    cantidad: int
    observaciones: str
    parada_id: int | None = None
