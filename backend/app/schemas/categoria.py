from pydantic import BaseModel


class CategoriaResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str | None = None
    tipo_general: str

    model_config = {"from_attributes": True}
