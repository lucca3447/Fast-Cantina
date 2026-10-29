from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from core.database import Base


class Categoria(Base):
    __tablename__ = "categorias"
    __table_args__ = (
        UniqueConstraint("descricao", "id_cantina", name="uq_categorias_descricao_cantina"),
    )

    id_categoria = Column(Integer, primary_key=True, index=True)
    descricao = Column(String(100), nullable=False)
    id_cantina = Column(Integer, ForeignKey("cantinas.id_cantina"), nullable=False)
    produtos = relationship("Produto", back_populates="categoria")
