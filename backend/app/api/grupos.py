from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.usuario import Usuario
from ..schemas.grupo import GrupoResponse, GrupoConIntegrantesResponse, GrupoCreate, GrupoUpdate, IntegranteAddRequest
from ..schemas.excel import ExcelImportResponse
from ..services.grupo_service import GrupoService
from ..services.excel_import_service import ExcelImportService
from .deps import RequirePermission, get_current_user

router = APIRouter()


@router.get("/", response_model=list[GrupoConIntegrantesResponse], dependencies=[Depends(RequirePermission("VER_INVENTARIO"))])
def get_grupos(
    parada_id: int | None = None,
    usuario_id: int | None = None,
    db: Session = Depends(get_db),
):
    service = GrupoService(db)
    return service.get_all(parada_id, usuario_id)


@router.get("/{id}", response_model=GrupoConIntegrantesResponse, dependencies=[Depends(RequirePermission("VER_INVENTARIO"))])
def get_grupo(id: int, db: Session = Depends(get_db)):
    service = GrupoService(db)
    return service.get_by_id(id)


@router.post("/", response_model=GrupoResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RequirePermission("GESTIONAR_GRUPOS"))])
def create_grupo(
    data: GrupoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    service = GrupoService(db)
    return service.create(data, usuario_id=current_user.id)


@router.put("/{id}", response_model=GrupoResponse, dependencies=[Depends(RequirePermission("GESTIONAR_GRUPOS"))])
def update_grupo(
    id: int,
    data: GrupoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    service = GrupoService(db)
    return service.update(id, data, usuario_id=current_user.id)


@router.post("/importar-excel", response_model=ExcelImportResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RequirePermission("GESTIONAR_GRUPOS"))])
async def importar_excel(file: UploadFile = File(...), parada_id: int = Form(...), db: Session = Depends(get_db)):
    service = ExcelImportService(db)
    content = await file.read()
    return service.importar_excel(content, parada_id)


@router.post("/{id}/integrantes", dependencies=[Depends(RequirePermission("GESTIONAR_GRUPOS"))])
def add_integrante(
    id: int,
    data: IntegranteAddRequest,
    db: Session = Depends(get_db),
):
    service = GrupoService(db)
    resultado = service.add_integrante(id, data.usuario_id, es_lider_frente=data.es_lider_frente)
    return {
        "grupo_id": resultado.grupo_id,
        "usuario_id": resultado.usuario_id,
        "es_lider_frente": resultado.es_lider_frente,
        "fecha_ingreso": resultado.fecha_ingreso.isoformat(),
        "fecha_salida": None,
        "activo": resultado.activo,
    }


@router.patch("/{id}/integrantes/{usuario_id}/desactivar", dependencies=[Depends(RequirePermission("GESTIONAR_GRUPOS"))])
def remove_integrante(
    id: int,
    usuario_id: int,
    forzar_perdida: bool = Query(False),
    db: Session = Depends(get_db),
):
    service = GrupoService(db)
    return service.remove_integrante(id, usuario_id, forzar_perdida)


@router.get("/{grupo_id}/integrantes/{usuario_id}/herramientas-en-uso", dependencies=[Depends(RequirePermission("VER_INVENTARIO"))])
def get_herramientas_en_uso_integrante(
    grupo_id: int,
    usuario_id: int,
    db: Session = Depends(get_db),
):
    service = GrupoService(db)
    return service.get_herramientas_en_uso_integrante(grupo_id, usuario_id)


@router.get("/{id}/herramientas-en-uso", dependencies=[Depends(RequirePermission("VER_INVENTARIO"))])
def get_herramientas_en_uso_grupo(
    id: int,
    db: Session = Depends(get_db),
):
    service = GrupoService(db)
    return service.get_herramientas_en_uso_grupo(id)
