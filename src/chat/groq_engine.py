"""
Engine de chat usando qualquer API compatível com OpenAI (Groq, Ollama, OpenRouter...).
Ativa quando GROQ_API_KEY ou OPENAI_API_KEY estiver definida.

Configuração via variáveis de ambiente:
  GROQ_API_KEY=gsk_...          → usa Groq (grátis, recomendado)
  OPENAI_API_KEY=sk-...         → usa OpenAI ou outro serviço
  OPENAI_BASE_URL=http://...    → override da URL (ex: Ollama em localhost:11434/v1)
  CHAT_MODEL=llama-3.3-70b-versatile  → modelo a usar
"""
import json
import os
import re
import unicodedata
from typing import Any

import httpx
from openai import OpenAI

from src.chat.data import SqliteGateway
from src.chat.integration import load_adapter
from src.chat.state import SessionStore


_SYSTEM_PROMPT = """Você é Mariana, atendente da {loja_nome}, localizada em {endereco}.
Seu trabalho é atender clientes com calor humano, simpatia e eficiência — como uma boa atendente de farmácia faria pessoalmente.

Regras de comportamento:
- Fale SEMPRE em português do Brasil, de forma natural e descontraída, mas profissional.
- Use "você" ao se dirigir ao cliente.
- Nunca revele que é uma IA. Se perguntarem, diga que é a Mariana da farmácia.
- Respostas curtas e diretas (2-4 frases). Sem enrolação.
- Use emojis com moderação: 😊 ✅ 📦 🛵 💊
- Quando o cliente perguntar por produto, use SEMPRE a ferramenta buscar_produtos.
- Antes de fechar pedido, confirme itens, quantidade, entrega e nome do cliente.
- Para calcular frete, use calcular_frete com o bairro do cliente.
- Só registre o pedido com registrar_pedido após confirmação explícita.
- Produto sem estoque? Sugira alternativa da mesma categoria.
- Horário: 7h às 22h todos os dias.
- Retirada na loja: pronto em ~30 min. Entrega: 45–60 min.

Fluxo de pedido:
1. Busca produto → informa preço e estoque
2. Pergunta quantidade
3. Pergunta se retira ou quer entrega
4. Se entrega → pergunta bairro, calcula frete, confirma endereço
5. Pergunta nome do cliente
6. Confirma tudo (itens + total + entrega)
7. Registra pedido e informa o número
"""

_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "buscar_produtos",
            "description": "Busca produtos no catálogo da farmácia por nome ou descrição. Retorna nome, SKU, preço e estoque.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Nome ou descrição do produto (ex: 'dipirona', 'vitamina C 1g')"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "verificar_estoque",
            "description": "Verifica estoque de um produto pelo SKU.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sku": {
                        "type": "string",
                        "description": "Código SKU do produto (ex: 'MED001')"
                    }
                },
                "required": ["sku"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calcular_frete",
            "description": "Calcula taxa e prazo de entrega para um bairro.",
            "parameters": {
                "type": "object",
                "properties": {
                    "bairro": {
                        "type": "string",
                        "description": "Nome do bairro para entrega"
                    }
                },
                "required": ["bairro"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "registrar_pedido",
            "description": "Registra o pedido confirmado no sistema. Use SOMENTE após confirmação explícita do cliente.",
            "parameters": {
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
                    "nome_cliente": {"type": "string", "description": "Nome do cliente"},
                    "tipo_entrega": {
                        "type": "string",
                        "enum": ["retirada", "entrega"],
                        "description": "Forma de recebimento"
                    },
                    "endereco": {
                        "type": "string",
                        "description": "Endereço completo (obrigatório se entrega)"
                    },
                    "taxa_entrega": {
                        "type": "number",
                        "description": "Taxa de entrega em reais (0 para retirada)"
                    }
                },
                "required": ["itens", "nome_cliente", "tipo_entrega", "taxa_entrega"]
            }
        }
    }
]


def _parse_delivery_rules(rules_str: str) -> list[dict]:
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
                "prazo": fields[2].strip() if len(fields) > 2 else "45-60 minutos",
            })
    return rules


def _normalize(text: str) -> str:
    t = unicodedata.normalize("NFD", text.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9\s]", " ", t).strip()


