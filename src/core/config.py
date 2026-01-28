import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    db_path: str
    report_dir: str
    bonus_markup_pct: float
    days_no_sales: int
    low_margin_threshold: float
    safety_stock_days: int
    turnover_window_days: int
    automation_mode: str
    automation_interval_min: int
    automation_max_runs: int
    automation_retries: int
    automation_retry_delay_sec: int
    automation_seed_demo: bool
    whatsapp_webhook_url: str
    whatsapp_to: str
    whatsapp_sender: str
    chat_mode: str
    chat_loja_nome: str
    chat_endereco: str
    chat_filial: str
    chat_reserva_validade: str
    chat_delivery_rules: str
    chat_delivery_fallback: str
    chat_webhook_host: str
    chat_webhook_port: int
    chat_session_dir: str
    low_stock_threshold: int
    integration_adapter: str
    integration_adapter_path: str
    integration_webhook_url: str
    scopes: dict


def _load_env_file(path: str = ".env") -> None:
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="ascii") as handle:
        for line in handle:
            raw = line.strip()
            if not raw or raw.startswith("#") or "=" not in raw:
                continue
            key, value = raw.split("=", 1)
            key = key.strip()
            value = value.strip().strip("\"").strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def _get_env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _get_env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _get_env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _get_scopes(prefix: str) -> set:
    raw = os.getenv(prefix, "")
    if not raw.strip():
        return set()
    return {part.strip() for part in raw.split(",") if part.strip()}


def load_settings() -> Settings:
    _load_env_file()
    return Settings(
        db_path=os.getenv("ERP_DB_PATH", os.path.join("data", "erp_demo.db")),
        report_dir=os.getenv("REPORT_DIR", "out"),
        bonus_markup_pct=_get_env_float("BONUS_MARKUP_PCT", 110.0),
        days_no_sales=_get_env_int("DAYS_NO_SALES", 60),
        low_margin_threshold=_get_env_float("LOW_MARGIN_THRESHOLD", 0.15),
        safety_stock_days=_get_env_int("SAFETY_STOCK_DAYS", 15),
        turnover_window_days=_get_env_int("TURNOVER_WINDOW_DAYS", 30),
        automation_mode=os.getenv("AUTOMATION_MODE", "once"),
        automation_interval_min=_get_env_int("AUTOMATION_INTERVAL_MIN", 30),
        automation_max_runs=_get_env_int("AUTOMATION_MAX_RUNS", 0),
        automation_retries=_get_env_int("AUTOMATION_RETRIES", 1),
        automation_retry_delay_sec=_get_env_int("AUTOMATION_RETRY_DELAY_SEC", 5),
        automation_seed_demo=_get_env_bool("AUTOMATION_SEED_DEMO", False),
        whatsapp_webhook_url=os.getenv("WHATSAPP_WEBHOOK_URL", ""),
        whatsapp_to=os.getenv("WHATSAPP_TO", ""),
        whatsapp_sender=os.getenv("WHATSAPP_SENDER", ""),
        chat_mode=os.getenv("CHAT_MODE", "atendimento"),
        chat_loja_nome=os.getenv("CHAT_LOJA_NOME", "Drogarias Max - Barra Blue"),
        chat_endereco=os.getenv("CHAT_ENDERECO", "Av. das Americas, 12.700"),
        chat_filial=os.getenv("CHAT_FILIAL", "Barra Blue"),
        chat_reserva_validade=os.getenv("CHAT_RESERVA_VALIDADE", "fim do dia"),
        chat_delivery_rules=os.getenv("CHAT_DELIVERY_RULES", ""),
        chat_delivery_fallback=os.getenv(
            "CHAT_DELIVERY_FALLBACK", "vou consultar a taxa certinha e ja te retorno."
        ),
        chat_webhook_host=os.getenv("CHAT_WEBHOOK_HOST", "0.0.0.0"),
        chat_webhook_port=_get_env_int("CHAT_WEBHOOK_PORT", 8000),
        chat_session_dir=os.getenv("CHAT_SESSION_DIR", os.path.join("out", "chat_sessions")),
        low_stock_threshold=_get_env_int("LOW_STOCK_THRESHOLD", 10),
        integration_adapter=os.getenv("INTEGRATION_ADAPTER", "local"),
        integration_adapter_path=os.getenv("INTEGRATION_ADAPTER_PATH", ""),
        integration_webhook_url=os.getenv("INTEGRATION_WEBHOOK_URL", ""),
        scopes={
            "operational": _get_scopes("OPERATIONAL_SCOPES"),
            "audit": _get_scopes("AUDIT_SCOPES"),
            "strategist": _get_scopes("STRATEGIST_SCOPES"),
            "inventory": _get_scopes("INVENTORY_SCOPES"),
        },
    )
