from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..core.security import hash_password
from ..models import GrupoIntegrante, Usuario
from ..schemas.usuario import UsuarioCreate


class UsuarioService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Usuario]:
        return (
            self.db.query(Usuario)
            .filter(Usuario.activo.is_(True))
            .order_by(Usuario.apellido)
            .all()
        )

    def get_by_id(self, usuario_id: int) -> Usuario:
        usuario = (
            self.db.query(Usuario)
            .filter(Usuario.id == usuario_id)
            .first()
        )
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )

        historial_grupos = (
            self.db.query(GrupoIntegrante)
            .filter(GrupoIntegrante.usuario_id == usuario_id)
            .order_by(GrupoIntegrante.fecha_ingreso.desc())
            .all()
        )

        grupos = []
        paradas_historial = []
        seen_paradas = set()
        for gi in historial_grupos:
            grupo = gi.grupo
            parada = grupo.parada if grupo else None
            grupos.append({
                "grupo_id": gi.grupo_id,
                "grupo_codigo": grupo.codigo if grupo else "",
                "grupo_nombre": grupo.nombre if grupo else "",
                "parada_id": parada.id if parada else 0,
                "parada_codigo": parada.codigo if parada else "",
                "parada_nombre": parada.nombre if parada else "",
                "fecha_ingreso": gi.fecha_ingreso,
                "fecha_salida": gi.fecha_salida,
                "activo": gi.activo,
            })

            if parada and parada.id not in seen_paradas:
                seen_paradas.add(parada.id)
                paradas_historial.append({
                    "parada_id": parada.id,
                    "parada_codigo": parada.codigo,
                    "parada_nombre": parada.nombre,
                    "grupo_codigo": grupo.codigo if grupo else "",
                    "grupo_nombre": grupo.nombre if grupo else "",
                    "lider_nombre": "",
                    "fecha_ingreso": gi.fecha_ingreso,
                })

        setattr(usuario, "historial_grupos", grupos)
        setattr(usuario, "historial_paradas", paradas_historial)
        return usuario

    def create(self, data: UsuarioCreate, creado_por_id: int | None = None) -> Usuario:
        existing = (
            self.db.query(Usuario)
            .filter(Usuario.dni == data.dni)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El DNI {data.dni} ya está registrado",
            )

        password_hash = hash_password(data.dni)
        usuario = Usuario(
            dni=data.dni,
            nombre=data.nombre,
            apellido=data.apellido,
            rol_id=data.rol_id,
            password_hash=password_hash,
            email=data.email,
            telefono=data.telefono,
            especialidad_id=data.especialidad_id,
            creado_por_id=creado_por_id,
        )
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario
