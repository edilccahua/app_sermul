from pydantic import BaseModel


class EspecialidadCreate(BaseModel):
    nombre: str


class EspecialidadResponse(BaseModel):
    id: int
    nombre: str

    model_config = {"from_attributes": True}
