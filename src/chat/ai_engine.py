"""
Claude-powered chat engine that replaces the rule-based state machine.
Active when ANTHROPIC_API_KEY is set in the environment.
"""
import json
import os
from datetime import datetime, timezone
from typing import Any

import anthropic

from src.chat.data import SqliteGateway
from src.chat.integration import load_adapter
from src.chat.state import SessionStore


_SYSTEM_PROMPT = """Você é Mariana, atendente da {loja_nome}, localizada em {endereco}.
Seu trabalho é atender clientes com calor humano, simpatia e eficiência — como uma boa atendente de farmácia faria pessoalmente.

Regras de comportamento:
- Fale sempre em português do Brasil, de forma natural e descontraída, mas profissional.
- Use "você" ao se dirigir ao cliente.
- Nunca revele que é uma IA. Se perguntarem, diga apenas que é a Mariana da farmácia.
- Mantenha as respostas curtas e diretas (2-4 frases quando possível).
- Use emojis com moderação para soar mais humana: 😊 ✅ 📦 🛵 💊
- Quando o cliente perguntar por um produto, SEMPRE use a ferramenta buscar_produtos primeiro.
- Antes de fechar um pedido, confirme os itens, quantidade, forma de entrega e nome do cliente.
- Para calcular frete, use calcular_frete com o bairro informado pelo cliente.
- Só registre o pedido com registrar_pedido quando o cliente confirmar tudo.
- Se um produto estiver sem estoque, sugira alternativas da mesma categoria.
- Horário de funcionamento: 7h às 22h todos os dias.
- Para retirada na loja, o prazo é de 30 minutos após confirmação.
- Para entrega, o prazo padrão é de 45 a 60 minutos.

Fluxo típico de pedido:
1. Cliente pergunta pelo produto → você busca e informa preço/estoque
2. Cliente quer comprar → pergunta quantidade
3. Cliente quer mais produtos ou vai fechar → pergunta se retira ou quer entrega
4. Se entrega → pergunta o bairro, calcula taxa, confirma endereço completo
5. Pede o nome do cliente
6. Confirma todo o pedido (itens + qtd + total + forma de entrega)
7. Registra o pedido e informa o número
"""

_TOOLS: list[dict[str, Any]] = [
    {
        "name": "buscar_produtos",
        "description": "Busca produtos no catálogo da farmácia por nome ou descrição. Retorna nome, SKU, preço e estoque disponível.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Nome ou descrição do produto a buscar (ex: 'dipirona', 'vitamina C 1g')"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "verificar_estoque",
        "description": "Verifica o estoque disponível de um produto específico pelo SKU.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sku": {
                    "type": "string",
                    "description": "Código SKU do produto (ex: 'MED001')"
                }
            },
            "required": ["sku"]
        }
    },
    {
        "name": "calcular_frete",
        "description": "Calcula a taxa e o prazo de entrega para um determinado bairro.",
        "input_schema": {
            "type": "object",
            "properties": {
                "bairro": {
                    "type": "string",
                    "description": "Nome do bairro para entrega"
                }
            },
            "required": ["bairro"]
        }
    },
    {
        "name": "registrar_pedido",
        "description": "Registra o pedido confirmado pelo cliente no sistema. Use apenas após confirmação explícita do cliente.",
        "input_schema": {
            "type": "object",
            "properties": {
                "itens": {
                    "type": "array",
                    "description": "Lista de itens do pedido",
                    "items": {
                        "type": "object",
                        "properties": {
                            "sku": {"type": "string"},
                            "nome": {"type": "string"},
                            "quantidade": {"type": "integer"},
                            "preco": {"type": "number"}
                        },
                        "required": ["sku", "nome", "quantidade", "preco"]
                    }
                },
                "nome_cliente": {
                    "type": "string",
                    "description": "Nome do cliente"
                },
                "tipo_entrega": {
                    "type": "string",
                    "enum": ["retirada", "entrega"],
                    "description": "Forma de recebimento do pedido"
                },
                "endereco": {
                    "type": "string",
                    "description": "Endereço completo de entrega (obrigatório se tipo_entrega = entrega)"
                },
                "taxa_entrega": {
                    "type": "number",
                    "description": "Taxa de entrega em reais (0 para retirada)"
                }
            },
            "required": ["itens", "nome_cliente", "tipo_entrega", "taxa_entrega"]
        }
    }
]


def _parse_delivery_rules(rules_str: str) -> list[dict]:
    """Parse 'bairro:taxa:prazo;bairro2:taxa2:prazo2' into list of dicts."""
    if not rules_str.strip():
        return []
    rules = []
    for part in rules_str.split(";"):
        part = part.strip()
        if not part:
            continue
        fields = part.split(":")
        if len(fields) >= 2:
            rules.append({
                "bairro": fields[0].strip().lower(),
                "taxa": float(fields[1].strip()),
                "prazo": fields[2].strip() if len(fields) > 2 else "45-60 minutos"
            })
    return rules


