# Contratos de Dados (demo)

Tabelas
- products: sku, name, category, price, avg_cost, stock
- sales: product_id, qty, price, sale_date, region
- invoices: product_id, unit_cost, invoice_date, supplier
- competitor_prices: sku, competitor, price, collected_at
- orders: status, created_at, customer, total
- order_items: order_id, product_id, qty

Metricas-chave
- Markup % = (price - avg_cost) / avg_cost * 100
- Margem % = (price - unit_cost) / price * 100
- Variacao de giro % = (cur_total - prev_total) / prev_total * 100

Regras
- Bonus: markup > BONUS_MARKUP_PCT
- Estoque parado: days_no_sales > DAYS_NO_SALES
- Concorrencia: competitor_price < our_price
