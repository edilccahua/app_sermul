from pydantic import BaseModel, Field

from .categoria import CategoriaResponse


class CatalogoCreate(BaseModel):
    codigo_interno: str = Field(max_length=15)
    nombre: str = Field(max_length=200)
    descripcion: str | None = None
    categoria_id: int
    tipo_material: str = Field(max_length=30)
    costo_reposicion: float | None = None
    moneda: str = "PEN"
    es_devolutivo: bool
    stock_minimo: int | None = None
    unidad_medida: str | None = None
    cantidad: int = 0
    cant_disponible: int = 0
    cant_en_uso: int = 0
    cant_malograda: int = 0
    cant_perdida: int = 0


class CatalogoUpdate(BaseModel):
    nombre: str | None = Field(None, max_length=200)
    descripcion: str | None = None
    categoria_id: int | None = None
    tipo_material: str | None = Field(None, max_length=30)
    costo_reposicion: float | None = None
    es_devolutivo: bool | None = None
    stock_minimo: int | None = None
    unidad_medida: str | None = None
    activo: bool | None = None


class CatalogoResponse(BaseModel):
    id: int
    codigo_interno: str
    nombre: str
    descripcion: str | None = None
    categoria_id: int
    tipo_material: str
    costo_reposicion: float | None = None
    moneda: str
    es_devolutivo: bool
    stock_minimo: int | None = None
    unidad_medida: str | None = None
    activo: bool
    cantidad: int = 0
    cant_disponible: int = 0
    cant_en_uso: int = 0
    cant_malograda: int = 0
    cant_perdida: int = 0
    categoria: CategoriaResponse | None = None

    model_config = {"from_attributes": True}
