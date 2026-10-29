from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from repositories.cantina_repository import CantinaRepository
from repositories.usuario_repository import UsuarioRepository
from schemas.cantina_schema import CantinaCreate
from core.security import gerar_hash_senha

class CantinaService:
    def __init__(self, db: Session):
        self.db = db
        self.cantina_repo = CantinaRepository(db)
        self.usuario_repo = UsuarioRepository(db)

    def registrar_cantina(self, payload: CantinaCreate):
        if self.cantina_repo.buscar_por_cnpj(payload.cnpj):
            raise HTTPException(status_code=400, detail="CNPJ ja cadastrado")
        if self.cantina_repo.buscar_por_nome_fantasia(payload.nome_fantasia):
            raise HTTPException(status_code=400, detail="Nome fantasia ja cadastrado")
        if self.usuario_repo.buscar_por_login(payload.admin.login):
            raise HTTPException(status_code=400, detail="Login de admin ja cadastrado")
        
        try:
            cantina = self.cantina_repo.criar(payload.nome_fantasia, payload.cnpj, commit=False)
            senha_hash = gerar_hash_senha(payload.admin.senha)
            payload.admin.perfil = "admin" # Força o primeiro usuário a ser admin
            admin = self.usuario_repo.criar(payload.admin, senha_hash, cantina.id_cantina, commit=False)
            self.db.commit()
            self.db.refresh(cantina)
            self.db.refresh(admin)
        except Exception:
            self.db.rollback()
            raise
        
        return {
            "cantina": cantina,
            "admin": admin,
            "mensagem": "Cantina e Administrador registrados com sucesso"
        }
