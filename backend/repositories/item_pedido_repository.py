from sqlalchemy.orm import Session

from models.item_pedido_model import ItemPedido
from models.pedido_model import Pedido
from schemas.item_pedido_schema import ItemPedidoCreate, ItemPedidoUpdate


class ItemPedidoRepository:
    def __init__(self, db: Session, id_cantina: int):
        self.db = db
        self.id_cantina = id_cantina

    def listar(self):
        return self.db.query(ItemPedido).join(ItemPedido.pedido).filter(Pedido.id_cantina == self.id_cantina).all()

    def buscar_por_id(self, id_item_pedido: int):
        return self.db.query(ItemPedido).join(ItemPedido.pedido).filter(
            ItemPedido.id_item_pedido == id_item_pedido,
            Pedido.id_cantina == self.id_cantina
        ).first()

    def buscar_por_pedido(self, id_nota_fiscal: int):
        return self.db.query(ItemPedido).join(ItemPedido.pedido).filter(
            ItemPedido.id_nota_fiscal == id_nota_fiscal,
            Pedido.id_cantina == self.id_cantina
        ).all()

    def criar(self, item_pedido: ItemPedidoCreate):
        novo_item_pedido = ItemPedido(
            quantidade=item_pedido.quantidade,
            subtotal=item_pedido.subtotal,
            id_produto=item_pedido.id_produto,
            id_nota_fiscal=item_pedido.id_nota_fiscal
        )

        self.db.add(novo_item_pedido)
        self.db.commit()
        self.db.refresh(novo_item_pedido)

        return novo_item_pedido

    def atualizar(self, item_pedido_existente: ItemPedido, item_pedido: ItemPedidoUpdate):
        item_pedido_existente.quantidade = item_pedido.quantidade
        item_pedido_existente.subtotal = item_pedido.subtotal
        item_pedido_existente.id_produto = item_pedido.id_produto
        item_pedido_existente.id_nota_fiscal = item_pedido.id_nota_fiscal

        self.db.commit()
        self.db.refresh(item_pedido_existente)

        return item_pedido_existente

    def deletar(self, item_pedido: ItemPedido):
        self.db.delete(item_pedido)
        self.db.commit()
