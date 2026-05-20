from pydantic import BaseModel


class LoginRequest(BaseModel):
    dni: str
    password: str


class UsuarioPayload(BaseModel):
    id: int
    dni: str
    nombre: str
    apellido: str
    rol_codigo: str
    rol_nombre: str
    nivel_jerarquico: int

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioPayload
