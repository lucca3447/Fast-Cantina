from sqlalchemy.orm import Session

from models.funcionario_model import Funcionario
from schemas.funcionario_schema import FuncionarioCreate, FuncionarioUpdate


class FuncionarioRepository:
    def __init__(self, db: Session, id_cantina: int):
        self.db = db
        self.id_cantina = id_cantina

    def listar(self):
        return self.db.query(Funcionario).filter(Funcionario.id_cantina == self.id_cantina).all()

    def buscar_por_id(self, id_funcionario: int):
        return self.db.query(Funcionario).filter(
            Funcionario.id_funcionario == id_funcionario,
            Funcionario.id_cantina == self.id_cantina
        ).first()

    def buscar_por_nome(self, nome: str):
        return self.db.query(Funcionario).filter(
            Funcionario.nome == nome,
            Funcionario.id_cantina == self.id_cantina
        ).first()

    def criar(self, funcionario: FuncionarioCreate):
        novo_funcionario = Funcionario(
            nome=funcionario.nome,
            cargo=funcionario.cargo,
            id_cantina=self.id_cantina
        )

        self.db.add(novo_funcionario)
        self.db.commit()
        self.db.refresh(novo_funcionario)

        return novo_funcionario

    def atualizar(self, funcionario_existente: Funcionario, funcionario: FuncionarioUpdate):
        funcionario_existente.nome = funcionario.nome
        funcionario_existente.cargo = funcionario.cargo

        self.db.commit()
        self.db.refresh(funcionario_existente)

        return funcionario_existente

    def deletar(self, funcionario: Funcionario):
        self.db.delete(funcionario)
        self.db.commit()
