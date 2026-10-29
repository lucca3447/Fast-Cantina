from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from core.security import criar_access_token, decodificar_token, verificar_senha
from repositories.refresh_token_repository import RefreshTokenRepository
from repositories.usuario_repository import UsuarioRepository

REFRESH_TOKEN_EXPIRE_DAYS = 7


class AuthService:
    def __init__(self, db: Session):
        self.usuario_repository = UsuarioRepository(db)
        self.refresh_token_repository = RefreshTokenRepository(db)

    def gerar_tokens_usuario(self, usuario):
        if not usuario.ativo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inativo",
            )

        access_token = criar_access_token(
            {
                "sub": str(usuario.id_usuario),
                "perfil": usuario.perfil,
                "type": "access",
                "id_cantina": usuario.id_cantina,
            }
        )

        refresh_jti = str(uuid4())
        refresh_exp = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = criar_access_token(
            {
                "sub": str(usuario.id_usuario),
                "perfil": usuario.perfil,
                "id_cantina": usuario.id_cantina,
                "jti": refresh_jti,
                "type": "refresh",
            },
            expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        )

        self.refresh_token_repository.criar(
            id_usuario=usuario.id_usuario,
            token_jti=refresh_jti,
            expira_em=refresh_exp.replace(tzinfo=None),
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    def login(self, login: str, senha: str):
        usuario = self.usuario_repository.buscar_por_login(login)
        if not usuario or not verificar_senha(senha, usuario.senha_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Login ou senha invalidos",
            )

        return self.gerar_tokens_usuario(usuario)

    def refresh(self, refresh_token: str):
        payload = decodificar_token(refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token invalido",
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tipo de token invalido",
            )

        token_jti = payload.get("jti")
        token_db = self.refresh_token_repository.buscar_por_jti(token_jti)
        if not token_db or token_db.revogado:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token revogado",
            )

        if token_db.expira_em < datetime.utcnow():
            self.refresh_token_repository.revogar(token_db)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expirado",
            )

        id_usuario = int(payload.get("sub"))
        usuario = self.usuario_repository.buscar_por_id(id_usuario)
        if not usuario or not usuario.ativo:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario invalido",
            )

        access_token = criar_access_token(
            {
                "sub": str(usuario.id_usuario),
                "perfil": usuario.perfil,
                "type": "access",
                "id_cantina": usuario.id_cantina,
            }
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    def logout(self, refresh_token: str):
        payload = decodificar_token(refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token invalido",
            )

        token_jti = payload.get("jti")
        token_db = self.refresh_token_repository.buscar_por_jti(token_jti)
        if token_db and not token_db.revogado:
            self.refresh_token_repository.revogar(token_db)

        return {"mensagem": "Logout realizado com sucesso"}