class GroqEngine:
    def __init__(self, settings):
        self.settings = settings
        self.store = SessionStore(settings.chat_session_dir)
        self.data = SqliteGateway(settings.db_path)
        self.adapter = load_adapter(settings)
        self.delivery_rules = _parse_delivery_rules(settings.chat_delivery_rules)
        self._history: dict[str, list[dict]] = {}

        groq_key = os.getenv("GROQ_API_KEY", "")
        openai_key = os.getenv("OPENAI_API_KEY", "")
        base_url = os.getenv("OPENAI_BASE_URL", "")

        # Rede corporativa pode interceptar SSL — desabilita verificação
        _http = httpx.Client(verify=False)

        if groq_key:
            self.client = OpenAI(
                api_key=groq_key,
                base_url="https://api.groq.com/openai/v1",
                http_client=_http,
            )
            self.model = os.getenv("CHAT_MODEL", "llama-3.3-70b-versatile")
        elif openai_key:
            kwargs: dict = {"api_key": openai_key, "http_client": _http}
            if base_url:
                kwargs["base_url"] = base_url
            self.client = OpenAI(**kwargs)
            self.model = os.getenv("CHAT_MODEL", "gpt-4o-mini")
        else:
            raise RuntimeError("Defina GROQ_API_KEY ou OPENAI_API_KEY no .env")

    def handle_message(self, session_id: str, message: str) -> str:
        self.store.append(session_id, "user", message)
        self.adapter.on_message(session_id, message, {})

        history = self._history.setdefault(session_id, [])
        history.append({"role": "user", "content": message})

        system = _SYSTEM_PROMPT.format(
            loja_nome=self.settings.chat_loja_nome,
            endereco=self.settings.chat_endereco,
        )

        reply = self._run_loop(system, history, session_id)

        history.append({"role": "assistant", "content": reply})
        self.store.append(session_id, "assistant", reply)
        self.adapter.on_response(session_id, reply, {})
        return reply

    def _run_loop(self, system: str, history: list[dict], session_id: str) -> str:
        messages = [{"role": "system", "content": system}] + history

        for _ in range(10):  # limite de segurança: máx 10 rounds de tool calls
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=_TOOLS,
                tool_choice="auto",
                max_tokens=1024,
                temperature=0.7,
            )

            choice = resp.choices[0]

            if choice.finish_reason == "stop":
                return choice.message.content or "Desculpe, não entendi. Pode repetir?"

            if choice.finish_reason == "tool_calls":
                # adiciona a mensagem do assistente com tool_calls
                messages.append(choice.message)

                # executa cada tool call e adiciona o resultado
                for tc in choice.message.tool_calls:
                    try:
                        args = json.loads(tc.function.arguments)
                    except json.JSONDecodeError:
                        args = {}
                    result = self._execute_tool(tc.function.name, args, session_id)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result, ensure_ascii=False),
                    })
                continue

            # finish_reason inesperado (length, etc.)
            content = choice.message.content or ""
            return content if content else "Desculpe, não consegui processar. Pode repetir?"

        return "Desculpe, algo deu errado. Tente novamente."

    def _execute_tool(self, name: str, inputs: dict, session_id: str) -> Any:
        if name == "buscar_produtos":
            produtos = self.data.search_products(inputs.get("query", ""), limit=6)
            if not produtos:
                return {"encontrados": [], "mensagem": "Nenhum produto encontrado no catálogo"}
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
            item = self.data.stock_by_sku(inputs.get("sku", "").upper())
            if not item:
                return {"erro": f"Produto SKU '{inputs.get('sku')}' não encontrado"}
            return {"sku": item.sku, "nome": item.nome, "estoque": item.estoque, "disponivel": item.estoque > 0}

        if name == "calcular_frete":
            bairro = inputs.get("bairro", "").strip()
            b_norm = _normalize(bairro)
            for rule in self.delivery_rules:
                r_norm = _normalize(rule["bairro"])
                if r_norm in b_norm or b_norm in r_norm:
                    return {"bairro": bairro, "taxa": rule["taxa"], "prazo": rule["prazo"], "atende": True}
            return {
                "bairro": bairro,
                "taxa": None,
                "prazo": None,
                "atende": False,
                "mensagem": self.settings.chat_delivery_fallback,
            }

        if name == "registrar_pedido":
            itens = inputs.get("itens", [])
            taxa = float(inputs.get("taxa_entrega", 0))
            total = sum(float(i["preco"]) * int(i["quantidade"]) for i in itens) + taxa
            data = {
                "session_id": session_id,
                "nome_cliente": inputs.get("nome_cliente", ""),
                "telefone_cliente": "",
                "carrinho": itens,
                "delivery_type": inputs.get("tipo_entrega", "retirada"),
                "endereco_parcial": inputs.get("endereco", ""),
                "taxa_entrega": taxa,
            }
            try:
                order_id = self.data.save_customer_order(data)
                return {"sucesso": True, "pedido_id": order_id, "total": round(total, 2)}
            except Exception as exc:
                return {"sucesso": False, "erro": str(exc)}

        return {"erro": f"Ferramenta desconhecida: {name}"}
