from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..api.deps import RequirePermission
from ..core.database import get_db
from ..models.usuario import Usuario
from ..schemas.parada import ParadaCreate, ParadaResponse, ParadaUpdate
from ..services.parada_service import ParadaService

router = APIRouter()


@router.get("/", response_model=list[ParadaResponse])
def list_paradas(
    db: Session = Depends(get_db),
    _: Usuario = Depends(RequirePermission("VER_INVENTARIO")),
):
    service = ParadaService(db)
    return service.get_all()


@router.get("/{parada_id}", response_model=ParadaResponse)
def get_parada(
    parada_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(RequirePermission("VER_INVENTARIO")),
):
    service = ParadaService(db)
    return service.get_by_id(parada_id)


@router.post("/", response_model=ParadaResponse, status_code=201)
def create_parada(
    data: ParadaCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(RequirePermission("CREAR_PARADA")),
):
    service = ParadaService(db)
    return service.create(data)


@router.put("/{parada_id}", response_model=ParadaResponse)
def update_parada(
    parada_id: int,
    data: ParadaUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(RequirePermission("CREAR_PARADA")),
):
    service = ParadaService(db)
    return service.update(parada_id, data)
