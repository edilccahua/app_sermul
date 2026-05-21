from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import decode_access_token
from ..models.usuario import Usuario
from ..models.permiso import Permiso, RolPermiso

security_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    try:
        payload = decode_access_token(credentials.credentials)
        dni = str(payload.get("sub", ""))
        if not dni:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    usuario = (
        db.query(Usuario)
        .filter(Usuario.dni == dni, Usuario.activo.is_(True))
        .first()
    )
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return usuario


class RequirePermission:
    def __init__(self, permiso_codigo: str):
        self.permiso_codigo = permiso_codigo

    def __call__(
        self,
        usuario: Usuario = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> Usuario:
        permiso = (
            db.query(Permiso)
            .filter(Permiso.codigo == self.permiso_codigo)
            .first()
        )
        if not permiso:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Permiso '{self.permiso_codigo}' no encontrado en el sistema",
            )

        rol_permiso = (
            db.query(RolPermiso)
            .filter(
                RolPermiso.rol_id == usuario.rol_id,
                RolPermiso.permiso_id == permiso.id,
            )
            .first()
        )
        if not rol_permiso:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para esta acción",
            )

        return usuario
