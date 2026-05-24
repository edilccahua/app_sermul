from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..api.deps import RequirePermission
from ..core.database import get_db
from ..models.usuario import Usuario
from ..schemas.check import CheckOutRequest, CheckInRequest, CheckResponse
from ..services.check_in_out_service import CheckInOutService

router = APIRouter()


@router.post("/check-out", response_model=CheckResponse)
def check_out(
    request: CheckOutRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(RequirePermission("CHECK_OUT")),
):
    service = CheckInOutService(db)
    try:
        return service.check_out(
            catalogo_id=request.catalogo_id,
            cantidad=request.cantidad,
            grupo_id=request.grupo_id,
            parada_id=request.parada_id,
            usuario_id=current_user.id,
            observacion_entrega=request.observacion_entrega,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/check-in", response_model=CheckResponse)
def check_in(
    request: CheckInRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(RequirePermission("CHECK_IN")),
):
    if request.cant_buen_estado + request.cant_malograda == 0:
        raise HTTPException(status_code=400, detail="Debe devolver al menos una unidad")
    if request.cant_malograda > 0 and not request.descripcion_dano:
        raise HTTPException(status_code=400, detail="Describa el daño de las unidades malogradas")

    service = CheckInOutService(db)
    try:
        return service.check_in(
            catalogo_id=request.catalogo_id,
            cant_buen_estado=request.cant_buen_estado,
            cant_malograda=request.cant_malograda,
            usuario_id=current_user.id,
            observacion_recepcion=request.observacion_recepcion,
            descripcion_dano=request.descripcion_dano,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
