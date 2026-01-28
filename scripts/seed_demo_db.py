import os
import sqlite3
from datetime import datetime, timedelta, timezone


DB_PATH = os.path.join("data", "erp_demo.db")


def reset_schema(conn):
    conn.executescript(
        """
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS sales;
        DROP TABLE IF EXISTS invoices;
        DROP TABLE IF EXISTS competitor_prices;
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS order_items;

        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            avg_cost REAL NOT NULL,
            stock INTEGER NOT NULL
        );

        CREATE TABLE sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            qty INTEGER NOT NULL,
            price REAL NOT NULL,
            sale_date TEXT NOT NULL,
            region TEXT NOT NULL,
            FOREIGN KEY(product_id) REFERENCES products(id)
        );

        CREATE TABLE invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            unit_cost REAL NOT NULL,
            invoice_date TEXT NOT NULL,
            supplier TEXT NOT NULL,
            FOREIGN KEY(product_id) REFERENCES products(id)
        );

        CREATE TABLE competitor_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT NOT NULL,
            competitor TEXT NOT NULL,
            price REAL NOT NULL,
            collected_at TEXT NOT NULL
        );

        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            customer TEXT NOT NULL,
            total REAL NOT NULL
        );

        CREATE TABLE order_items (
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            qty INTEGER NOT NULL,
            FOREIGN KEY(order_id) REFERENCES orders(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        );
        """
    )


def seed_data(conn):
    products = [
        ("MED001", "Dipirona 500mg", "Analgesico", 12.90, 5.20, 120),
        ("MED002", "Paracetamol 750mg", "Analgesico", 18.50, 7.00, 60),
        ("MED003", "Amoxicilina 500mg", "Antibiotico", 42.00, 28.00, 15),
        ("HIG001", "Alcool Gel 70%", "Higiene", 9.90, 3.50, 300),
        ("HIG002", "Mascara Descartavel", "Higiene", 2.50, 0.80, 500),
        ("SUP001", "Vitamina C 1g", "Suplemento", 39.90, 18.00, 8),
    ]
    conn.executemany(
        "INSERT INTO products (sku, name, category, price, avg_cost, stock) VALUES (?, ?, ?, ?, ?, ?)",
        products,
    )

    today = datetime.now(timezone.utc).date()

    # Sales (baseado no exemplo do enunciado)
    vendas = [
        (1, "2025-12-01", "Centro", "Joao", 125.80),
        (2, "2025-12-05", "Centro", "Maria", 89.50),
        (3, "2026-01-10", "Centro", "Carlos", 42.00),
        (4, "2026-01-15", "Centro", "Joao", 18.50),
    ]
    venda_datas = {row[0]: row[1] for row in vendas}
    itens_venda = [
        (1, 1, 1, 5, 12.90),
        (2, 1, 4, 3, 9.90),
        (3, 2, 2, 2, 18.50),
        (4, 3, 3, 1, 42.00),
        (5, 4, 2, 1, 18.50),
    ]
    sales_rows = []
    for _, id_venda, id_produto, quantidade, preco_unitario in itens_venda:
        sale_date = venda_datas.get(id_venda, today.isoformat())
        sales_rows.append((id_produto, quantidade, preco_unitario, sale_date, "centro"))

    conn.executemany(
        "INSERT INTO sales (product_id, qty, price, sale_date, region) VALUES (?, ?, ?, ?, ?)",
        sales_rows,
    )

    # Invoices
    invoice_rows = []
    for i, (sku, _, _, _, cost, _) in enumerate(products, start=1):
        inv_date = (today - timedelta(days=(i % 14))).isoformat()
        unit_cost = cost * (1.1 if i in (3,) else 1.0)
        invoice_rows.append((i, unit_cost, inv_date, "Fornecedor A"))

    conn.executemany(
        "INSERT INTO invoices (product_id, unit_cost, invoice_date, supplier) VALUES (?, ?, ?, ?)",
        invoice_rows,
    )

    # Competitor prices
    comp_rows = [
        ("MED001", "ConcorrenteA", 11.50, today.isoformat()),
        ("MED002", "ConcorrenteB", 16.90, today.isoformat()),
        ("SUP001", "ConcorrenteC", 34.90, today.isoformat()),
    ]
    conn.executemany(
        "INSERT INTO competitor_prices (sku, competitor, price, collected_at) VALUES (?, ?, ?, ?)",
        comp_rows,
    )

    # Orders
    order_rows = [
        ("enviado", (today - timedelta(days=1)).isoformat(), "Carlos Silva", 120.0),
        ("processando", today.isoformat(), "Ana Souza", 85.0),
        ("pendente", (today - timedelta(days=2)).isoformat(), "Marcos Lima", 55.0),
        ("entregue", (today - timedelta(days=5)).isoformat(), "Paula Reis", 200.0),
        ("processando", (today - timedelta(days=3)).isoformat(), "Lucas Prado", 30.0),
    ]
    conn.executemany(
        "INSERT INTO orders (status, created_at, customer, total) VALUES (?, ?, ?, ?)",
        order_rows,
    )

    order_item_rows = [
        (1, 1, 2),
        (1, 3, 1),
        (2, 2, 1),
        (3, 4, 1),
        (4, 5, 1),
        (5, 6, 1),
    ]
    conn.executemany(
        "INSERT INTO order_items (order_id, product_id, qty) VALUES (?, ?, ?)",
        order_item_rows,
    )


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        reset_schema(conn)
        seed_data(conn)
        conn.commit()
        print(f"Banco demo criado em {DB_PATH}")
    finally:
        conn.close()
