from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..models.inventario_fisico import InventarioFisico
from ..models.catalogo_material import CatalogoMaterial


class InventarioService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self, estado: str | None = None, ubicacion: str | None = None
    ) -> list[InventarioFisico]:
        query = self.db.query(InventarioFisico)
        if estado:
            query = query.filter(InventarioFisico.estado == estado)
        if ubicacion:
            query = query.filter(InventarioFisico.ubicacion_macro == ubicacion)
        return query.order_by(InventarioFisico.id).all()

    def get_by_id(self, inventario_id: int) -> InventarioFisico:
        unidad = (
            self.db.query(InventarioFisico)
            .filter(InventarioFisico.id == inventario_id)
            .first()
        )
        if not unidad:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unidad de inventario no encontrada",
            )
        return unidad

    def get_by_short_code(self, short_code: str) -> list[InventarioFisico]:
        pattern = f"%{short_code}%"
        return (
            self.db.query(InventarioFisico)
            .join(CatalogoMaterial)
            .filter(
                or_(
                    CatalogoMaterial.codigo_interno.ilike(pattern),
                    CatalogoMaterial.nombre.ilike(pattern),
                )
            )
            .order_by(InventarioFisico.id)
            .all()
        )

    def get_disponibles(self, catalogo_id: int) -> list[InventarioFisico]:
        return (
            self.db.query(InventarioFisico)
            .filter(
                InventarioFisico.catalogo_id == catalogo_id,
                InventarioFisico.estado == "Disponible",
                InventarioFisico.ubicacion_macro == "Mina",
            )
            .all()
        )

    def change_ubicacion(self, inventario_id: int, ubicacion_macro: str) -> InventarioFisico:
        unidad = self.get_by_id(inventario_id)
        ubicaciones_validas = ["Ciudad", "Transito_Compra", "Mina"]
        if ubicacion_macro not in ubicaciones_validas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ubicación inválida. Usar: {', '.join(ubicaciones_validas)}",
            )
        unidad.ubicacion_macro = ubicacion_macro
        self.db.commit()
        self.db.refresh(unidad)
        return unidad
