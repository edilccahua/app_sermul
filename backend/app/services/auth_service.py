from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..core.security import create_access_token, hash_password, verify_password
from ..models.usuario import Usuario


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate(self, dni: str, password: str) -> tuple[Usuario | None, str]:
        usuario = (
            self.db.query(Usuario)
            .filter(Usuario.dni == dni, Usuario.activo.is_(True))
            .first()
        )

        if usuario is None or not verify_password(password, usuario.password_hash):
            return None, ""

        usuario.ultimo_acceso = datetime.now(timezone.utc)
        self.db.commit()

        token = create_access_token(
            data={
                "sub": usuario.dni,
                "rol": usuario.rol.codigo,
            }
        )

        return usuario, token

    def change_password(self, usuario_id: int, new_password: str) -> None:
        usuario = self.db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )
        usuario.password_hash = hash_password(new_password)
        self.db.commit()

