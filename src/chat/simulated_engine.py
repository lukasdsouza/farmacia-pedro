"""
Simulação da Mariana sem usar API externa.
Ativa quando ANTHROPIC_API_KEY=simulate ou CHAT_AI_MODE=simulate.
Usa o banco de dados real mas respostas são geradas localmente.
"""
import json
import random
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from src.chat.data import SqliteGateway, ProdutoInfo
from src.chat.integration import load_adapter
from src.chat.state import SessionStore


# ──────────────────────────────────────────────
# Estados da conversa
# ──────────────────────────────────────────────
ESTADO_INICIO = "inicio"
ESTADO_AGUARDANDO = "aguardando"
ESTADO_PRODUTOS_ENCONTRADOS = "produtos_encontrados"
ESTADO_AGUARDANDO_QTD = "aguardando_qtd"
ESTADO_CARRINHO = "carrinho"
ESTADO_TIPO_ENTREGA = "tipo_entrega"
ESTADO_BAIRRO = "bairro"
ESTADO_ENDERECO = "endereco"
ESTADO_NOME = "nome"
ESTADO_CONFIRMANDO = "confirmando"
ESTADO_CONCLUIDO = "concluido"


# ──────────────────────────────────────────────
# Utilitários de texto
# ──────────────────────────────────────────────
def _normalizar(texto: str) -> str:
    t = texto.strip().lower()
    t = unicodedata.normalize("NFD", t)
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def _contem(texto: str, palavras: list[str]) -> bool:
    n = _normalizar(texto)
    return any(p in n for p in palavras)


def _extrair_numero(texto: str) -> Optional[int]:
    m = re.search(r"\b(\d+)\b", texto)
    return int(m.group(1)) if m else None


def _formatar_preco(valor: float) -> str:
    return f"R$ {valor:.2f}".replace(".", ",")


def _saudacao_hora() -> str:
    h = datetime.now().hour
    if h < 12:
        return "Bom dia"
    if h < 18:
        return "Boa tarde"
    return "Boa noite"


def _escolha_aleatoria(opcoes: list[str]) -> str:
    return random.choice(opcoes)


# ──────────────────────────────────────────────
# Parser de regras de entrega
# ──────────────────────────────────────────────
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


def _calcular_frete(bairro: str, rules: list[dict], fallback: str) -> dict:
    b = _normalizar(bairro)
    for r in rules:
        r_norm = _normalizar(r["bairro"])
        if r_norm in b or b in r_norm:
            return {"taxa": r["taxa"], "prazo": r["prazo"], "atende": True}
    return {"taxa": None, "prazo": None, "atende": False, "fallback": fallback}


