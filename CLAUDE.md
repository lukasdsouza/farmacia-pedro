# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Seed the demo SQLite database (required before running anything)
python scripts/seed_demo_db.py

# Run the report generation swarm
python scripts/run_demo.py

# Run automation (once or scheduled, depending on AUTOMATION_MODE env var)
python scripts/automation.py

# Interactive chat CLI
python scripts/chat_cli.py

# Chat webhook server (listens on port 8000)
python scripts/chat_webhook.py
# Test it: POST http://localhost:8000/webhook {"from":"cliente1","text":"Tem dipirona?"}

# WebSocket server for live report updates (port 8765)
python scripts/ws_server.py

# Quick smoke test
python scripts/smoke_test.py

# Run all tests
pytest

# Run a single test
pytest tests/test_agents.py::test_operational_returns_expected_keys
```

## Architecture

This is a read-only AI swarm for pharmacy ERP operations. The write layer (`executor_stub.py`) is intentionally disabled and requires explicit WhatsApp approval before any mutation happens.

### Data layer

SQLite database at `data/erp_demo.db` (created by `seed_demo_db.py`). Tables: `products`, `sales`, `invoices`, `competitor_prices`, `orders`, `order_items`.

All DB access goes through `src/core/db.py:get_conn()` — a context manager that sets `row_factory = sqlite3.Row`.

### Report pipeline (`src/runner.py`)

`generate_report()` runs five agents in sequence, each receiving `(conn, settings)`:
- `operational` — low stock + recent orders (filtered by `OPERATIONAL_SCOPES`)
- `inbound_audit` — detects negative margins on invoices
- `strategist` — strategic pricing/competitor insights
- `inventory` — dead stock + reorder suggestions
- `executor_stub` — always returns `{"status": "disabled"}`

Outputs: `out/report.json` and `out/report.md`. Errors per agent are caught and logged individually, never propagated.

### Automation (`src/automation/flow.py`)

Wraps the report pipeline. Two modes via `AUTOMATION_MODE` env var:
- `once` (default) — runs once then exits
- `schedule` / `agendado` — loops every `AUTOMATION_INTERVAL_MIN` minutes

After each run, optionally POSTs the report to a WhatsApp webhook (`WHATSAPP_WEBHOOK_URL`).

### Agent scopes

Each agent's queries are gated by scope sets loaded from env vars. Example: `OPERATIONAL_SCOPES=stock,orders` enables stock and order queries. Empty scope = no data returned.

```python
if "stock" in settings.scopes.get("operational", set()):
    ...
```

### Chat system (`src/chat/`)

State-machine chat for customer service (WhatsApp-style). Entry points: `scripts/chat_cli.py` (stdin/stdout) and `scripts/chat_webhook.py` (HTTP POST on port 8000).

- **`data.py`** — `DataGateway` ABC defines the data contract. `SqliteGateway` is the real implementation; `MySqlGateway` is a stub. Product search tokenizes user input (strips stopwords) and matches normalized product names.
- **`flow_atendimento.py`** — `AtendimentoFlow` is the state machine. States: `START → ASK_PRODUCT_CHOICE / ASK_VARIANT → ASK_QTY / ASK_CART_QTY → OUT_OF_STOCK / ASK_FULFILLMENT → PICKUP_CONFIRM / DELIVERY_ADDRESS → DELIVERY_DETAILS → ASK_CLIENT_NAME → ASK_CONTACT_PERMISSION → DONE`. Each `handle()` call returns `(reply, next_state, data)`.
- **`state.py`** — `SessionStore` persists messages as JSONL (`.jsonl`) and flow state as JSON (`.state.json`) under `out/chat_sessions/` (configurable via `CHAT_SESSION_DIR`).
- **`integration.py`** — `IntegrationAdapter` with two implementations: `LocalAdapter` (writes to audit log) and `WebhookAdapter` (POSTs events to `INTEGRATION_WEBHOOK_URL`). Selectable via `INTEGRATION_ADAPTER=local|webhook` or a custom `module:Class` path.

### WebSocket server (`scripts/ws_server.py`)

Polls `out/report.json` every 2 seconds for file mtime changes and broadcasts `{"type": "report_update", ...}` to all connected clients on `ws://0.0.0.0:8765`.

### Configuration

All settings are in `src/core/config.py:Settings` (frozen dataclass), loaded from `.env` + environment variables. Key env vars:

| Var | Default | Purpose |
|-----|---------|---------|
| `ERP_DB_PATH` | `data/erp_demo.db` | SQLite path |
| `REPORT_DIR` | `out` | Output directory |
| `AUTOMATION_MODE` | `once` | `once` or `schedule` |
| `AUTOMATION_SEED_DEMO` | `false` | Auto-seed DB on first automation run |
| `CHAT_LOJA_NOME` | `Drogarias Max - Barra Blue` | Store name used in chat replies |
| `CHAT_DELIVERY_RULES` | `` | Semicolon-separated `bairro:taxa:prazo` rules |
| `INTEGRATION_ADAPTER` | `local` | `local`, `webhook`, or `module:Class` |
| `WHATSAPP_WEBHOOK_URL` | `` | WhatsApp send is skipped if empty |
| `OPERATIONAL_SCOPES` | `` | Comma-separated scopes: `stock`, `orders` |

### Docker

The `Dockerfile` seeds the demo DB at build time (`scripts/seed_demo_db.py`) and runs `scripts/run_demo.py` as the default command. Only `websockets>=12.0` and `pytest>=8.0` are in `requirements.txt` — the agents are rule-based, not LLM-backed.
