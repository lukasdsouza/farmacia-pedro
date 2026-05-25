import os
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from src.api.deps import get_current_user, get_settings
from src.api.models import ChatMessageRequest, ChatMessageResponse
from src.core.config import Settings

router = APIRouter(prefix="/api/chat", tags=["chat"])

_engine_cache: dict = {}


def _get_engine(settings: Settings):
    key = settings.db_path
    if key not in _engine_cache:
        anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
        groq_key = os.getenv("GROQ_API_KEY", "")
        openai_key = os.getenv("OPENAI_API_KEY", "")
        mode = os.getenv("CHAT_AI_MODE", "")

        if mode == "simulate" or anthropic_key == "simulate":
            from src.chat.simulated_engine import SimulatedChatEngine
            _engine_cache[key] = SimulatedChatEngine(settings)
        elif anthropic_key and anthropic_key != "simulate":
            from src.chat.ai_engine import AIChatEngine
            _engine_cache[key] = AIChatEngine(settings)
        elif groq_key or openai_key:
            from src.chat.groq_engine import GroqEngine
            _engine_cache[key] = GroqEngine(settings)
        else:
            from src.chat.simulated_engine import SimulatedChatEngine
            _engine_cache[key] = SimulatedChatEngine(settings)
    return _engine_cache[key]


@router.post("/message", response_model=ChatMessageResponse)
def send_message(body: ChatMessageRequest, settings: Settings = Depends(get_settings)):
    engine = _get_engine(settings)

    if body.customer_id:
        _prefill_customer_context(engine, body.session_id, body.customer_id, settings)

    reply = engine.handle_message(body.session_id, body.text)
    return ChatMessageResponse(ok=True, reply=reply, session_id=body.session_id)


def _prefill_customer_context(engine, session_id: str, customer_id: int, settings: Settings):
    from src.core.db import get_conn
    with get_conn(settings.db_path) as conn:
        row = conn.execute(
            "SELECT nome, telefone, endereco_rua, endereco_numero, "
            "endereco_complemento, endereco_bairro, endereco_cidade "
            "FROM customers WHERE id = ?", (customer_id,)
        ).fetchone()
    if not row:
        return
    # inject customer data into the engine session context
    if hasattr(engine, "_sessions"):
        ctx = engine._sessions.setdefault(session_id, {})
        if not ctx.get("customer_prefilled"):
            ctx["nome_cliente"] = row["nome"]
            ctx["telefone_cliente"] = row["telefone"] or ""
            partes = [row["endereco_rua"] or "", row["endereco_numero"] or ""]
            if row["endereco_complemento"]:
                partes.append(row["endereco_complemento"])
            if row["endereco_bairro"]:
                partes.append(row["endereco_bairro"])
            ctx["endereco_cliente"] = ", ".join(p for p in partes if p)
            ctx["bairro_cliente"] = row["endereco_bairro"] or ""
            ctx["customer_prefilled"] = True


@router.get("/sessions")
def list_sessions(
    settings: Settings = Depends(get_settings),
    user: dict = Depends(get_current_user),
):
    from src.chat.state import SessionStore
    store = SessionStore(settings.chat_session_dir)
    return {"sessions": store.list_sessions()}


@router.get("/sessions/{session_id}")
def get_session(
    session_id: str,
    settings: Settings = Depends(get_settings),
    user: dict = Depends(get_current_user),
):
    if len(session_id) > 128:
        raise HTTPException(status_code=400, detail="session_id muito longo")
    from src.chat.state import SessionStore
    store = SessionStore(settings.chat_session_dir)
    state = store.load(session_id)
    flow_state = store.load_state(session_id)
    return {
        "session_id": session_id,
        "messages": [{"role": m.role, "content": m.content} for m in state.messages],
        "flow_state": flow_state["state"],
        "flow_data": flow_state["data"],
    }
