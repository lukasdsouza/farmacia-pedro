# AGENTS.md

## Visao Geral
Este repositorio define o ecossistema de agentes de IA do projeto farmacia-pedro. O objetivo e construir um swarm modular de agentes especializados conectados ao banco do ERP (leitura via SQL/API), habilitando automacao, analise de dados e suporte a decisao via WhatsApp.

## Prioridade Atual
Foque primeiro na **camada de leitura** (agentes que analisam e enviam relatorios). A **camada de escrita** (agentes que alteram precos ou aplicam bonificacoes) fica para a fase 2, somente apos validar a precisao.

## Arquitetura de Agentes (Swarms)
- Agente Operacional (WhatsApp): estoque e status de pedidos em tempo real para clientes/vendas.
- Agente de Auditoria de Entrada: leitura de XML/PDF de notas, compara com custo medio e alerta margem baixa.
- Agente Estrategista (BI + Brick): integra PowerBI/dados de venda para detectar queda de giro por regiao e comparar com precos do concorrente (via Google Search/grounding).
- Agente de Gestao de Estoque: sugestao de compras (giro + estoque de seguranca) e estoque parado com recomendacoes de remarcacao.
- Agente Executor (escrita): apos aprovacao explicita do dono via WhatsApp, pode escrever no ERP para alterar precos ou aplicar bonificacoes.

## Requisitos Tecnicos
- IA Core: Google Gemini 2.5 Flash (contexto + custo).
- Orquestrador: fluxo de automacao em Python (substitui n8n/Make).
- Conexao ERP:
  - Leitura via queries SQL (evitar sobrecarga).
  - Escrita via API do ERP ou automacao controlada do banco.
- Seguranca:
  - Humano-no-loop para qualquer escrita (sem mudanca autonoma de preco).
  - Log de todas as acoes dos agentes.
  - Acesso por perfil (ex: agente de vendas nao acessa dados de margem).

## Regras de Negocio (Prioridade)
- Regra de bonus: markup > 110% => aciona alerta de bonus para vendedores.
- Regra de giro: sem vendas por > XX dias => sugerir estrategia de queima.
- Regra de concorrencia: se preco do concorrente no Google < nosso preco => disparar analise de viabilidade de reajuste.

## Orientacao para Proximos Passos
- Comece pela extracao de dados e pipelines de relatorio.
- Defina esquemas e datasets minimos por agente antes das automacoes.
- Garanta que o fluxo de aprovacao no WhatsApp seja explicito e auditavel.
- Mantenha modulos desacoplados; agentes trocam sumarios, nao dados brutos.

## Mapa do Repo (demo)
- src/runner.py: Orquestra o swarm da camada de leitura e grava relatorios.
- src/automation/flow.py: Automacao em Python (agendamento + entrega).
- src/chat/engine.py: Chat pseudo-IA (atendimento via codigo).
- src/chat/integration.py: Adapter de integracao com sistemas externos.
- src/agents/: Agentes especializados (operacional, auditoria, estrategista, estoque).
- scripts/seed_demo_db.py: Cria um banco SQLite demo do ERP.
- scripts/run_demo.py: Gera relatorios em menos de 5 minutos.
- scripts/automation.py: Executa a automacao em Python.
- scripts/chat_cli.py: Inicia o atendimento via chat no terminal.
- scripts/chat_webhook.py: Webhook HTTP para integrar o chat com outros sistemas.
- out/: Relatorios e logs de auditoria.
- docs/: Arquitetura, contratos de dados, operacoes.

## Teste em 5 Minutos
1) python scripts\seed_demo_db.py
2) python scripts\run_demo.py
3) Abra out\report.md
