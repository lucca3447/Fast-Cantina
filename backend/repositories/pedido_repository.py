from sqlalchemy.orm import Session

from models.pedido_model import Pedido
from schemas.pedido_schema import PedidoCreate, PedidoUpdate, PedidoStatusUpdate


class PedidoRepository:
    def __init__(self, db: Session, id_cantina: int):
        self.db = db
        self.id_cantina = id_cantina

    def listar(self):
        return self.db.query(Pedido).filter(Pedido.id_cantina == self.id_cantina).all()

    def buscar_por_id(self, id_nota_fiscal: int):
        return self.db.query(Pedido).filter(
            Pedido.id_nota_fiscal == id_nota_fiscal,
            Pedido.id_cantina == self.id_cantina
        ).first()

    def buscar_por_funcionario(self, id_funcionario: int):
        return self.db.query(Pedido).filter(
            Pedido.id_funcionario == id_funcionario,
            Pedido.id_cantina == self.id_cantina
        ).all()

    def criar(self, pedido: PedidoCreate):
        novo_pedido = Pedido(
            id_funcionario=pedido.id_funcionario,
            valor_total=pedido.valor_total,
            status=pedido.status,
            id_cantina=self.id_cantina
        )

        self.db.add(novo_pedido)
        self.db.commit()
        self.db.refresh(novo_pedido)

        return novo_pedido

    def atualizar(self, pedido_existente: Pedido, pedido: PedidoUpdate):
        pedido_existente.id_funcionario = pedido.id_funcionario
        pedido_existente.valor_total = pedido.valor_total
        pedido_existente.status = pedido.status

        self.db.commit()
        self.db.refresh(pedido_existente)

        return pedido_existente

    def atualizar_status(self, pedido_existente: Pedido, pedido_status: PedidoStatusUpdate):
        pedido_existente.status = pedido_status.status

        self.db.commit()
        self.db.refresh(pedido_existente)

        return pedido_existente

    def deletar(self, pedido: Pedido):
        self.db.delete(pedido)
        self.db.commit()
