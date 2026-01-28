from typing import Dict


def run(conn, settings) -> Dict:
    estoque_baixo = []
    pedidos_recentes = []

    if "stock" in settings.scopes.get("operational", set()):
        rows = conn.execute(
            """
            SELECT sku, name, stock
            FROM products
            ORDER BY stock ASC
            LIMIT 5
            """
        ).fetchall()
        estoque_baixo = [
            {"sku": row["sku"], "nome": row["name"], "estoque": row["stock"]} for row in rows
        ]

    if "orders" in settings.scopes.get("operational", set()):
        rows = conn.execute(
            """
            SELECT id AS order_id, status, customer
            FROM orders
            ORDER BY created_at DESC
            LIMIT 5
            """
        ).fetchall()
        pedidos_recentes = [
            {
                "pedido_id": row["order_id"],
                "status": row["status"],
                "cliente": row["customer"],
            }
            for row in rows
        ]

    return {
        "estoque_baixo": estoque_baixo,
        "pedidos_recentes": pedidos_recentes,
    }
