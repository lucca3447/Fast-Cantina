import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.database import Base
from core.security import decodificar_token
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
from services.demo_service import DemoService, DEMO_CNPJ, DEMO_ADMIN_LOGIN, DEMO_MANAGER_LOGIN, DEMO_OPERATOR_LOGIN


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_garantir_cantina_demo_e_autenticacao(db_session):
    service = DemoService(db_session)
    cantina = service.garantir_cantina_demo()

    assert cantina is not None
    assert cantina.cnpj == DEMO_CNPJ

    # Verifica se os produtos, estoque e pedidos foram criados
    produtos = db_session.query(Produto).filter(Produto.id_cantina == cantina.id_cantina).all()
    assert len(produtos) >= 8

    pedidos = db_session.query(Pedido).filter(Pedido.id_cantina == cantina.id_cantina).all()
    assert len(pedidos) >= 2

    # Autenticação de admin demo
    admin_tokens = service.autenticar_demo(perfil="admin")
    assert "access_token" in admin_tokens
    payload_admin = decodificar_token(admin_tokens["access_token"])
    assert payload_admin["perfil"] == "admin"
    assert payload_admin["id_cantina"] == cantina.id_cantina

    # Autenticação de gerente demo
    gerente_tokens = service.autenticar_demo(perfil="gerente")
    assert "access_token" in gerente_tokens
    payload_gerente = decodificar_token(gerente_tokens["access_token"])
    assert payload_gerente["perfil"] == "gerente"
    assert payload_gerente["id_cantina"] == cantina.id_cantina

    # Autenticação de atendente demo
    func_tokens = service.autenticar_demo(perfil="funcionario")
    assert "access_token" in func_tokens
    payload_func = decodificar_token(func_tokens["access_token"])
    assert payload_func["perfil"] == "funcionario"
    assert payload_func["id_cantina"] == cantina.id_cantina


def test_reset_demo_preserva_outros_tenants(db_session):
    # Cria uma cantina de cliente real
    cantina_real = Cantina(nome_fantasia="Cantina Real Escola", cnpj="99999999000199")
    db_session.add(cantina_real)
    db_session.flush()

    prod_real = Produto(nome="Pastel Real", preco=8.00, id_cantina=cantina_real.id_cantina)
    db_session.add(prod_real)
    db_session.commit()

    # Executa reset da demo
    service = DemoService(db_session)
    service.resetar_dados_demo()

    # O dado do tenant real deve continuar intacto
    prod_check = db_session.query(Produto).filter(Produto.id_produto == prod_real.id_produto).first()
    assert prod_check is not None
    assert prod_check.nome == "Pastel Real"
    assert prod_check.id_cantina == cantina_real.id_cantina
