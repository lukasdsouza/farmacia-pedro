from fastapi import APIRouter, Depends, HTTPException, status

from src.api.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from src.api.deps import get_current_user, get_settings
from src.api.models import LoginRequest, RefreshRequest, TokenResponse, UserResponse
from src.core.config import Settings
from src.core.db import get_conn

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, settings: Settings = Depends(get_settings)):
    with get_conn(settings.db_path) as conn:
        row = conn.execute(
            "SELECT id, username, email, password_hash, role, is_active, nome_completo FROM users WHERE username = ?",
            (body.username,),
        ).fetchone()

    if not row or not row["is_active"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais invalidas")

    if not verify_password(body.password, row["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais invalidas")

    token_data = {"sub": str(row["id"]), "role": row["role"]}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        role=row["role"],
        nome_completo=row["nome_completo"] or row["username"],
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(body: RefreshRequest, settings: Settings = Depends(get_settings)):
    payload = decode_token(body.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token invalido")

    user_id = payload.get("sub")
    with get_conn(settings.db_path) as conn:
        row = conn.execute(
            "SELECT id, role, is_active, nome_completo, username FROM users WHERE id = ?",
            (int(user_id),),
        ).fetchone()

    if not row or not row["is_active"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario inativo")

    token_data = {"sub": str(row["id"]), "role": row["role"]}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        role=row["role"],
        nome_completo=row["nome_completo"] or row["username"],
    )


@router.get("/me", response_model=UserResponse)
def me(
    user: dict = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    with get_conn(settings.db_path) as conn:
        row = conn.execute(
            "SELECT id, username, email, role, is_active, nome_completo, created_at FROM users WHERE id = ?",
            (user["id"],),
        ).fetchone()
    return UserResponse(
        id=row["id"],
        username=row["username"],
        email=row["email"],
        role=row["role"],
        is_active=bool(row["is_active"]),
        nome_completo=row["nome_completo"] or "",
        created_at=row["created_at"],
    )
