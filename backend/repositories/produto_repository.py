from sqlalchemy.orm import Session
from models.produto_model import Produto
from models.estoque_model import Estoque
from schemas.produto_schema import ProdutoCreate, ProdutoUpdate


class ProdutoRepository:
    def __init__(self, db: Session, id_cantina: int):
        self.db = db
        self.id_cantina = id_cantina

    def listar(self):
        return self.db.query(Produto).filter(Produto.id_cantina == self.id_cantina).all()

    def buscar_por_id(self, id_produto: int):
        return self.db.query(Produto).filter(
            Produto.id_produto == id_produto,
            Produto.id_cantina == self.id_cantina
        ).first()

    def buscar_por_nome(self, nome: str):
        return self.db.query(Produto).filter(
            Produto.nome == nome,
            Produto.id_cantina == self.id_cantina
        ).first()

    def criar(self, produto: ProdutoCreate):
        novo_produto = Produto(
            nome=produto.nome,
            preco=produto.preco,
            id_categoria=produto.id_categoria,
            exige_preparo=produto.exige_preparo,
            id_cantina=self.id_cantina
        )

        self.db.add(novo_produto)
        self.db.flush()

        novo_estoque = Estoque(
            id_produto=novo_produto.id_produto,
            quantidade_estoque=0
        )
        self.db.add(novo_estoque)

        self.db.commit()
        self.db.refresh(novo_produto)

        return novo_produto

    def atualizar(self, produto_existente: Produto, produto: ProdutoUpdate):
        produto_existente.nome = produto.nome
        produto_existente.preco = produto.preco
        produto_existente.id_categoria = produto.id_categoria
        produto_existente.exige_preparo = produto.exige_preparo

        self.db.commit()
        self.db.refresh(produto_existente)

        return produto_existente

    def deletar(self, produto: Produto):
        self.db.delete(produto)
        self.db.commit()
