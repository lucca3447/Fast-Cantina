from sqlalchemy.orm import Session

from models.usuario_model import Usuario
from schemas.usuario_schema import UsuarioCreate, UsuarioUpdate


class UsuarioRepository:
    def __init__(self, db: Session, id_cantina: int | None = None):
        self.db = db
        self.id_cantina = id_cantina

    def listar(self):
        query = self.db.query(Usuario)
        if self.id_cantina is not None:
            query = query.filter(Usuario.id_cantina == self.id_cantina)
        return query.all()

    def buscar_por_id(self, id_usuario: int):
        query = self.db.query(Usuario).filter(Usuario.id_usuario == id_usuario)
        if self.id_cantina is not None:
            query = query.filter(Usuario.id_cantina == self.id_cantina)
        return query.first()

    def buscar_por_login(self, login: str):
        query = self.db.query(Usuario).filter(Usuario.login == login)
        if self.id_cantina is not None:
            query = query.filter(Usuario.id_cantina == self.id_cantina)
        return query.first()

    def criar(self, usuario: UsuarioCreate, senha_hash: str, id_cantina: int | None = None, commit: bool = True):
        cantina_id = id_cantina or self.id_cantina
        if cantina_id is None:
            raise ValueError("id_cantina obrigatorio para criar usuario")
        
        novo_usuario = Usuario(
            nome=usuario.nome,
            login=usuario.login,
            senha_hash=senha_hash,
            perfil=usuario.perfil,
            ativo=usuario.ativo,
            id_cantina=cantina_id,
        )
        self.db.add(novo_usuario)
        if commit:
            self.db.commit()
            self.db.refresh(novo_usuario)
        else:
            self.db.flush()
        return novo_usuario

    def atualizar(self, usuario_db: Usuario, usuario: UsuarioUpdate, senha_hash: str | None = None):
        if usuario.nome is not None:
            usuario_db.nome = usuario.nome
        if usuario.login is not None:
            usuario_db.login = usuario.login
        if usuario.perfil is not None:
            usuario_db.perfil = usuario.perfil
        if usuario.ativo is not None:
            usuario_db.ativo = usuario.ativo
        if senha_hash:
            usuario_db.senha_hash = senha_hash

        self.db.commit()
        self.db.refresh(usuario_db)
        return usuario_db

    def deletar(self, usuario: Usuario):
        self.db.delete(usuario)
        self.db.commit()

    def existe_admin(self) -> bool:
        query = self.db.query(Usuario).filter(Usuario.perfil == "admin")
        if self.id_cantina is not None:
            query = query.filter(Usuario.id_cantina == self.id_cantina)
        return query.first() is not None
