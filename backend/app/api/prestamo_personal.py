from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..api.deps import RequirePermission
from ..core.database import get_db
from ..models.usuario import Usuario
from ..schemas.prestamo_personal import (
    DevolucionPersonalRequest,
    HerramientaPrestadaResponse,
    PrestamoPersonalRequest,
    PrestamoPersonalResponse,
)
from ..services.prestamo_personal_service import PrestamoPersonalService

router = APIRouter()


@router.post("/salida", response_model=PrestamoPersonalResponse)
def prestamo_salida(
    request: PrestamoPersonalRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(RequirePermission("CHECK_OUT")),
):
    service = PrestamoPersonalService(db)
    try:
        return service.prestar(request, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/entrada", response_model=PrestamoPersonalResponse)
def prestamo_entrada(
    request: DevolucionPersonalRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(RequirePermission("CHECK_IN")),
):
    service = PrestamoPersonalService(db)
    try:
        return service.devolver(request, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/usuario/{usuario_id}/herramientas", response_model=list[HerramientaPrestadaResponse])
def herramientas_prestadas(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(RequirePermission("VER_INVENTARIO")),
):
    service = PrestamoPersonalService(db)
    return service.herramientas_por_usuario(usuario_id)
