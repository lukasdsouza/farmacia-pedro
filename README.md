# farmacia-pedro - Swarm de IA (camada de leitura)

Inicio rapido (<=5 min)

1) Criar banco demo do ERP
   python scripts\seed_demo_db.py

2) Rodar swarm da camada de leitura
   python scripts\run_demo.py

3) Teste de fumaca (opcional)
   python scripts\smoke_test.py

Automacao em Python (substitui n8n/Make)
1) copie .env.example para .env e ajuste os valores
2) python scripts\automation.py
   - use AUTOMATION_SEED_DEMO=1 para criar o banco demo

Chat pseudo-IA (atendimento local)
1) python scripts\seed_demo_db.py
2) python scripts\chat_cli.py

Chat pseudo-IA via webhook (integracao)
1) python scripts\chat_webhook.py
2) POST http://localhost:8000/webhook com {"from":"cliente1","text":"Tem dipirona?"}

Saidas
- out\report.json
- out\report.md
- out\audit_log.jsonl

Notas
- Demo local somente leitura usando SQLite.
- Camada de escrita (executor) esta desabilitada e requer aprovacao explicita via WhatsApp.
- Configure via .env (veja .env.example). O runner carrega .env automaticamente se existir.
