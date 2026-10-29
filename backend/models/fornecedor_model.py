from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from core.database import Base


class Fornecedor(Base):
    __tablename__ = "fornecedores"
    __table_args__ = (
        UniqueConstraint("cnpj", "id_cantina", name="uq_fornecedores_cnpj_cantina"),
    )

    id_fornecedor = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    telefone = Column(String(20), nullable=False)
    cnpj = Column(String(18), nullable=False)
    id_cantina = Column(Integer, ForeignKey("cantinas.id_cantina"), nullable=False)

    fornecedor_produtos = relationship("FornecedorProduto", back_populates="fornecedor", cascade="all, delete-orphan")
