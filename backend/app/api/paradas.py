from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..api.deps import RequirePermission
from ..core.database import get_db
from ..models.usuario import Usuario
from ..schemas.grupo import GrupoConIntegrantesResponse
from ..schemas.parada import (
    CierreParadaResponse,
    ParadaCreate,
    ParadaResponse,
    ParadaUpdate,
    ResolverPendientesRequest,
)
from ..services.grupo_service import GrupoService
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


@router.get("/{parada_id}/grupos", response_model=list[GrupoConIntegrantesResponse], dependencies=[Depends(RequirePermission("VER_INVENTARIO"))])
def get_grupos_parada(
    parada_id: int,
    db: Session = Depends(get_db),
):
    service = GrupoService(db)
    return service.get_all(parada_id=parada_id)


@router.post("/", response_model=ParadaResponse, status_code=201)
def create_parada(
    data: ParadaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(RequirePermission("CREAR_PARADA")),
):
    service = ParadaService(db)
    return service.create(data, usuario_id=current_user.id)


@router.put("/{parada_id}", response_model=ParadaResponse)
def update_parada(
    parada_id: int,
    data: ParadaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(RequirePermission("CREAR_PARADA")),
):
    service = ParadaService(db)
    return service.update(parada_id, data, usuario_id=current_user.id)


@router.get("/{parada_id}/simular-cierre", response_model=CierreParadaResponse)
def simular_cierre_parada(
    parada_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(RequirePermission("CREAR_PARADA")),
):
    service = ParadaService(db)
    return service.simular_cierre(parada_id)


@router.put("/{parada_id}/resolver-pendiente")
def resolver_pendientes(
    parada_id: int,
    data: ResolverPendientesRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(RequirePermission("CREAR_PARADA")),
):
    service = ParadaService(db)
    return service.resolver_pendientes(parada_id, data.resoluciones, current_user.id)
