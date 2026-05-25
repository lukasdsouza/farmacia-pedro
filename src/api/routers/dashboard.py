from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from src.api.deps import get_current_user, get_settings
from src.api.models import DashboardStats
from src.core.config import Settings
from src.core.db import get_conn

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardStats)
def get_dashboard(
    settings: Settings = Depends(get_settings),
    user: dict = Depends(get_current_user),
):
    today = datetime.now(timezone.utc).date().isoformat()

    with get_conn(settings.db_path) as conn:
        total_products = conn.execute("SELECT COUNT(*) AS c FROM products").fetchone()["c"]
        low_stock = conn.execute(
            "SELECT COUNT(*) AS c FROM products WHERE stock < ?", (settings.low_stock_threshold,)
        ).fetchone()["c"]

        pending_orders = conn.execute(
            "SELECT COUNT(*) AS c FROM orders WHERE status IN ('pendente', 'processando')"
        ).fetchone()["c"]

        todays_orders = conn.execute(
            "SELECT COUNT(*) AS c FROM orders WHERE created_at >= ?", (today,)
        ).fetchone()["c"]

        total_customer_orders = conn.execute("SELECT COUNT(*) AS c FROM customer_orders").fetchone()["c"]

        pending_customer_orders = conn.execute(
            "SELECT COUNT(*) AS c FROM customer_orders WHERE status IN ('pendente', 'confirmado', 'em_preparo')"
        ).fetchone()["c"]

        revenue_today = 0.0
        if user["role"] == "gestor":
            rev_row = conn.execute(
                "SELECT COALESCE(SUM(total), 0) AS r FROM orders WHERE created_at >= ?", (today,)
            ).fetchone()
            revenue_today = float(rev_row["r"])

        top_rows = conn.execute(
            """SELECT p.name, p.sku, COALESCE(SUM(s.qty), 0) AS total_sold
               FROM products p
               LEFT JOIN sales s ON s.product_id = p.id
               GROUP BY p.id ORDER BY total_sold DESC LIMIT 5"""
        ).fetchall()
        top_products = [{"name": r["name"], "sku": r["sku"], "total_sold": r["total_sold"]} for r in top_rows]

    return DashboardStats(
        total_products=total_products,
        low_stock_count=low_stock,
        pending_orders=pending_orders,
        todays_orders=todays_orders,
        total_customer_orders=total_customer_orders,
        pending_customer_orders=pending_customer_orders,
        revenue_today=revenue_today,
        top_products=top_products,
    )
