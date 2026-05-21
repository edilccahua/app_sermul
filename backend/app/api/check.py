from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..api.deps import RequirePermission
from ..core.database import get_db
from ..models.usuario import Usuario
from ..schemas.check import CheckInRequest, CheckOutRequest, CheckResponse
from ..services.check_in_out_service import CheckInOutService

router = APIRouter()


@router.post("/check-out", response_model=CheckResponse)
def check_out(
    body: CheckOutRequest,
    usuario: Usuario = Depends(RequirePermission("CHECK_OUT")),
    db: Session = Depends(get_db),
):  # type: ignore[return-value]
    service = CheckInOutService(db)
    movimiento, unidad = service.check_out(
        short_code=body.short_code,
        grupo_id=body.grupo_id,
        parada_id=body.parada_id,
        usuario_id=usuario.id,
    )
    return CheckResponse(movimiento=movimiento, unidad=unidad)  # type: ignore[arg-type]


@router.post("/check-in", response_model=CheckResponse)
def check_in(
    body: CheckInRequest,
    usuario: Usuario = Depends(RequirePermission("CHECK_IN")),
    db: Session = Depends(get_db),
):  # type: ignore[return-value]
    service = CheckInOutService(db)
    movimiento, unidad = service.check_in(
        inventario_id=body.inventario_id,
        buen_estado=body.buen_estado,
        usuario_id=usuario.id,
        dano=body.dano,
    )
    return CheckResponse(movimiento=movimiento, unidad=unidad)  # type: ignore[arg-type]
