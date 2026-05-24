from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..schemas.reserva import ReservaResponse, ReservaCreate, RechazarReservaRequest, DespacharReservaRequest
from ..services.reserva_service import ReservaService
from .deps import RequirePermission, get_current_user

router = APIRouter()

@router.get("/", response_model=list[ReservaResponse], dependencies=[Depends(RequirePermission("VER_INVENTARIO"))])
def get_reservas(grupo_id: int | None = None, estado: str | None = None, parada_id: int | None = None, db: Session = Depends(get_db)):
    service = ReservaService(db)
    return service.get_all(grupo_id, estado, parada_id)

@router.get("/{id}", response_model=ReservaResponse, dependencies=[Depends(RequirePermission("VER_INVENTARIO"))])
def get_reserva(id: int, db: Session = Depends(get_db)):
    service = ReservaService(db)
    return service.get_by_id(id)

@router.post("/", response_model=ReservaResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RequirePermission("CREAR_RESERVA"))])
def create_reserva(data: ReservaCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    service = ReservaService(db)
    return service.create(data, current_user.id)

@router.post("/{id}/aprobar", response_model=ReservaResponse, dependencies=[Depends(RequirePermission("APROBAR_RESERVA"))])
def aprobar_reserva(id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    service = ReservaService(db)
    return service.aprobar(id, current_user.id)

@router.post("/{id}/rechazar", response_model=ReservaResponse, dependencies=[Depends(RequirePermission("APROBAR_RESERVA"))])
def rechazar_reserva(id: int, request: RechazarReservaRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    service = ReservaService(db)
    return service.rechazar(id, current_user.id, request.motivo)

@router.post("/{id}/despachar", response_model=ReservaResponse, dependencies=[Depends(RequirePermission("CHECK_OUT"))])
def despachar_reserva(id: int, request: DespacharReservaRequest | None = None, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    service = ReservaService(db)
    items_ids = request.items_ids if request else None
    return service.despachar(id, current_user.id, items_ids)
