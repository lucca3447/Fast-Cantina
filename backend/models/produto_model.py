from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from core.database import Base


class Produto(Base):
    __tablename__ = "produtos"
    __table_args__ = (
        UniqueConstraint("nome", "id_cantina", name="uq_produtos_nome_cantina"),
    )

    id_produto = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    preco = Column(Numeric(10,2), nullable=False) #Diferente de como foi feito no modelo logico, numeric(decimal no sql) é mais adequado do que float para valores monetários 
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria"))
    exige_preparo = Column(Boolean, default=False, nullable=False)
    id_cantina = Column(Integer, ForeignKey("cantinas.id_cantina"), nullable=False)
    categoria = relationship("Categoria", back_populates="produtos")
    itens_pedido = relationship("ItemPedido", back_populates="produto", cascade="all, delete-orphan")
    estoque = relationship("Estoque", back_populates="produto", uselist=False, cascade="all, delete-orphan")
    fornecedor_produtos = relationship("FornecedorProduto", back_populates="produto", cascade="all, delete-orphan")
