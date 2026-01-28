# Operacoes

Demo em 5 minutos
1) python scripts\seed_demo_db.py
2) python scripts\run_demo.py

Automacao em Python (substitui n8n/Make)
1) copie .env.example para .env e ajuste os valores
2) execucao unica: python scripts\automation.py
3) agendado: ajuste AUTOMATION_MODE=agendado e rode python scripts\automation.py
   - use AUTOMATION_SEED_DEMO=1 para criar o banco demo

Artefatos
- out\report.json (dados estruturados)
- out\report.md (resumo humano)
- out\audit_log.jsonl (log de auditoria)
- out\chat_sessions (logs de conversa)

Proximas integracoes
- Conectar queries SQL do ERP em src\core\db.py
- Substituir competitor_prices por resultados de grounding do Google
- Conectar entrega no WhatsApp ao report.md

Base de dados ficticia (MySQL)
- Script: docs\sql\farmacia_mysql.sql

Chat (pseudo-IA)
- Guia: docs\CHAT.md
- Webhook: python scripts\chat_webhook.py
