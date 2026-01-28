# Chat (pseudo-IA)

Este chat simula um atendimento via codigo (sem usar API de IA). A logica e baseada em regras e consultas diretas ao banco.

Como rodar
1) python scripts\seed_demo_db.py
2) python scripts\chat_cli.py

Webhook (integracao com sistema existente)
1) python scripts\chat_webhook.py
2) Envie POST para http://localhost:8000/webhook com JSON:
   {"from": "cliente123", "text": "Tem dipirona?"}

Comandos
- ajuda
- estoque baixo
- sku MED001
- pedido status 1
- estoque parado
- sugestao de compra
- markup bonus
- sair

Integracao (porta aberta)
- Ajuste INTEGRATION_ADAPTER para "local" ou "webhook".
- Para integracao customizada, defina INTEGRATION_ADAPTER_PATH no formato modulo:Classe.
- O adapter deve implementar on_message e on_response. Veja src\chat\integration.py.

Sessao
- As conversas ficam em CHAT_SESSION_DIR (default: out\chat_sessions)
- Opcional: defina CHAT_SESSION_ID para nomear a sessao atual

Configuracoes do atendimento
- CHAT_MODE=atendimento (usa fluxo de cliente)
- CHAT_MODE=interno (usa comandos operacionais internos)
- CHAT_LOJA_NOME, CHAT_ENDERECO, CHAT_FILIAL (mensagens de saudacao)
- CHAT_RESERVA_VALIDADE (ex.: fim do dia)
- CHAT_DELIVERY_RULES (ex.: Recreio:8:60min;Barra:5:30min)
- CHAT_DELIVERY_FALLBACK (mensagem quando nao ha regra de entrega)
