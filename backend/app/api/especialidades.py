from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..api.deps import RequirePermission, get_current_user
from ..core.database import get_db
from ..models.usuario import Usuario
from ..schemas.especialidad import EspecialidadCreate, EspecialidadResponse
from ..services.especialidad_service import EspecialidadService

router = APIRouter(prefix="/api/especialidades", tags=["especialidades"])


@router.get("/", response_model=list[EspecialidadResponse])
def list_especialidades(
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    service = EspecialidadService(db)
    return service.get_all()


@router.post("/", response_model=EspecialidadResponse, status_code=201)
def create_especialidad(
    data: EspecialidadCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(RequirePermission("ADMIN_USUARIOS")),
):
    service = EspecialidadService(db)
    return service.create(data.nombre, current_user.id)
