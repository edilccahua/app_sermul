from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..models.catalogo_material import CatalogoMaterial


class InventarioService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, tipo_material: str | None = None) -> list[CatalogoMaterial]:
        query = self.db.query(CatalogoMaterial).filter(CatalogoMaterial.activo.is_(True))
        if tipo_material:
            query = query.filter(CatalogoMaterial.tipo_material == tipo_material)
        return query.order_by(CatalogoMaterial.codigo_interno).all()

    def get_by_id(self, catalogo_id: int) -> CatalogoMaterial:
        material = (
            self.db.query(CatalogoMaterial)
            .filter(CatalogoMaterial.id == catalogo_id, CatalogoMaterial.activo.is_(True))
            .first()
        )
        if not material:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Material no encontrado",
            )
        return material

    def get_by_short_code(self, short_code: str) -> list[CatalogoMaterial]:
        pattern = f"%{short_code}%"
        return (
            self.db.query(CatalogoMaterial)
            .filter(
                CatalogoMaterial.activo.is_(True),
                or_(
                    CatalogoMaterial.codigo_interno.ilike(pattern),
                    CatalogoMaterial.nombre.ilike(pattern),
                ),
            )
            .order_by(CatalogoMaterial.codigo_interno)
            .all()
        )
