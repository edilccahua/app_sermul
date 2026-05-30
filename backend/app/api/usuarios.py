from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..api.deps import get_current_user, RequirePermission
from ..models.usuario import Usuario
from ..schemas.usuario import (
    PasswordChangeRequest, UsuarioResponse,
    UsuarioCreate, UsuarioDetalleResponse,
)
from ..services.auth_service import AuthService
from ..services.usuario_service import UsuarioService

router = APIRouter()


@router.get("/buscar-dni", response_model=UsuarioResponse, dependencies=[Depends(RequirePermission("VER_INVENTARIO"))])
def buscar_por_dni(dni: str, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.dni == dni).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.get("/buscar", response_model=list[UsuarioResponse], dependencies=[Depends(RequirePermission("VER_INVENTARIO"))])
def buscar_usuarios(q: str, db: Session = Depends(get_db)):
    if not q or len(q.strip()) < 2:
        return []
    
    termino = f"%{q.strip()}%"
    usuarios = db.query(Usuario).filter(
        or_(
            Usuario.dni.ilike(termino),
            Usuario.nombre.ilike(termino),
            Usuario.apellido.ilike(termino)
        )
    ).limit(10).all()
    
    return usuarios


@router.get("/me", response_model=UsuarioResponse)
def get_my_profile(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    return current_user


@router.get("/", response_model=list[UsuarioResponse], dependencies=[Depends(RequirePermission("VER_INVENTARIO"))])
def list_usuarios(db: Session = Depends(get_db)):
    service = UsuarioService(db)
    return service.get_all()


@router.get("/{id}", response_model=UsuarioDetalleResponse, dependencies=[Depends(RequirePermission("VER_INVENTARIO"))])
def get_usuario(id: int, db: Session = Depends(get_db)):
    service = UsuarioService(db)
    return service.get_by_id(id)


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RequirePermission("ADMIN_USUARIOS"))])
def create_usuario(
    data: UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    service = UsuarioService(db)
    return service.create(data, creado_por_id=current_user.id)


@router.put("/{id}/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    id: int,
    data: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> None:
    if current_user.id != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes cambiar la contraseña de otro usuario",
        )
    service = AuthService(db)
    service.change_password(id, data.new_password)
