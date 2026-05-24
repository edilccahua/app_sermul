from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..schemas.dashboard import DashboardResidenteResponse
from ..services.dashboard_service import DashboardService
from .deps import RequirePermission

router = APIRouter()

@router.get("/residente", response_model=DashboardResidenteResponse, dependencies=[Depends(RequirePermission("VER_DASHBOARD_COMPLETO"))])
def get_dashboard_residente(db: Session = Depends(get_db)):
    service = DashboardService(db)
    return service.get_residente_kpis()
