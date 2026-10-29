from typing import Literal
from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.auth_dependencies import get_current_user
from core.config import settings
from core.database import get_db
from core.rate_limit import limiter
from core.security import ACCESS_TOKEN_EXPIRE_MINUTES
from schemas.auth_schema import (
    LoginRequest,
    LogoutResponse,
    RefreshTokenRequest,
    TokenResponse,
)
from schemas.usuario_schema import UsuarioResponse
from services.auth_service import AuthService, REFRESH_TOKEN_EXPIRE_DAYS
from services.demo_service import DemoService

router = APIRouter(prefix="/auth", tags=["Auth"])


class DemoLoginRequest(BaseModel):
    perfil: Literal["admin", "gerente", "funcionario"] = "admin"


def _set_auth_cookies(response: Response, tokens: dict):
    """Injeta access e refresh tokens como cookies HttpOnly."""
    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/auth",
    )


def _clear_auth_cookies(response: Response):
    """Remove os cookies de autenticação."""
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/auth")


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, response: Response, payload: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    tokens = service.login(payload.login, payload.senha)
    _set_auth_cookies(response, tokens)
    return tokens


@router.post("/demo", response_model=TokenResponse)
@limiter.limit("10/minute")
def login_demo(
    request: Request,
    response: Response,
    payload: DemoLoginRequest | None = None,
    db: Session = Depends(get_db),
):
    perfil = payload.perfil if payload else "admin"
    demo_service = DemoService(db)
    tokens = demo_service.autenticar_demo(perfil=perfil)
    _set_auth_cookies(response, tokens)
    return tokens


@router.post("/token", response_model=TokenResponse)
@limiter.limit("5/minute")
def login_for_access_token(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    tokens = service.login(form_data.username, form_data.password)
    _set_auth_cookies(response, tokens)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
def refresh(request: Request, response: Response, db: Session = Depends(get_db), payload: RefreshTokenRequest | None = None):
    # Prioridade: cookie, fallback: body JSON
    refresh_token_value = request.cookies.get("refresh_token")
    if not refresh_token_value and payload:
        refresh_token_value = payload.refresh_token

    if not refresh_token_value:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token nao fornecido")

    service = AuthService(db)
    tokens = service.refresh(refresh_token_value)
    _set_auth_cookies(response, tokens)
    return tokens


@router.post("/logout", response_model=LogoutResponse)
def logout(request: Request, response: Response, db: Session = Depends(get_db), payload: RefreshTokenRequest | None = None):
    # Prioridade: cookie, fallback: body JSON
    refresh_token_value = request.cookies.get("refresh_token")
    if not refresh_token_value and payload:
        refresh_token_value = payload.refresh_token

    if refresh_token_value:
        service = AuthService(db)
        service.logout(refresh_token_value)

    _clear_auth_cookies(response)
    return {"mensagem": "Logout realizado com sucesso"}


@router.get("/me", response_model=UsuarioResponse)
def me(usuario=Depends(get_current_user)):
    return usuario
