from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.deps import get_current_user, get_settings
from src.api.models import (
    CustomerOrderResponse,
    OrderItemResponse,
    OrderResponse,
    UpdateCustomerOrderRequest,
    UpdateOrderStatusRequest,
)
from src.core.config import Settings
from src.core.db import get_conn

router = APIRouter(prefix="/api/orders", tags=["orders"])


# ---------- ERP orders (sistema legado) ----------

@router.get("/erp", response_model=List[OrderResponse])
def list_erp_orders(
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    settings: Settings = Depends(get_settings),
    user: dict = Depends(get_current_user),
):
    with get_conn(settings.db_path) as conn:
        if status:
            rows = conn.execute(
                "SELECT id, status, created_at, customer, total FROM orders WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                (status, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, status, created_at, customer, total FROM orders ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()

        orders = []
        for row in rows:
            items_rows = conn.execute(
                """SELECT oi.product_id, p.sku, p.name, oi.qty, p.price
                   FROM order_items oi JOIN products p ON p.id = oi.product_id
                   WHERE oi.order_id = ?""",
                (row["id"],),
            ).fetchall()
            items = [OrderItemResponse(product_id=i["product_id"], sku=i["sku"], name=i["name"], qty=i["qty"], price=i["price"]) for i in items_rows]
            orders.append(OrderResponse(
                id=row["id"], status=row["status"], created_at=row["created_at"],
                customer=row["customer"], total=row["total"], items=items,
            ))
    return orders


@router.patch("/erp/{order_id}/status")
def update_erp_order_status(
    order_id: int,
    body: UpdateOrderStatusRequest,
    settings: Settings = Depends(get_settings),
    user: dict = Depends(get_current_user),
):
    with get_conn(settings.db_path) as conn:
        result = conn.execute(
            "UPDATE orders SET status = ? WHERE id = ?", (body.status, order_id)
        )
        conn.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Pedido nao encontrado")
    return {"ok": True, "id": order_id, "status": body.status}


# ---------- Customer orders (via chat) ----------

@router.get("", response_model=List[CustomerOrderResponse])
def list_customer_orders(
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    settings: Settings = Depends(get_settings),
    user: dict = Depends(get_current_user),
):
    with get_conn(settings.db_path) as conn:
        if status:
            rows = conn.execute(
                """SELECT id, session_id, customer_name, customer_phone, items_json,
                          delivery_type, delivery_address, taxa_entrega, status, total, notes, created_at, updated_at
                   FROM customer_orders WHERE status = ? ORDER BY created_at DESC LIMIT ?""",
                (status, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT id, session_id, customer_name, customer_phone, items_json,
                          delivery_type, delivery_address, taxa_entrega, status, total, notes, created_at, updated_at
                   FROM customer_orders ORDER BY created_at DESC LIMIT ?""",
                (limit,),
            ).fetchall()
    return [CustomerOrderResponse(**dict(r)) for r in rows]


@router.get("/{order_id}", response_model=CustomerOrderResponse)
def get_customer_order(
    order_id: int,
    settings: Settings = Depends(get_settings),
    user: dict = Depends(get_current_user),
):
    with get_conn(settings.db_path) as conn:
        row = conn.execute(
            """SELECT id, session_id, customer_name, customer_phone, items_json,
                      delivery_type, delivery_address, taxa_entrega, status, total, notes, created_at, updated_at
               FROM customer_orders WHERE id = ?""",
            (order_id,),
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Pedido nao encontrado")
    return CustomerOrderResponse(**dict(row))


@router.patch("/{order_id}/status")
def update_customer_order_status(
    order_id: int,
    body: UpdateCustomerOrderRequest,
    settings: Settings = Depends(get_settings),
    user: dict = Depends(get_current_user),
):
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    with get_conn(settings.db_path) as conn:
        result = conn.execute(
            "UPDATE customer_orders SET status = ?, updated_at = ? WHERE id = ?",
            (body.status, now, order_id),
        )
        conn.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Pedido nao encontrado")
    return {"ok": True, "id": order_id, "status": body.status}
