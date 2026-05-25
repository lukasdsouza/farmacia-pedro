from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException

from src.api.auth import create_access_token, decode_token, hash_password, verify_password
from src.api.deps import get_settings
from src.api.models import (
    CustomerLoginRequest,
    CustomerRegisterRequest,
    CustomerResponse,
    CustomerTokenResponse,
    CustomerUpdateRequest,
)
from src.core.config import Settings
from src.core.db import get_conn

router = APIRouter(prefix="/api/customers", tags=["customers"])


def _row_to_response(r) -> CustomerResponse:
    return CustomerResponse(
        id=r["id"], nome=r["nome"], email=r["email"], telefone=r["telefone"] or "",
        endereco_rua=r["endereco_rua"] or "", endereco_numero=r["endereco_numero"] or "",
        endereco_complemento=r["endereco_complemento"] or "",
        endereco_bairro=r["endereco_bairro"] or "",
        endereco_cidade=r["endereco_cidade"] or "Rio de Janeiro",
        created_at=r["created_at"],
    )


def get_current_customer(
    authorization: Optional[str] = Header(None),
    settings: Settings = Depends(get_settings),
) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token de cliente requerido")
    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_token(token)
    if not payload or payload.get("actor") != "customer":
        raise HTTPException(status_code=401, detail="Token invalido ou expirado")
    customer_id = payload.get("customer_id")
    with get_conn(settings.db_path) as conn:
        row = conn.execute(
            "SELECT id, nome, email, telefone, endereco_rua, endereco_numero, "
            "endereco_complemento, endereco_bairro, endereco_cidade, created_at "
            "FROM customers WHERE id = ?", (customer_id,)
        ).fetchone()
    if not row:
        raise HTTPException(status_code=401, detail="Cliente nao encontrado")
    return dict(row)


@router.post("/register", response_model=CustomerTokenResponse, status_code=201)
def register(body: CustomerRegisterRequest, settings: Settings = Depends(get_settings)):
    with get_conn(settings.db_path) as conn:
        if conn.execute("SELECT id FROM customers WHERE email = ?", (body.email,)).fetchone():
            raise HTTPException(status_code=409, detail="Email ja cadastrado")
        cursor = conn.execute(
            """INSERT INTO customers
               (nome, email, telefone, senha_hash, endereco_rua, endereco_numero,
                endereco_complemento, endereco_bairro, endereco_cidade)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (body.nome, body.email, body.telefone, hash_password(body.senha),
             body.endereco_rua, body.endereco_numero, body.endereco_complemento,
             body.endereco_bairro, body.endereco_cidade),
        )
        conn.commit()
        row = conn.execute(
            "SELECT id, nome, email, telefone, endereco_rua, endereco_numero, "
            "endereco_complemento, endereco_bairro, endereco_cidade, created_at "
            "FROM customers WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()

    token = create_access_token({
        "sub": body.email, "customer_id": row["id"], "actor": "customer"
    })
    return CustomerTokenResponse(access_token=token, customer=_row_to_response(row))


@router.post("/login", response_model=CustomerTokenResponse)
def login(body: CustomerLoginRequest, settings: Settings = Depends(get_settings)):
    with get_conn(settings.db_path) as conn:
        row = conn.execute(
            "SELECT id, nome, email, telefone, senha_hash, endereco_rua, endereco_numero, "
            "endereco_complemento, endereco_bairro, endereco_cidade, created_at "
            "FROM customers WHERE email = ?", (body.email,)
        ).fetchone()
    if not row or not verify_password(body.senha, row["senha_hash"]):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")

    token = create_access_token({
        "sub": row["email"], "customer_id": row["id"], "actor": "customer"
    })
    return CustomerTokenResponse(access_token=token, customer=_row_to_response(row))


@router.get("/me", response_model=CustomerResponse)
def get_me(customer: dict = Depends(get_current_customer)):
    return CustomerResponse(
        id=customer["id"], nome=customer["nome"], email=customer["email"],
        telefone=customer.get("telefone", ""),
        endereco_rua=customer.get("endereco_rua", ""),
        endereco_numero=customer.get("endereco_numero", ""),
        endereco_complemento=customer.get("endereco_complemento", ""),
        endereco_bairro=customer.get("endereco_bairro", ""),
        endereco_cidade=customer.get("endereco_cidade", "Rio de Janeiro"),
        created_at=customer["created_at"],
    )


@router.put("/me", response_model=CustomerResponse)
def update_me(
    body: CustomerUpdateRequest,
    customer: dict = Depends(get_current_customer),
    settings: Settings = Depends(get_settings),
):
    field_map = [
        ("nome", "nome"), ("telefone", "telefone"),
        ("endereco_rua", "endereco_rua"), ("endereco_numero", "endereco_numero"),
        ("endereco_complemento", "endereco_complemento"),
        ("endereco_bairro", "endereco_bairro"), ("endereco_cidade", "endereco_cidade"),
    ]
    updates, values = [], []
    for attr, col in field_map:
        val = getattr(body, attr)
        if val is not None:
            updates.append(f"{col} = ?")
            values.append(val)
    if body.senha is not None:
        updates.append("senha_hash = ?")
        values.append(hash_password(body.senha))

    if updates:
        values.append(customer["id"])
        with get_conn(settings.db_path) as conn:
            conn.execute(f"UPDATE customers SET {', '.join(updates)} WHERE id = ?", values)
            conn.commit()
            row = conn.execute(
                "SELECT id, nome, email, telefone, endereco_rua, endereco_numero, "
                "endereco_complemento, endereco_bairro, endereco_cidade, created_at "
                "FROM customers WHERE id = ?", (customer["id"],)
            ).fetchone()
        return _row_to_response(row)

    return CustomerResponse(
        id=customer["id"], nome=customer["nome"], email=customer["email"],
        telefone=customer.get("telefone", ""),
        endereco_rua=customer.get("endereco_rua", ""),
        endereco_numero=customer.get("endereco_numero", ""),
        endereco_complemento=customer.get("endereco_complemento", ""),
        endereco_bairro=customer.get("endereco_bairro", ""),
        endereco_cidade=customer.get("endereco_cidade", "Rio de Janeiro"),
        created_at=customer["created_at"],
    )
