from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.deps import get_current_user, get_settings
from src.api.models import ProductResponse
from src.core.config import Settings
from src.core.db import get_conn

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=List[ProductResponse])
def list_products(
    category: Optional[str] = Query(None),
    q: Optional[str] = Query(None, max_length=100),
    settings: Settings = Depends(get_settings),
):
    with get_conn(settings.db_path) as conn:
        if q:
            rows = conn.execute(
                "SELECT id, sku, name, category, price, avg_cost, stock FROM products WHERE LOWER(name) LIKE ? ORDER BY name",
                (f"%{q.lower()}%",),
            ).fetchall()
        elif category:
            rows = conn.execute(
                "SELECT id, sku, name, category, price, avg_cost, stock FROM products WHERE category = ? ORDER BY name",
                (category,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, sku, name, category, price, avg_cost, stock FROM products ORDER BY name"
            ).fetchall()
    return [ProductResponse(**dict(r)) for r in rows]


@router.get("/categories")
def list_categories(settings: Settings = Depends(get_settings)):
    with get_conn(settings.db_path) as conn:
        rows = conn.execute("SELECT DISTINCT category FROM products ORDER BY category").fetchall()
    return [r["category"] for r in rows]


@router.get("/{sku}", response_model=ProductResponse)
def get_product(sku: str, settings: Settings = Depends(get_settings)):
    with get_conn(settings.db_path) as conn:
        row = conn.execute(
            "SELECT id, sku, name, category, price, avg_cost, stock FROM products WHERE sku = ?",
            (sku.upper(),),
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")
    return ProductResponse(**dict(row))


@router.patch("/{sku}/stock")
def update_stock(
    sku: str,
    body: dict,
    settings: Settings = Depends(get_settings),
    user: dict = Depends(get_current_user),
):
    new_stock = body.get("stock")
    if new_stock is None or not isinstance(new_stock, int) or new_stock < 0:
        raise HTTPException(status_code=400, detail="Campo 'stock' deve ser inteiro >= 0")
    with get_conn(settings.db_path) as conn:
        result = conn.execute(
            "UPDATE products SET stock = ? WHERE sku = ?", (new_stock, sku.upper())
        )
        conn.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Produto nao encontrado")
    return {"ok": True, "sku": sku.upper(), "stock": new_stock}
