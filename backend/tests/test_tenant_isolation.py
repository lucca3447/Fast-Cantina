import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decimal import Decimal

from core.database import Base
from models.cantina_model import Cantina
from models.categoria_model import Categoria
from models.estoque_model import Estoque
from models.fornecedor_model import Fornecedor
from models.fornecedor_produto_model import FornecedorProduto
from models.funcionario_model import Funcionario
from models.item_pedido_model import ItemPedido
from models.pedido_model import Pedido
from models.produto_model import Produto
from models.refresh_token_model import RefreshToken
from models.usuario_model import Usuario

from repositories.pedido_repository import PedidoRepository
from repositories.produto_repository import ProdutoRepository
from repositories.cantina_repository import CantinaRepository
from repositories.usuario_repository import UsuarioRepository
from schemas.pedido_schema import PedidoCreate
from schemas.produto_schema import ProdutoCreate
from schemas.usuario_schema import UsuarioCreate
from services.cantina_service import CantinaService
from schemas.cantina_schema import CantinaCreate
from fastapi import HTTPException


@pytest.fixture
def db_session():
    # In-memory SQLite for fast, isolated testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_pedido_repository_tenant_isolation(db_session):
    # Setup two cantinas
    cantina1 = Cantina(id_cantina=1, nome_fantasia="Cantina Alpha", cnpj="11.111.111/0001-11")
    cantina2 = Cantina(id_cantina=2, nome_fantasia="Cantina Beta", cnpj="22.222.222/0001-22")
    db_session.add_all([cantina1, cantina2])

    func1 = Funcionario(id_funcionario=1, nome="Funcionario 1", cargo="Atendente", id_cantina=1)
    func2 = Funcionario(id_funcionario=2, nome="Funcionario 2", cargo="Atendente", id_cantina=2)
    db_session.add_all([func1, func2])
    db_session.commit()

    # Create an order in Cantina 2
    repo2 = PedidoRepository(db_session, id_cantina=2)
    pedido2 = repo2.criar(PedidoCreate(id_funcionario=2, valor_total=Decimal("50.00"), status="pendente"))

    # Cantina 1 MUST NOT be able to find Cantina 2's order (IDOR protection)
    repo1 = PedidoRepository(db_session, id_cantina=1)
    assert repo1.buscar_por_id(pedido2.id_nota_fiscal) is None

    # Cantina 2 CAN find its own order
    pedido_encontrado = repo2.buscar_por_id(pedido2.id_nota_fiscal)
    assert pedido_encontrado is not None
    assert pedido_encontrado.id_nota_fiscal == pedido2.id_nota_fiscal


def test_produto_criacao_inicializa_estoque(db_session):
    cantina = Cantina(id_cantina=1, nome_fantasia="Cantina Teste", cnpj="12.345.678/0001-90")
    cat = Categoria(id_categoria=1, descricao="Lanches", id_cantina=1)
    db_session.add_all([cantina, cat])
    db_session.commit()

    repo = ProdutoRepository(db_session, id_cantina=1)
    novo_produto = repo.criar(ProdutoCreate(
        nome="Pão de Queijo",
        preco=Decimal("6.50"),
        id_categoria=1,
        exige_preparo=False
    ))

    # Verify estoque was automatically initialized with 0
    estoque = db_session.query(Estoque).filter(Estoque.id_produto == novo_produto.id_produto).first()
    assert estoque is not None
    assert estoque.quantidade_estoque == 0


def test_registro_cantina_atomico_e_validacoes(db_session):
    service = CantinaService(db_session)

    payload = CantinaCreate(
        nome_fantasia="Cantina Sucesso",
        cnpj="99.999.999/0001-99",
        admin=UsuarioCreate(
            nome="Admin Teste",
            login="admin@cantina.com",
            senha="SenhaForte123!",
            perfil="admin"
        )
    )

    res = service.registrar_cantina(payload)
    assert res["cantina"].id_cantina is not None
    assert res["admin"].id_usuario is not None

    # Tentar cadastrar novamente com mesmo CNPJ deve falhar com HTTPException 400
    with pytest.raises(HTTPException) as exc_info:
        service.registrar_cantina(payload)
    assert exc_info.value.status_code == 400
    assert "CNPJ ja cadastrado" in exc_info.value.detail
