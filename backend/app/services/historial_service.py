from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from ..models.catalogo_material import CatalogoMaterial
from ..models.historial_movimiento import HistorialMovimiento
from ..schemas.historial import HistorialFilter


class HistorialService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        filters: HistorialFilter | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[HistorialMovimiento], int]:
        query = (
            self.db.query(HistorialMovimiento)
            .options(
                joinedload(HistorialMovimiento.catalogo),
                joinedload(HistorialMovimiento.parada),
                joinedload(HistorialMovimiento.grupo_destino),
                joinedload(HistorialMovimiento.usuario_ejecuta),
                joinedload(HistorialMovimiento.usuario_receptor),
            )
        )

        if filters:
            if filters.parada_id is not None:
                query = query.filter(HistorialMovimiento.parada_id == filters.parada_id)
            if filters.tipo is not None:
                query = query.filter(HistorialMovimiento.tipo_movimiento == filters.tipo)
            if filters.fecha_desde is not None:
                query = query.filter(HistorialMovimiento.timestamp >= filters.fecha_desde)
            if filters.fecha_hasta is not None:
                query = query.filter(HistorialMovimiento.timestamp <= filters.fecha_hasta)
            if filters.catalogo_id is not None:
                query = query.filter(HistorialMovimiento.catalogo_id == filters.catalogo_id)
            if filters.grupo_destino_id is not None:
                query = query.filter(
                    HistorialMovimiento.grupo_destino_id == filters.grupo_destino_id,
                )
            if filters.search:
                like = f"%{filters.search}%"
                query = query.join(
                    CatalogoMaterial,
                    HistorialMovimiento.catalogo_id == CatalogoMaterial.id,
                ).filter(
                    or_(
                        CatalogoMaterial.codigo_interno.ilike(like),
                        CatalogoMaterial.nombre.ilike(like),
                        HistorialMovimiento.observaciones.ilike(like),
                        HistorialMovimiento.observacion_entrega.ilike(like),
                        HistorialMovimiento.observacion_recepcion.ilike(like),
                    )
                )

        total = query.count()

        resultados = (
            query.order_by(HistorialMovimiento.timestamp.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return resultados, total

    def get_by_id(self, historial_id: str) -> HistorialMovimiento | None:
        return (
            self.db.query(HistorialMovimiento)
            .options(
                joinedload(HistorialMovimiento.catalogo),
                joinedload(HistorialMovimiento.parada),
                joinedload(HistorialMovimiento.grupo_destino),
                joinedload(HistorialMovimiento.usuario_ejecuta),
                joinedload(HistorialMovimiento.usuario_receptor),
            )
            .filter(HistorialMovimiento.id == historial_id)
            .first()
        )
