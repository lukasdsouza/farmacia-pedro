import os
import re
from typing import Optional, Tuple

from src.chat.data import SqliteGateway
from src.chat.flow_atendimento import AtendimentoFlow
from src.chat.integration import load_adapter
from src.chat.state import SessionStore
from src.core.config import load_settings


class ChatEngine:
    def __init__(self, settings):
        self.settings = settings
        self.store = SessionStore(settings.chat_session_dir)
        self.data = SqliteGateway(settings.db_path)
        self.adapter = load_adapter(settings)
        self.atendimento = AtendimentoFlow(settings, self.data)

    def handle_message(self, session_id: str, message: str) -> str:
        history = self.store.load(session_id)
        state_payload = self.store.load_state(session_id)
        state = state_payload.get("state", "START")
        data = state_payload.get("data", {})

        self.store.append(session_id, "user", message)
        self.adapter.on_message(session_id, message, {"total": len(history.messages)})

        if self.settings.chat_mode == "atendimento":
            response, new_state, new_data = self.atendimento.handle(state, data, message)
        else:
            response = self._route_internal(message.strip().lower())
            new_state, new_data = state, data

        self.store.append(session_id, "assistant", response)
        self.adapter.on_response(session_id, response, {"total": len(history.messages) + 1})
        self.store.save_state(session_id, new_state, new_data)
        return response

    def _route_internal(self, msg: str) -> str:
        if msg in {"sair", "exit", "quit"}:
            return "Encerrando atendimento."

        if any(word in msg for word in ["ajuda", "menu", "comandos"]):
            return self._help()

        sku = self._extract_sku(msg)
        if sku:
            item = self.data.stock_by_sku(sku)
            if not item:
                return f"Nao encontrei o SKU {sku}."
            return f"SKU {item.sku} - {item.nome}: estoque={item.estoque}."

        if "estoque baixo" in msg or "baixo estoque" in msg:
            itens = self.data.low_stock(self.settings.low_stock_threshold)
            if not itens:
                return "Nao ha itens com estoque baixo."
            linhas = [f"- {i.sku} {i.nome} (estoque={i.estoque})" for i in itens]
            return "Estoque baixo:\n" + "\n".join(linhas)

        if "pedido" in msg and "status" in msg:
            pedido_id = self._extract_number(msg)
            if not pedido_id:
                pedidos = self.data.recent_orders(5)
                if not pedidos:
                    return "Nao encontrei pedidos recentes."
                linhas = [f"- {p.pedido_id} {p.status} ({p.cliente})" for p in pedidos]
                return "Pedidos recentes:\n" + "\n".join(linhas)
            pedido = self.data.order_status(pedido_id)
            if not pedido:
                return f"Nao encontrei o pedido {pedido_id}."
            return f"Pedido {pedido.pedido_id}: status={pedido.status} cliente={pedido.cliente}."

        if "estoque parado" in msg or "dead stock" in msg or "sem venda" in msg:
            itens = self.data.dead_stock(self.settings.days_no_sales)
            if not itens:
                return "Nao ha estoque parado acima do limite."
            linhas = [
                f"- {i.sku} {i.nome} ultima_venda={i.ultima_venda} dias_sem_venda={i.dias_sem_venda}"
                for i in itens
            ]
            return "Estoque parado:\n" + "\n".join(linhas)

        if "recompra" in msg or "comprar" in msg or "sugestao" in msg:
            itens = self.data.reorder_suggestions(self.settings.safety_stock_days)
            if not itens:
                return "Nao ha sugestoes de compra no momento."
            linhas = [
                f"- {i.sku} {i.nome} quantidade_recompra={i.quantidade_recompra}" for i in itens
            ]
            return "Sugestoes de compra:\n" + "\n".join(linhas)

        if "markup" in msg or "bonus" in msg:
            itens = self.data.bonus_alerts(self.settings.bonus_markup_pct)
            if not itens:
                return "Nenhum item com markup acima do limite."
            linhas = [f"- {i.sku} {i.nome} markup={i.markup_pct}%" for i in itens]
            return "Alertas de bonus:\n" + "\n".join(linhas)

        if "relatorio" in msg or "report" in msg:
            return "Para relatorio completo, rode: python scripts\\run_demo.py"

        return (
            "Nao entendi. Digite 'ajuda' para ver os comandos. "
            "Exemplos: 'estoque baixo', 'pedido status 2', 'sku MED001'."
        )

    def _extract_number(self, msg: str) -> Optional[int]:
        match = re.search(r"\b(\d+)\b", msg)
        if not match:
            return None
        try:
            return int(match.group(1))
        except ValueError:
            return None

    def _extract_sku(self, msg: str) -> Optional[str]:
        match = re.search(r"\b([A-Z]{2,5}-?\d{2,4})\b", msg.upper())
        if match:
            return match.group(1)
        return None

    def _help(self) -> str:
        return (
            "Comandos internos:\n"
            "- ajuda\n"
            "- estoque baixo\n"
            "- sku MED001\n"
            "- pedido status 1\n"
            "- estoque parado\n"
            "- sugestao de compra\n"
            "- markup bonus\n"
            "- sair"
        )


def run_cli():
    settings = load_settings()
    engine = ChatEngine(settings)
    session_id = os.getenv("CHAT_SESSION_ID", "atendimento")

    modo = settings.chat_mode
    print(f"Chat iniciado (modo: {modo}). Digite 'ajuda' ou 'sair' para encerrar.")
    while True:
        try:
            message = input("voce> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando atendimento.")
            break
        if not message:
            continue
        response = engine.handle_message(session_id, message)
        print(f"ia> {response}")
        if response.lower().startswith("encerrando"):
            break


if __name__ == "__main__":
    run_cli()
