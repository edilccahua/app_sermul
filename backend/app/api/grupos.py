from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..schemas.grupo import GrupoResponse, GrupoConIntegrantesResponse, GrupoCreate, GrupoUpdate, IntegranteAddRequest
from ..schemas.excel import ExcelImportResponse
from ..services.grupo_service import GrupoService
from ..services.excel_import_service import ExcelImportService
from .deps import RequirePermission

router = APIRouter()

@router.get("/", response_model=list[GrupoResponse], dependencies=[Depends(RequirePermission("VER_INVENTARIO"))])
def get_grupos(parada_id: int | None = None, estado: str | None = None, db: Session = Depends(get_db)):
    service = GrupoService(db)
    return service.get_all(parada_id, estado)

@router.get("/{id}", response_model=GrupoConIntegrantesResponse, dependencies=[Depends(RequirePermission("VER_INVENTARIO"))])
def get_grupo(id: int, db: Session = Depends(get_db)):
    service = GrupoService(db)
    return service.get_by_id(id)

@router.post("/", response_model=GrupoResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RequirePermission("GESTIONAR_GRUPOS"))])
def create_grupo(data: GrupoCreate, db: Session = Depends(get_db)):
    service = GrupoService(db)
    return service.create(data)

@router.put("/{id}", response_model=GrupoResponse, dependencies=[Depends(RequirePermission("GESTIONAR_GRUPOS"))])
def update_grupo(id: int, data: GrupoUpdate, db: Session = Depends(get_db)):
    service = GrupoService(db)
    return service.update(id, data)

@router.post("/importar-excel", response_model=ExcelImportResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RequirePermission("GESTIONAR_GRUPOS"))])
async def importar_excel(file: UploadFile = File(...), parada_id: int = Form(...), db: Session = Depends(get_db)):
    service = ExcelImportService(db)
    content = await file.read()
    return service.importar_excel(content, parada_id)

@router.post("/{id}/integrantes", dependencies=[Depends(RequirePermission("GESTIONAR_GRUPOS"))])
def add_integrante(id: int, data: IntegranteAddRequest, db: Session = Depends(get_db)):
    service = GrupoService(db)
    service.add_integrante(id, data.usuario_id)
    return {"ok": True}

@router.delete("/{id}/integrantes/{usuario_id}", dependencies=[Depends(RequirePermission("GESTIONAR_GRUPOS"))])
def remove_integrante(id: int, usuario_id: int, db: Session = Depends(get_db)):
    service = GrupoService(db)
    service.remove_integrante(id, usuario_id)
    return {"ok": True}
