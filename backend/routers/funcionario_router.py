from core.auth_dependencies import get_current_user
from models.usuario_model import Usuario
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.auth_dependencies import require_roles
from core.database import get_db
from schemas.funcionario_schema import (
    FuncionarioCreate,
    FuncionarioResponse,
    FuncionarioUpdate
)
from services.funcionario_service import FuncionarioService


router = APIRouter(
    prefix="/funcionarios",
    tags=["Funcionarios"]
)


@router.post("/", response_model=FuncionarioResponse, status_code=201)
def criar_funcionario(
    funcionario: FuncionarioCreate,
    db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user),
    _: object = Depends(require_roles("admin"))
):
    service = FuncionarioService(db, current_user.id_cantina)
    return service.criar(funcionario)


@router.get("/", response_model=list[FuncionarioResponse])
def listar_funcionarios(
    db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user),
    _: object = Depends(require_roles("admin", "gerente", "funcionario"))
):
    service = FuncionarioService(db, current_user.id_cantina)
    return service.listar()


@router.get("/{id_funcionario}", response_model=FuncionarioResponse)
def buscar_funcionario(
    id_funcionario: int,
    db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user),
    _: object = Depends(require_roles("admin", "gerente"))
):
    service = FuncionarioService(db, current_user.id_cantina)
    return service.buscar_por_id(id_funcionario)


@router.put("/{id_funcionario}", response_model=FuncionarioResponse)
def atualizar_funcionario(
    id_funcionario: int,
    funcionario: FuncionarioUpdate,
    db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user),
    _: object = Depends(require_roles("admin"))
):
    service = FuncionarioService(db, current_user.id_cantina)
    return service.atualizar(id_funcionario, funcionario)


@router.delete("/{id_funcionario}")
def deletar_funcionario(
    id_funcionario: int,
    db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user),
    _: object = Depends(require_roles("admin"))
):
    service = FuncionarioService(db, current_user.id_cantina)
    return service.deletar(id_funcionario)
