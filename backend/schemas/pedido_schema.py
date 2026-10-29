from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime

class PedidoCreate(BaseModel):
    id_funcionario: int
    valor_total: Decimal = Field(..., ge=0)
    status: str = "pendente"


class PedidoUpdate(BaseModel):
    id_funcionario: int
    valor_total: Decimal = Field(..., ge=0)
    status: str = "pendente"

class PedidoStatusUpdate(BaseModel):
    status: str


class ItemPedidoSimplesResponse(BaseModel):
    id_item_pedido: int
    id_produto: int
    quantidade: int
    subtotal: Decimal

    class Config:
        from_attributes = True


class PedidoResponse(BaseModel):
    id_nota_fiscal: int
    id_funcionario: int
    valor_total: Decimal 
    data_hora: datetime
    status: str
    itens: list[ItemPedidoSimplesResponse] = []

    class Config:
        from_attributes = True


class ItemPedidoCompletoCreate(BaseModel):
    id_produto: int
    quantidade: int = Field(..., gt=0)


class PedidoCompletoCreate(BaseModel):
    id_funcionario: int
    itens: list[ItemPedidoCompletoCreate] = Field(..., min_length=1)
