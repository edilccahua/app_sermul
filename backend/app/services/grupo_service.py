from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..models import GrupoTrabajo, GrupoIntegrante
from ..schemas.grupo import GrupoCreate, GrupoUpdate

class GrupoService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, parada_id: int | None = None, estado: str | None = None):
        query = self.db.query(GrupoTrabajo)
        if parada_id:
            query = query.filter(GrupoTrabajo.parada_id == parada_id)
        if estado:
            query = query.filter(GrupoTrabajo.estado == estado)
        return query.all()

    def get_by_id(self, grupo_id: int):
        grupo = self.db.query(GrupoTrabajo).filter(GrupoTrabajo.id == grupo_id).first()
        if not grupo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo no encontrado")
        
        integrantes = self.db.query(GrupoIntegrante).filter(
            GrupoIntegrante.grupo_id == grupo_id,
            GrupoIntegrante.activo
        ).all()
        
        setattr(grupo, "integrantes", integrantes)
        return grupo

    def create(self, data: GrupoCreate):
        nuevo_grupo = GrupoTrabajo(
            codigo=data.codigo,
            nombre=data.nombre,
            parada_id=data.parada_id,
            lider_id=data.lider_id,
            supervisor_id=data.supervisor_id
        )
        self.db.add(nuevo_grupo)
        self.db.commit()
        self.db.refresh(nuevo_grupo)
        return nuevo_grupo

    def update(self, grupo_id: int, data: GrupoUpdate):
        grupo = self.db.query(GrupoTrabajo).filter(GrupoTrabajo.id == grupo_id).first()
        if not grupo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo no encontrado")
        
        if data.nombre is not None:
            grupo.nombre = data.nombre
        if data.estado is not None:
            grupo.estado = data.estado
        if data.lider_id is not None:
            grupo.lider_id = data.lider_id
        if data.supervisor_id is not None:
            grupo.supervisor_id = data.supervisor_id
            
        self.db.commit()
        self.db.refresh(grupo)
        return grupo

    def add_integrante(self, grupo_id: int, usuario_id: int):
        grupo = self.db.query(GrupoTrabajo).filter(GrupoTrabajo.id == grupo_id).first()
        if not grupo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo no encontrado")
        
        existente = self.db.query(GrupoIntegrante).filter(
            GrupoIntegrante.grupo_id == grupo_id,
            GrupoIntegrante.usuario_id == usuario_id,
            GrupoIntegrante.activo
        ).first()
        
        if existente:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario ya es integrante activo")
            
        otros_activos = self.db.query(GrupoIntegrante).filter(
            GrupoIntegrante.usuario_id == usuario_id,
            GrupoIntegrante.activo,
            GrupoIntegrante.grupo_id != grupo_id
        ).all()
        for otro in otros_activos:
            otro.activo = False
            
        nuevo_integrante = GrupoIntegrante(
            grupo_id=grupo_id,
            usuario_id=usuario_id,
            activo=True
        )
        self.db.add(nuevo_integrante)
        self.db.commit()
        return True

    def remove_integrante(self, grupo_id: int, usuario_id: int):
        integrante = self.db.query(GrupoIntegrante).filter(
            GrupoIntegrante.grupo_id == grupo_id,
            GrupoIntegrante.usuario_id == usuario_id,
            GrupoIntegrante.activo
        ).first()
        
        if not integrante:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integrante no encontrado")
            
        integrante.activo = False
        self.db.commit()
        return True
