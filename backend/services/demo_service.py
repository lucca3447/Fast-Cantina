from decimal import Decimal
from typing import Literal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from core.security import gerar_hash_senha
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
from services.auth_service import AuthService

DEMO_CNPJ = "00000000000100"
DEMO_CANTINA_NOME = "Cantina Modelo (Demo)"
DEMO_ADMIN_LOGIN = "admin@fastcantina.com"
DEMO_MANAGER_LOGIN = "gerente@fastcantina.com"
DEMO_OPERATOR_LOGIN = "atendente@fastcantina.com"
DEMO_PASSWORD = "password"


class DemoService:
    def __init__(self, db: Session):
        self.db = db

    def garantir_cantina_demo(self) -> Cantina:
        cantina = self.db.query(Cantina).filter(Cantina.cnpj == DEMO_CNPJ).first()
        admin = self.db.query(Usuario).filter(Usuario.login == DEMO_ADMIN_LOGIN).first()
        gerente = self.db.query(Usuario).filter(Usuario.login == DEMO_MANAGER_LOGIN).first()
        operador = self.db.query(Usuario).filter(Usuario.login == DEMO_OPERATOR_LOGIN).first()

        if not cantina or not admin or not gerente or not operador:
            self.resetar_dados_demo()
            cantina = self.db.query(Cantina).filter(Cantina.cnpj == DEMO_CNPJ).first()

        return cantina

    def autenticar_demo(self, perfil: Literal["admin", "gerente", "funcionario"] = "admin"):
        self.garantir_cantina_demo()
        login_map = {
            "admin": DEMO_ADMIN_LOGIN,
            "gerente": DEMO_MANAGER_LOGIN,
            "funcionario": DEMO_OPERATOR_LOGIN,
        }
        login = login_map.get(perfil, DEMO_ADMIN_LOGIN)
        usuario = self.db.query(Usuario).filter(Usuario.login == login).first()

        if not usuario or not usuario.ativo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário de demonstração não encontrado ou inativo.",
            )

        auth_service = AuthService(self.db)
        return auth_service.gerar_tokens_usuario(usuario)

    def resetar_dados_demo(self):
        try:
            cantina = self.db.query(Cantina).filter(Cantina.cnpj == DEMO_CNPJ).first()
            if not cantina:
                cantina = Cantina(nome_fantasia=DEMO_CANTINA_NOME, cnpj=DEMO_CNPJ)
                self.db.add(cantina)
                self.db.flush()
            else:
                demo_id = cantina.id_cantina
                pedidos_demo = self.db.query(Pedido.id_nota_fiscal).filter(Pedido.id_cantina == demo_id).all()
                id_pedidos = [p[0] for p in pedidos_demo]
                if id_pedidos:
                    self.db.query(ItemPedido).filter(ItemPedido.id_nota_fiscal.in_(id_pedidos)).delete(synchronize_session=False)
                    self.db.query(Pedido).filter(Pedido.id_nota_fiscal.in_(id_pedidos)).delete(synchronize_session=False)

                produtos_demo = self.db.query(Produto.id_produto).filter(Produto.id_cantina == demo_id).all()
                id_prods = [p[0] for p in produtos_demo]
                if id_prods:
                    self.db.query(FornecedorProduto).filter(FornecedorProduto.id_produto.in_(id_prods)).delete(synchronize_session=False)
                    self.db.query(Estoque).filter(Estoque.id_produto.in_(id_prods)).delete(synchronize_session=False)
                    self.db.query(Produto).filter(Produto.id_produto.in_(id_prods)).delete(synchronize_session=False)

                self.db.query(Categoria).filter(Categoria.id_cantina == demo_id).delete(synchronize_session=False)
                self.db.query(Funcionario).filter(Funcionario.id_cantina == demo_id).delete(synchronize_session=False)
                self.db.query(Fornecedor).filter(Fornecedor.id_cantina == demo_id).delete(synchronize_session=False)

                usuarios_demo = self.db.query(Usuario.id_usuario).filter(Usuario.id_cantina == demo_id).all()
                id_users = [u[0] for u in usuarios_demo]
                if id_users:
                    self.db.query(RefreshToken).filter(RefreshToken.id_usuario.in_(id_users)).delete(synchronize_session=False)
                    self.db.query(Usuario).filter(Usuario.id_usuario.in_(id_users)).delete(synchronize_session=False)

            # 1. Usuários de Demonstração
            senha_hash = gerar_hash_senha(DEMO_PASSWORD)
            admin = Usuario(
                nome="Admin FastCantina",
                login=DEMO_ADMIN_LOGIN,
                senha_hash=senha_hash,
                perfil="admin",
                ativo=True,
                id_cantina=cantina.id_cantina,
            )
            gerente = Usuario(
                nome="Gerente FastCantina",
                login=DEMO_MANAGER_LOGIN,
                senha_hash=senha_hash,
                perfil="gerente",
                ativo=True,
                id_cantina=cantina.id_cantina,
            )
            operador = Usuario(
                nome="Maria Atendente",
                login=DEMO_OPERATOR_LOGIN,
                senha_hash=senha_hash,
                perfil="funcionario",
                ativo=True,
                id_cantina=cantina.id_cantina,
            )
            self.db.add_all([admin, gerente, operador])

            # 2. Funcionários para o PDV
            func_maria = Funcionario(
                nome="Maria Atendente",
                cargo="Atendente",
                id_cantina=cantina.id_cantina,
            )
            func_carlos = Funcionario(
                nome="Carlos Caixa",
                cargo="Operador de Caixa",
                id_cantina=cantina.id_cantina,
            )
            self.db.add_all([func_maria, func_carlos])

            # 3. Fornecedor
            fornecedor = Fornecedor(
                nome="Distribuidora Alimentos Modelo",
                telefone="(11) 98765-4321",
                cnpj="11222333000199",
                id_cantina=cantina.id_cantina,
            )
            self.db.add(fornecedor)

            # 4. Categorias
            cat_salgados = Categoria(descricao="Salgados", id_cantina=cantina.id_cantina)
            cat_bebidas = Categoria(descricao="Bebidas", id_cantina=cantina.id_cantina)
            cat_doces = Categoria(descricao="Doces & Sobremesas", id_cantina=cantina.id_cantina)
            cat_lanches = Categoria(descricao="Lanches Naturais", id_cantina=cantina.id_cantina)
            self.db.add_all([cat_salgados, cat_bebidas, cat_doces, cat_lanches])
            self.db.flush()

            # 5. Produtos + Estoque
            produtos_data = [
                ("Coxinha com Catupiry", Decimal("7.50"), cat_salgados.id_categoria, False, 30),
                ("Pão de Queijo Tradicional", Decimal("4.00"), cat_salgados.id_categoria, False, 45),
                ("Misto Quente na Chapa", Decimal("8.50"), cat_salgados.id_categoria, True, 20),
                ("Suco Natural de Laranja 300ml", Decimal("7.00"), cat_bebidas.id_categoria, True, 25),
                ("Refrigerante Lata 350ml", Decimal("5.50"), cat_bebidas.id_categoria, False, 40),
                ("Água Mineral 500ml", Decimal("3.50"), cat_bebidas.id_categoria, False, 60),
                ("Brownie com Nozes", Decimal("6.50"), cat_doces.id_categoria, False, 15),
                ("Sanduíche Natural de Frango", Decimal("9.00"), cat_lanches.id_categoria, True, 18),
            ]

            produtos_criados = []
            for nome, preco, id_cat, exige_prep, qtd_est in produtos_data:
                prod = Produto(
                    nome=nome,
                    preco=preco,
                    id_categoria=id_cat,
                    exige_preparo=exige_prep,
                    id_cantina=cantina.id_cantina,
                )
                self.db.add(prod)
                self.db.flush()
                estoque = Estoque(quantidade_estoque=qtd_est, id_produto=prod.id_produto)
                self.db.add(estoque)
                produtos_criados.append(prod)

            # 6. Pedidos de exemplo para Dashboard e Cozinha
            p_coxinha = produtos_criados[0]
            p_refri = produtos_criados[4]
            p_misto = produtos_criados[2]
            p_suco = produtos_criados[3]
            p_sanduiche = produtos_criados[7]

            # Pedido 1: Concluído
            ped1 = Pedido(
                id_funcionario=func_maria.id_funcionario,
                valor_total=Decimal("20.50"),
                status="concluido",
                id_cantina=cantina.id_cantina,
            )
            self.db.add(ped1)
            self.db.flush()
            self.db.add(ItemPedido(quantidade=2, subtotal=Decimal("15.00"), id_produto=p_coxinha.id_produto, id_nota_fiscal=ped1.id_nota_fiscal))
            self.db.add(ItemPedido(quantidade=1, subtotal=Decimal("5.50"), id_produto=p_refri.id_produto, id_nota_fiscal=ped1.id_nota_fiscal))

            # Pedido 2: Pendente (visível na Cozinha)
            ped2 = Pedido(
                id_funcionario=func_maria.id_funcionario,
                valor_total=Decimal("15.50"),
                status="pendente",
                id_cantina=cantina.id_cantina,
            )
            self.db.add(ped2)
            self.db.flush()
            self.db.add(ItemPedido(quantidade=1, subtotal=Decimal("8.50"), id_produto=p_misto.id_produto, id_nota_fiscal=ped2.id_nota_fiscal))
            self.db.add(ItemPedido(quantidade=1, subtotal=Decimal("7.00"), id_produto=p_suco.id_produto, id_nota_fiscal=ped2.id_nota_fiscal))

            # Pedido 3: Em preparo (visível na Cozinha)
            ped3 = Pedido(
                id_funcionario=func_carlos.id_funcionario,
                valor_total=Decimal("9.00"),
                status="em_preparo",
                id_cantina=cantina.id_cantina,
            )
            self.db.add(ped3)
            self.db.flush()
            self.db.add(ItemPedido(quantidade=1, subtotal=Decimal("9.00"), id_produto=p_sanduiche.id_produto, id_nota_fiscal=ped3.id_nota_fiscal))

            self.db.commit()
            return {"mensagem": "Banco de dados de demonstração restaurado com sucesso para o estado original."}
        except Exception:
            self.db.rollback()
            raise
