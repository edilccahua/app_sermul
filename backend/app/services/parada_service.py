from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models.parada import Parada
from ..schemas.parada import ParadaCreate, ParadaUpdate


class ParadaService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Parada]:
        return (
            self.db.query(Parada)
            .order_by(Parada.fecha_inicio.desc())
            .all()
        )

    def get_by_id(self, parada_id: int) -> Parada:
        parada = (
            self.db.query(Parada)
            .filter(Parada.id == parada_id)
            .first()
        )
        if not parada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parada no encontrada",
            )
        return parada

    def create(self, data: ParadaCreate) -> Parada:
        existing = (
            self.db.query(Parada)
            .filter(Parada.codigo == data.codigo)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El código de parada ya existe",
            )
        parada = Parada(**data.model_dump())
        self.db.add(parada)
        self.db.commit()
        self.db.refresh(parada)
        return parada

    def update(self, parada_id: int, data: ParadaUpdate) -> Parada:
        parada = self.get_by_id(parada_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(parada, field, value)
        self.db.commit()
        self.db.refresh(parada)
        return parada
