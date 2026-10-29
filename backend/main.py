from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware


from core.config import settings
from core.database import Base, engine
from core.rate_limit import limiter

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

from routers.auth_router import router as auth_router
from routers.cantina_router import router as cantina_router
from routers.categoria_router import router as categoria_router
from routers.demo_router import router as demo_router
from routers.estoque_router import router as estoque_router
from routers.fornecedor_produto_router import router as fornecedor_produto_router
from routers.fornecedor_router import router as fornecedor_router
from routers.funcionario_router import router as funcionario_router
from routers.item_pedido_router import router as item_pedido_router
from routers.pedido_router import router as pedido_router
from routers.produto_router import router as produto_router
from routers.usuario_router import router as usuario_router
from routers.previsao_router import router as previsao_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API para cantina", description="API para controle de cantina ", version="1.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

allowed_origins = [
    origin.strip()
    for origin in settings.CORS_ORIGINS.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(cantina_router)
app.include_router(usuario_router)
app.include_router(categoria_router)
app.include_router(produto_router)
app.include_router(funcionario_router)
app.include_router(fornecedor_router)
app.include_router(estoque_router)
app.include_router(pedido_router)
app.include_router(item_pedido_router)
app.include_router(fornecedor_produto_router)
app.include_router(previsao_router)
app.include_router(demo_router)


@app.get("/")
def home():
    return {
        "mensagem": "API da cantina funcionandokkkk"
    }

@app.get("/ping")
def ping():
    """Rota usada por serviços como o cron-job.org para manter o servidor acordado."""
    return {"ping": "pong"}
