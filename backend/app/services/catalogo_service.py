from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models.catalogo_material import CatalogoMaterial
from ..models.categoria_material import CategoriaMaterial
from ..schemas.catalogo import CatalogoCreate, CatalogoUpdate


class CatalogoService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[CatalogoMaterial]:
        return (
            self.db.query(CatalogoMaterial)
            .filter(CatalogoMaterial.activo.is_(True))
            .order_by(CatalogoMaterial.codigo_interno)
            .all()
        )

    def get_by_id(self, catalogo_id: int) -> CatalogoMaterial:
        catalogo = (
            self.db.query(CatalogoMaterial)
            .filter(CatalogoMaterial.id == catalogo_id)
            .first()
        )
        if not catalogo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Material de catálogo no encontrado",
            )
        return catalogo

    def create(self, data: CatalogoCreate) -> CatalogoMaterial:
        existing = (
            self.db.query(CatalogoMaterial)
            .filter(CatalogoMaterial.codigo_interno == data.codigo_interno)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El código interno ya existe",
            )
        categoria = (
            self.db.query(CategoriaMaterial)
            .filter(CategoriaMaterial.id == data.categoria_id)
            .first()
        )
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada",
            )
        catalogo = CatalogoMaterial(**data.model_dump())
        self.db.add(catalogo)
        self.db.commit()
        self.db.refresh(catalogo)
        return catalogo

    def update(self, catalogo_id: int, data: CatalogoUpdate) -> CatalogoMaterial:
        catalogo = self.get_by_id(catalogo_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(catalogo, field, value)
        self.db.commit()
        self.db.refresh(catalogo)
        return catalogo

    def search(self, term: str) -> list[CatalogoMaterial]:
        return (
            self.db.query(CatalogoMaterial)
            .filter(
                CatalogoMaterial.activo.is_(True),
                CatalogoMaterial.nombre.ilike(f"%{term}%"),
            )
            .order_by(CatalogoMaterial.codigo_interno)
            .all()
        )
