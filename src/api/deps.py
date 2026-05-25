from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.api.auth import decode_token
from src.core.config import load_settings, Settings
from src.core.db import get_conn

_bearer = HTTPBearer(auto_error=False)


def get_settings() -> Settings:
    return load_settings()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    settings: Settings = Depends(get_settings),
) -> dict:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token nao fornecido")

    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido ou expirado")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")

    with get_conn(settings.db_path) as conn:
        row = conn.execute(
            "SELECT id, username, email, role, is_active, nome_completo FROM users WHERE id = ?",
            (int(user_id),),
        ).fetchone()

    if not row or not row["is_active"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario nao encontrado ou inativo")

    return {
        "id": row["id"],
        "username": row["username"],
        "email": row["email"],
        "role": row["role"],
        "nome_completo": row["nome_completo"],
    }


def require_gestor(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "gestor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso restrito a gestores")
    return user