class AIChatEngine:
    def __init__(self, settings):
        self.settings = settings
        self.store = SessionStore(settings.chat_session_dir)
        self.data = SqliteGateway(settings.db_path)
        self.adapter = load_adapter(settings)
        self.delivery_rules = _parse_delivery_rules(settings.chat_delivery_rules)
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self._history: dict[str, list[dict]] = {}

    def handle_message(self, session_id: str, message: str) -> str:
        self.store.append(session_id, "user", message)
        self.adapter.on_message(session_id, message, {})

        if session_id not in self._history:
            self._history[session_id] = []
        self._history[session_id].append({"role": "user", "content": message})

        system = _SYSTEM_PROMPT.format(
            loja_nome=self.settings.chat_loja_nome,
            endereco=self.settings.chat_endereco,
        )

        messages = self._history[session_id]
        response = self._run_agent_loop(system, messages, session_id)

        self._history[session_id].append({"role": "assistant", "content": response})
        self.store.append(session_id, "assistant", response)
        self.adapter.on_response(session_id, response, {})
        return response

    def _run_agent_loop(self, system: str, messages: list[dict], session_id: str) -> str:
        current_messages = list(messages)

        while True:
            resp = self.client.messages.create(
                model="claude-opus-4-7",
                max_tokens=1024,
                system=system,
                tools=_TOOLS,
                messages=current_messages,
            )

            if resp.stop_reason == "end_turn":
                return self._extract_text(resp)

            if resp.stop_reason == "tool_use":
                tool_results = []
                for block in resp.content:
                    if block.type == "tool_use":
                        result = self._execute_tool(block.name, block.input, session_id)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result, ensure_ascii=False),
                        })

                current_messages = current_messages + [
                    {"role": "assistant", "content": resp.content},
                    {"role": "user", "content": tool_results},
                ]
                continue

            return self._extract_text(resp)

    def _extract_text(self, resp) -> str:
        parts = []
        for block in resp.content:
            if hasattr(block, "text"):
                parts.append(block.text)
        return " ".join(parts).strip() or "Desculpe, não entendi. Pode repetir?"

    def _execute_tool(self, name: str, inputs: dict, session_id: str) -> Any:
        if name == "buscar_produtos":
            produtos = self.data.search_products(inputs["query"], limit=5)
            if not produtos:
                return {"encontrados": [], "mensagem": "Nenhum produto encontrado"}
            return {
                "encontrados": [
                    {
                        "sku": p.sku,
                        "nome": p.nome,
                        "categoria": p.categoria,
                        "preco": p.preco,
                        "disponivel": p.estoque > 0,
                        "estoque": p.estoque,
                    }
                    for p in produtos
                ]
            }

        if name == "verificar_estoque":
            item = self.data.stock_by_sku(inputs["sku"].upper())
            if not item:
                return {"erro": f"Produto com SKU {inputs['sku']} não encontrado"}
            return {"sku": item.sku, "nome": item.nome, "estoque": item.estoque, "disponivel": item.estoque > 0}

        if name == "calcular_frete":
            bairro = inputs["bairro"].strip().lower()
            import unicodedata, re
            bairro_norm = unicodedata.normalize("NFD", bairro)
            bairro_norm = "".join(c for c in bairro_norm if unicodedata.category(c) != "Mn")
            bairro_norm = re.sub(r"[^a-z0-9\s]", " ", bairro_norm).strip()

            for rule in self.delivery_rules:
                rule_norm = unicodedata.normalize("NFD", rule["bairro"])
                rule_norm = "".join(c for c in rule_norm if unicodedata.category(c) != "Mn")
                rule_norm = re.sub(r"[^a-z0-9\s]", " ", rule_norm).strip()
                if rule_norm in bairro_norm or bairro_norm in rule_norm:
                    return {"bairro": inputs["bairro"], "taxa": rule["taxa"], "prazo": rule["prazo"], "atende": True}

            fallback = self.settings.chat_delivery_fallback
            return {"bairro": inputs["bairro"], "taxa": None, "prazo": None, "atende": False, "mensagem": fallback}

        if name == "registrar_pedido":
            total = sum(float(i["preco"]) * int(i["quantidade"]) for i in inputs["itens"])
            total += float(inputs.get("taxa_entrega", 0))
            data = {
                "session_id": session_id,
                "nome_cliente": inputs["nome_cliente"],
                "telefone_cliente": "",
                "carrinho": inputs["itens"],
                "delivery_type": inputs["tipo_entrega"],
                "endereco_parcial": inputs.get("endereco", ""),
                "taxa_entrega": float(inputs.get("taxa_entrega", 0)),
            }
            try:
                order_id = self.data.save_customer_order(data)
                return {"sucesso": True, "pedido_id": order_id, "total": round(total, 2)}
            except Exception as exc:
                return {"sucesso": False, "erro": str(exc)}

        return {"erro": f"Ferramenta desconhecida: {name}"}
