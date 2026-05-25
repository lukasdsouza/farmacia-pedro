from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.auth import hash_password
from src.api.deps import get_current_user, get_settings, require_gestor
from src.api.models import CreateUserRequest, UpdateUserRequest, UserResponse
from src.core.config import Settings
from src.core.db import get_conn

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=List[UserResponse])
def list_users(
    settings: Settings = Depends(get_settings),
    user: dict = Depends(require_gestor),
):
    with get_conn(settings.db_path) as conn:
        rows = conn.execute(
            "SELECT id, username, email, role, is_active, nome_completo, created_at FROM users ORDER BY created_at DESC"
        ).fetchall()
    return [UserResponse(id=r["id"], username=r["username"], email=r["email"],
                         role=r["role"], is_active=bool(r["is_active"]),
                         nome_completo=r["nome_completo"] or "", created_at=r["created_at"]) for r in rows]


@router.post("", response_model=UserResponse, status_code=201)
def create_user(
    body: CreateUserRequest,
    settings: Settings = Depends(get_settings),
    user: dict = Depends(require_gestor),
):
    with get_conn(settings.db_path) as conn:
        existing = conn.execute(
            "SELECT id FROM users WHERE username = ? OR email = ?", (body.username, body.email)
        ).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="Username ou email ja em uso")

        cursor = conn.execute(
            "INSERT INTO users (username, email, password_hash, role, is_active, nome_completo) VALUES (?, ?, ?, ?, 1, ?)",
            (body.username, body.email, hash_password(body.password), body.role, body.nome_completo),
        )
        conn.commit()
        new_id = cursor.lastrowid
        row = conn.execute(
            "SELECT id, username, email, role, is_active, nome_completo, created_at FROM users WHERE id = ?",
            (new_id,),
        ).fetchone()

    return UserResponse(id=row["id"], username=row["username"], email=row["email"],
                        role=row["role"], is_active=bool(row["is_active"]),
                        nome_completo=row["nome_completo"] or "", created_at=row["created_at"])


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    body: UpdateUserRequest,
    settings: Settings = Depends(get_settings),
    current_user: dict = Depends(require_gestor),
):
    with get_conn(settings.db_path) as conn:
        existing = conn.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Usuario nao encontrado")

        updates = []
        values = []
        if body.email is not None:
            updates.append("email = ?")
            values.append(body.email)
        if body.role is not None:
            updates.append("role = ?")
            values.append(body.role)
        if body.is_active is not None:
            updates.append("is_active = ?")
            values.append(1 if body.is_active else 0)
        if body.nome_completo is not None:
            updates.append("nome_completo = ?")
            values.append(body.nome_completo)
        if body.password is not None:
            updates.append("password_hash = ?")
            values.append(hash_password(body.password))

        if updates:
            values.append(user_id)
            conn.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", values)
            conn.commit()

        row = conn.execute(
            "SELECT id, username, email, role, is_active, nome_completo, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()

    return UserResponse(id=row["id"], username=row["username"], email=row["email"],
                        role=row["role"], is_active=bool(row["is_active"]),
                        nome_completo=row["nome_completo"] or "", created_at=row["created_at"])


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    settings: Settings = Depends(get_settings),
    current_user: dict = Depends(require_gestor),
):
    if user_id == current_user["id"]:
        raise HTTPException(status_code=400, detail="Voce nao pode deletar sua propria conta")
    with get_conn(settings.db_path) as conn:
        result = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Usuario nao encontrado")
