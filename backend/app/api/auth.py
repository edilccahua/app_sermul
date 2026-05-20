from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..schemas.auth import LoginRequest, LoginResponse, UsuarioPayload
from ..services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    usuario, token = service.authenticate(body.dni, body.password)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="DNI o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        usuario=UsuarioPayload(
            id=usuario.id,
            dni=usuario.dni,
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            rol_codigo=usuario.rol.codigo,
            rol_nombre=usuario.rol.nombre,
            nivel_jerarquico=usuario.rol.nivel_jerarquico,
        ),
    )
