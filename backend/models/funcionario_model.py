from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from core.database import Base


class Funcionario(Base):
    __tablename__ = "funcionarios"

    id_funcionario = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    cargo = Column(String(50), nullable=False)
    id_cantina = Column(Integer, ForeignKey("cantinas.id_cantina"), nullable=False)

    pedidos = relationship("Pedido", back_populates="funcionario")
