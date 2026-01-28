from datetime import datetime, timedelta, timezone
from typing import Dict


def _sum_by_region(conn, start_date: str, end_date: str):
    rows = conn.execute(
        """
        SELECT region, SUM(qty * price) AS total
        FROM sales
        WHERE sale_date >= ? AND sale_date < ?
        GROUP BY region
        """,
        (start_date, end_date),
    ).fetchall()
    return {row["region"]: float(row["total"]) for row in rows}


def run(conn, settings) -> Dict:
    quedas_giro = []
    alertas_concorrencia = []

    if "sales" in settings.scopes.get("strategist", set()):
        today = datetime.now(timezone.utc).date()
        cur_start = today - timedelta(days=settings.turnover_window_days)
        prev_start = cur_start - timedelta(days=settings.turnover_window_days)

        cur = _sum_by_region(conn, cur_start.isoformat(), today.isoformat())
        prev = _sum_by_region(conn, prev_start.isoformat(), cur_start.isoformat())

        regions = set(cur.keys()) | set(prev.keys())
        for region in regions:
            cur_total = cur.get(region, 0.0)
            prev_total = prev.get(region, 0.0)
            if prev_total <= 0:
                continue
            change = ((cur_total - prev_total) / prev_total) * 100
            if change <= -10.0:
                quedas_giro.append(
                    {
                        "regiao": region,
                        "total_anterior": round(prev_total, 2),
                        "total_atual": round(cur_total, 2),
                        "variacao_pct": round(change, 1),
                    }
                )

    if "competitors" in settings.scopes.get("strategist", set()):
        rows = conn.execute(
            """
            SELECT c.sku, c.competitor, c.price AS competitor_price, p.price AS our_price
            FROM competitor_prices c
            JOIN products p ON p.sku = c.sku
            WHERE c.price < p.price
            ORDER BY (p.price - c.price) DESC
            LIMIT 10
            """
        ).fetchall()
        alertas_concorrencia = [
            {
                "sku": row["sku"],
                "concorrente": row["competitor"],
                "preco_concorrente": row["competitor_price"],
                "preco_nosso": row["our_price"],
            }
            for row in rows
        ]

    return {
        "quedas_giro": quedas_giro,
        "alertas_concorrencia": alertas_concorrencia,
    }
