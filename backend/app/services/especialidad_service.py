from sqlalchemy.orm import Session

from ..models.especialidad_tecnica import EspecialidadTecnica


class EspecialidadService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return self.db.query(EspecialidadTecnica).order_by(EspecialidadTecnica.nombre).all()

    def get_or_create(self, nombre: str) -> EspecialidadTecnica:
        nombre = nombre.strip().upper()
        existente = self.db.query(EspecialidadTecnica).filter(
            EspecialidadTecnica.nombre == nombre
        ).first()
        if existente:
            return existente
        nueva = EspecialidadTecnica(nombre=nombre)
        self.db.add(nueva)
        self.db.commit()
        self.db.refresh(nueva)
        return nueva

    def create(self, nombre: str, usuario_id: int) -> EspecialidadTecnica:
        nombre = nombre.strip().upper()
        existente = self.db.query(EspecialidadTecnica).filter(
            EspecialidadTecnica.nombre == nombre
        ).first()
        if existente:
            return existente
        nueva = EspecialidadTecnica(nombre=nombre, creado_por_id=usuario_id)
        self.db.add(nueva)
        self.db.commit()
        self.db.refresh(nueva)
        return nueva
