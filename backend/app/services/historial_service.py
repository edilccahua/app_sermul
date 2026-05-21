
from sqlalchemy.orm import Session

from ..models.historial_movimiento import HistorialMovimiento
from ..schemas.historial import HistorialFilter


class HistorialService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, filters: HistorialFilter | None = None) -> list[HistorialMovimiento]:
        query = self.db.query(HistorialMovimiento)

        if filters:
            if filters.parada_id is not None:
                query = query.filter(HistorialMovimiento.parada_id == filters.parada_id)
            if filters.tipo is not None:
                query = query.filter(HistorialMovimiento.tipo_movimiento == filters.tipo)
            if filters.fecha_desde is not None:
                query = query.filter(HistorialMovimiento.timestamp >= filters.fecha_desde)
            if filters.fecha_hasta is not None:
                query = query.filter(HistorialMovimiento.timestamp <= filters.fecha_hasta)

        return query.order_by(HistorialMovimiento.timestamp.desc()).limit(500).all()
