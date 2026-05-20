from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..core.security import create_access_token, verify_password
from ..models.usuario import Usuario


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate(self, dni: str, password: str) -> tuple[Usuario | None, str | None]:
        usuario = (
            self.db.query(Usuario)
            .filter(Usuario.dni == dni, Usuario.activo.is_(True))
            .first()
        )

        if usuario is None or not verify_password(password, usuario.password_hash):
            return None, None

        usuario.ultimo_acceso = datetime.now(timezone.utc)
        self.db.commit()

        token = create_access_token(
            data={
                "sub": usuario.dni,
                "rol": usuario.rol.codigo,
            }
        )

        return usuario, token