# ──────────────────────────────────────────────
# Engine principal
# ──────────────────────────────────────────────
class SimulatedChatEngine:
    def __init__(self, settings):
        self.settings = settings
        self.store = SessionStore(settings.chat_session_dir)
        self.data = SqliteGateway(settings.db_path)
        self.adapter = load_adapter(settings)
        self.delivery_rules = _parse_delivery_rules(settings.chat_delivery_rules)
        self._sessions: dict[str, dict] = {}

    def handle_message(self, session_id: str, message: str) -> str:
        self.store.append(session_id, "user", message)
        self.adapter.on_message(session_id, message, {})

        ctx = self._load_ctx(session_id)
        reply = self._processar(ctx, message.strip())
        self._save_ctx(session_id, ctx)

        self.store.append(session_id, "assistant", reply)
        self.adapter.on_response(session_id, reply, {})
        return reply

    # ── contexto de sessão ──

    def _load_ctx(self, session_id: str) -> dict:
        if session_id not in self._sessions:
            saved = self.store.load_state(session_id)
            self._sessions[session_id] = saved.get("data", {}) or {}
            if not self._sessions[session_id].get("estado"):
                self._sessions[session_id]["estado"] = ESTADO_INICIO
        return self._sessions[session_id]

    def _save_ctx(self, session_id: str, ctx: dict):
        self._sessions[session_id] = ctx
        self.store.save_state(session_id, ctx.get("estado", ESTADO_INICIO), ctx)

    # ── roteador principal ──

    def _processar(self, ctx: dict, msg: str) -> str:
        estado = ctx.get("estado", ESTADO_INICIO)

        # atalhos globais
        if _contem(msg, ["cancelar", "cancela", "desistir", "tchau", "sair"]):
            ctx.clear()
            ctx["estado"] = ESTADO_INICIO
            return _escolha_aleatoria([
                "Tudo bem! Caso precise de algo, é só chamar 😊 Tenha um ótimo dia!",
                "Ok! Se precisar de mais alguma coisa, estarei aqui. Até logo! 👋",
            ])

        if _contem(msg, ["reiniciar", "comecar de novo", "recomecar"]):
            ctx.clear()
            ctx["estado"] = ESTADO_AGUARDANDO
            return "Claro! Vamos começar de novo. Em que posso te ajudar? 😊"

        if estado == ESTADO_INICIO:
            return self._handle_inicio(ctx, msg)
        if estado == ESTADO_AGUARDANDO:
            return self._handle_aguardando(ctx, msg)
        if estado == ESTADO_PRODUTOS_ENCONTRADOS:
            return self._handle_escolha_produto(ctx, msg)
        if estado == ESTADO_AGUARDANDO_QTD:
            return self._handle_quantidade(ctx, msg)
        if estado == ESTADO_CARRINHO:
            return self._handle_carrinho(ctx, msg)
        if estado == ESTADO_TIPO_ENTREGA:
            return self._handle_tipo_entrega(ctx, msg)
        if estado == ESTADO_BAIRRO:
            return self._handle_bairro(ctx, msg)
        if estado == ESTADO_ENDERECO:
            return self._handle_endereco(ctx, msg)
        if estado == ESTADO_NOME:
            return self._handle_nome(ctx, msg)
        if estado == ESTADO_CONFIRMANDO:
            return self._handle_confirmacao(ctx, msg)
        if estado == ESTADO_CONCLUIDO:
            ctx["estado"] = ESTADO_AGUARDANDO
            return "Posso te ajudar com mais alguma coisa? 😊"

        ctx["estado"] = ESTADO_AGUARDANDO
        return self._handle_aguardando(ctx, msg)

    # ── handlers por estado ──

    def _handle_inicio(self, ctx: dict, msg: str) -> str:
        ctx["estado"] = ESTADO_AGUARDANDO
        loja = self.settings.chat_loja_nome
        saud = _saudacao_hora()
        resp = (
            f"{saud}! 😊 Aqui é a Mariana, da {loja}. "
            f"Como posso te ajudar hoje? Pode me dizer o nome do produto que você precisa!"
        )
        # já pode ser uma pergunta
        if len(msg) > 3 and not _contem(msg, ["oi", "ola", "bom dia", "boa tarde", "boa noite", "boa noite", "tudo bem", "tudo bom"]):
            return self._handle_aguardando(ctx, msg)
        return resp

    def _handle_aguardando(self, ctx: dict, msg: str) -> str:
        saudacoes = {"oi", "ola", "ola", "bom dia", "boa tarde", "boa noite", "tudo bem",
                     "tudo bom", "hello", "hi", "boa", "bom"}
        msg_norm = _normalizar(msg)
        # só saudação pura → pede produto
        if msg_norm in saudacoes or (len(msg.split()) <= 2 and msg_norm in saudacoes):
            return _escolha_aleatoria([
                "Me diz o nome do produto que você está procurando que eu já te ajudo! 😊",
                "Pode me falar qual produto você precisa? Estou aqui pra te ajudar! 💊",
                "Qual produto você está buscando? É só me dizer o nome!",
            ])
        # qualquer outra coisa → tenta buscar como produto
        return self._buscar_produto(ctx, msg)

    def _buscar_produto(self, ctx: dict, msg: str) -> str:
        produtos = self.data.search_products(msg, limit=5)

        if not produtos:
            return (
                f"Hmm, não encontrei nada com \"{msg}\" no nosso estoque 😕 "
                "Pode tentar de outro jeito? Por exemplo, o nome genérico ou a marca?"
            )

        disponiveis = [p for p in produtos if p.estoque > 0]
        sem_estoque = [p for p in produtos if p.estoque == 0]

        if not disponiveis:
            # tudo sem estoque
            nomes = ", ".join(p.nome for p in sem_estoque[:3])
            # sugerir alternativas
            alts = self.data.suggest_alternatives(sem_estoque[0].categoria, sem_estoque[0].sku, limit=2)
            resp = f"Que pena! No momento estamos sem estoque de {nomes}. 😔\n"
            if alts:
                resp += "Mas tenho algumas alternativas que podem te ajudar:\n"
                for a in alts:
                    resp += f"• {a.nome} — {_formatar_preco(a.preco)}\n"
                resp += "\nAlguma dessas te serve?"
                ctx["estado"] = ESTADO_PRODUTOS_ENCONTRADOS
                ctx["produtos_encontrados"] = [{"sku": a.sku, "nome": a.nome, "preco": a.preco, "estoque": a.estoque} for a in alts]
            else:
                resp += "Infelizmente não tenho alternativas disponíveis agora. Posso buscar outro produto pra você?"
                ctx["estado"] = ESTADO_AGUARDANDO
            return resp

        if len(disponiveis) == 1:
            p = disponiveis[0]
            ctx["produto_atual"] = {"sku": p.sku, "nome": p.nome, "preco": p.preco, "estoque": p.estoque}
            ctx["estado"] = ESTADO_AGUARDANDO_QTD
            return (
                f"Encontrei! ✅\n"
                f"*{p.nome}*\n"
                f"Preço: {_formatar_preco(p.preco)}\n"
                f"Estoque disponível: {p.estoque} unid.\n\n"
                f"Quantas unidades você quer?"
            )

        # múltiplos resultados
        ctx["estado"] = ESTADO_PRODUTOS_ENCONTRADOS
        ctx["produtos_encontrados"] = [{"sku": p.sku, "nome": p.nome, "preco": p.preco, "estoque": p.estoque} for p in disponiveis]
        linhas = [f"{i+1}. {p.nome} — {_formatar_preco(p.preco)}" for i, p in enumerate(disponiveis)]
        return (
            "Encontrei algumas opções disponíveis 😊\n\n"
            + "\n".join(linhas)
            + "\n\nQual delas você quer? Pode digitar o número ou o nome!"
        )

    def _handle_escolha_produto(self, ctx: dict, msg: str) -> str:
        produtos = ctx.get("produtos_encontrados", [])
        if not produtos:
            ctx["estado"] = ESTADO_AGUARDANDO
            return self._handle_aguardando(ctx, msg)

        escolhido = None
        num = _extrair_numero(msg)
        if num and 1 <= num <= len(produtos):
            escolhido = produtos[num - 1]
        else:
            msg_norm = _normalizar(msg)
            for p in produtos:
                if _normalizar(p["nome"]) in msg_norm or any(w in msg_norm for w in _normalizar(p["nome"]).split() if len(w) > 3):
                    escolhido = p
                    break

        if not escolhido:
            nomes = "\n".join(f"{i+1}. {p['nome']}" for i, p in enumerate(produtos))
            return f"Não entendi qual você quer 😅 Pode digitar o número?\n\n{nomes}"

        ctx["produto_atual"] = escolhido
        ctx["estado"] = ESTADO_AGUARDANDO_QTD
        return (
            f"Ótima escolha! ✅ *{escolhido['nome']}* — {_formatar_preco(escolhido['preco'])}\n\n"
            "Quantas unidades você precisa?"
        )

    def _handle_quantidade(self, ctx: dict, msg: str) -> str:
        qty = _extrair_numero(msg)
        if not qty or qty <= 0:
            return "Não entendi a quantidade 😅 Me diz um número, tipo: *2* unidades."

        produto = ctx.get("produto_atual")
        if not produto:
            ctx["estado"] = ESTADO_AGUARDANDO
            return "Ops, perdi o fio da meada 😅 Qual produto você quer?"

        if qty > produto.get("estoque", 99):
            return (
                f"Poxa, só temos {produto['estoque']} unidade(s) em estoque 😕 "
                f"Posso separar {produto['estoque']} pra você?"
            )

        # adicionar ao carrinho
        carrinho = ctx.get("carrinho", [])
        item_existente = next((i for i in carrinho if i["sku"] == produto["sku"]), None)
        if item_existente:
            item_existente["quantidade"] += qty
        else:
            carrinho.append({"sku": produto["sku"], "nome": produto["nome"], "preco": produto["preco"], "quantidade": qty})
        ctx["carrinho"] = carrinho
        ctx["produto_atual"] = None
        ctx["estado"] = ESTADO_CARRINHO

        subtotal = sum(i["preco"] * i["quantidade"] for i in carrinho)
        resumo = "\n".join(f"• {i['quantidade']}x {i['nome']} — {_formatar_preco(i['preco'] * i['quantidade'])}" for i in carrinho)
        return (
            f"Adicionado ao carrinho! 🛒\n\n"
            f"{resumo}\n"
            f"*Subtotal: {_formatar_preco(subtotal)}*\n\n"
            "Quer adicionar mais algum produto ou prefere fechar o pedido?"
        )

    def _handle_carrinho(self, ctx: dict, msg: str) -> str:
        if _contem(msg, ["mais", "outro", "adicionar", "quero mais", "tbm", "tambem"]):
            ctx["estado"] = ESTADO_AGUARDANDO
            return "Claro! Me diz o próximo produto 😊"

        if _contem(msg, ["fechar", "finalizar", "confirmar", "pronto", "so isso", "pode fechar", "isso mesmo", "sim", "quero", "ok", "tudo"]):
            ctx["estado"] = ESTADO_TIPO_ENTREGA
            return (
                "Perfeito! 😊 Como você prefere receber?\n\n"
                "1. 🏪 *Retirada na loja* (pronto em ~30 min)\n"
                "2. 🛵 *Entrega* no seu endereço\n\n"
                "Pode digitar 1 ou 2!"
            )

        # pode ser busca de novo produto
        if len(msg) > 3:
            return self._buscar_produto(ctx, msg)

        return (
            "Quer adicionar mais algum produto ou fechar o pedido? 😊\n"
            "Digite o nome de outro produto ou diga *\"fechar\"*."
        )

    def _handle_bairro(self, ctx: dict, msg: str) -> str:
        frete = _calcular_frete(msg, self.delivery_rules, self.settings.chat_delivery_fallback)

        if not frete["atende"]:
            if frete.get("fallback"):
                ctx["bairro"] = msg
                ctx["taxa_entrega"] = 8.0  # taxa padrão
                ctx["estado"] = ESTADO_ENDERECO
                return (
                    f"Atendemos seu bairro sim! 😊 {frete['fallback']}\n"
                    "Pode me passar o *endereço completo* (rua, número, complemento)?"
                )

        ctx["bairro"] = msg
        ctx["taxa_entrega"] = frete["taxa"]
        ctx["prazo_entrega"] = frete.get("prazo", "45-60 minutos")
        ctx["estado"] = ESTADO_ENDERECO
        return (
            f"Entregamos no seu bairro! ✅\n"
            f"Taxa: {_formatar_preco(frete['taxa'])} | Prazo: {frete.get('prazo', '45-60 minutos')}\n\n"
            "Me passa o *endereço completo* (rua, número, complemento, ponto de referência)!"
        )

    def _handle_endereco(self, ctx: dict, msg: str) -> str:
        if len(msg) < 8:
            return "Preciso do endereço completo com rua e número 😊 Pode repetir?"
        ctx["endereco"] = msg
        ctx["estado"] = ESTADO_NOME
        return "Anotei! 📝 Agora me diz o seu *nome completo* pra eu registrar o pedido."

    def _handle_tipo_entrega(self, ctx: dict, msg: str) -> str:
        retirada = _contem(msg, ["1", "retirada", "retiro", "buscar", "busco", "loja", "pessoalmente"])
        entrega = _contem(msg, ["2", "entrega", "entregar", "manda", "mande", "delivery", "casa"])

        if retirada:
            ctx["tipo_entrega"] = "retirada"
            ctx["taxa_entrega"] = 0.0
            ctx["estado"] = ESTADO_NOME if not ctx.get("nome_cliente") else ESTADO_CONFIRMANDO
            end = self.settings.chat_endereco
            resposta = (
                f"Ótimo! 🏪 Pode retirar na nossa loja em:\n*{end}*\n"
                f"O pedido fica pronto em aproximadamente 30 minutos após confirmação.\n\n"
            )
            if ctx.get("nome_cliente"):
                return resposta + self._montar_confirmacao(ctx)
            return resposta + "Me diz o seu nome pra eu registrar o pedido!"

        if entrega:
            ctx["tipo_entrega"] = "entrega"
            # se já temos bairro do perfil, pular para endereço ou confirmação
            if ctx.get("bairro_cliente"):
                bairro = ctx["bairro_cliente"]
                frete = _calcular_frete(bairro, self.delivery_rules, self.settings.chat_delivery_fallback)
                ctx["taxa_entrega"] = frete.get("taxa") or 8.0
                ctx["prazo_entrega"] = frete.get("prazo") or "45-60 minutos"
                if ctx.get("endereco_cliente"):
                    ctx["endereco"] = ctx["endereco_cliente"]
                    ctx["estado"] = ESTADO_NOME if not ctx.get("nome_cliente") else ESTADO_CONFIRMANDO
                    if ctx.get("nome_cliente"):
                        return (
                            f"✅ Usando seu endereço cadastrado: *{ctx['endereco']}*\n"
                            f"Taxa de entrega: {_formatar_preco(ctx['taxa_entrega'])} | Prazo: {ctx['prazo_entrega']}\n\n"
                            + self._montar_confirmacao(ctx)
                        )
                    return (
                        f"✅ Usando seu endereço cadastrado: *{ctx['endereco']}*\n"
                        f"Taxa de entrega: {_formatar_preco(ctx['taxa_entrega'])}\n\n"
                        "Me diz seu nome pra finalizar!"
                    )
                ctx["estado"] = ESTADO_ENDERECO
                return (
                    f"Bairro: *{bairro}* | Taxa: {_formatar_preco(ctx['taxa_entrega'])}\n\n"
                    "Confirme o endereço completo de entrega (rua, número, complemento):"
                )
            ctx["estado"] = ESTADO_BAIRRO
            return "Ótimo! 🛵 Me diz o seu *bairro* pra eu verificar a taxa de entrega!"

        return "Não entendi 😅 Você prefere *retirada na loja* (1) ou *entrega* (2)?"

    def _handle_nome(self, ctx: dict, msg: str) -> str:
        if len(msg) < 2:
            return "Me diz seu nome pra eu registrar 😊"
        ctx["nome_cliente"] = msg.strip().title()
        ctx["estado"] = ESTADO_CONFIRMANDO
        return self._montar_confirmacao(ctx)

    def _montar_confirmacao(self, ctx: dict) -> str:
        carrinho = ctx.get("carrinho", [])
        subtotal = sum(i["preco"] * i["quantidade"] for i in carrinho)
        taxa = float(ctx.get("taxa_entrega", 0))
        total = subtotal + taxa

        itens_txt = "\n".join(
            f"  • {i['quantidade']}x {i['nome']} — {_formatar_preco(i['preco'] * i['quantidade'])}"
            for i in carrinho
        )

        tipo = ctx.get("tipo_entrega", "retirada")
        if tipo == "entrega":
            entrega_txt = (
                f"🛵 Entrega em: {ctx.get('endereco', '')}\n"
                f"  Taxa: {_formatar_preco(taxa)}"
            )
        else:
            entrega_txt = f"🏪 Retirada na loja"

        return (
            f"Perfeito, *{ctx.get('nome_cliente', '')}*! Confere seu pedido:\n\n"
            f"{itens_txt}\n\n"
            f"{entrega_txt}\n\n"
            f"*Total: {_formatar_preco(total)}*\n\n"
            "Está tudo certo? Posso confirmar o pedido? (sim/não)"
        )

    def _handle_confirmacao(self, ctx: dict, msg: str) -> str:
        if _contem(msg, ["sim", "confirma", "confirmar", "pode", "ok", "isso", "certo", "correto", "fecha"]):
            return self._registrar_pedido(ctx)

        if _contem(msg, ["nao", "não", "errado", "mudar", "alterar"]):
            ctx["estado"] = ESTADO_CARRINHO
            return (
                "Sem problema! O que você quer alterar?\n"
                "Pode me dizer um produto diferente ou digitar *\"fechar\"* quando estiver pronto."
            )

        return "Confirmo o pedido? Responde *sim* ou *não* 😊"

    def _registrar_pedido(self, ctx: dict) -> str:
        carrinho = ctx.get("carrinho", [])
        taxa = float(ctx.get("taxa_entrega", 0.0))
        total = sum(i["preco"] * i["quantidade"] for i in carrinho) + taxa

        data = {
            "nome_cliente": ctx.get("nome_cliente", ""),
            "telefone_cliente": "",
            "carrinho": carrinho,
            "delivery_type": ctx.get("tipo_entrega", "retirada"),
            "endereco_parcial": ctx.get("endereco", ""),
            "taxa_entrega": taxa,
        }
        try:
            order_id = self.data.save_customer_order(data)
        except Exception:
            order_id = 0

        tipo = ctx.get("tipo_entrega", "retirada")
        prazo = ctx.get("prazo_entrega", "30 minutos") if tipo == "retirada" else ctx.get("prazo_entrega", "45-60 minutos")

        ctx["estado"] = ESTADO_CONCLUIDO
        ctx["carrinho"] = []

        return (
            f"Pedido confirmado! 🎉 Número: *#{order_id}*\n\n"
            f"Total: *{_formatar_preco(total)}*\n"
            f"Prazo: {prazo}\n\n"
            f"Obrigada pela preferência, {ctx.get('nome_cliente', '')}! "
            f"Se precisar de mais alguma coisa, pode chamar 😊"
        )
