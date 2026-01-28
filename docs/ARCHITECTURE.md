# Arquitetura

Objetivo
- Fornecer um swarm modular de IA conectado aos dados do ERP para automacao, analise e suporte a decisao via WhatsApp.
- Priorizar a camada de leitura primeiro. A camada de escrita e uma fase separada com aprovacao explicita.

Camadas principais
1) Camada de dados (somente leitura na fase 1)
   - Queries SQL no ERP (demo usa SQLite).
   - API do ERP opcional para leitura.

2) Camada de swarm (agentes especializados)
   - Operacional: estoque + status de pedidos para vendas/clientes.
   - Auditoria de Entrada: custo de nota vs custo medio, alertas de margem baixa.
   - Estrategista: queda de giro por regiao + gaps de preco do concorrente.
   - Estoque: estoque parado + sugestoes de compra.
   - Executor: acoes de escrita (desabilitado na fase 1).

3) Orquestracao
   - Automacao em Python agenda, roteia e entrega relatorios.
   - Runner coleta a saida de cada agente e grava os artefatos.

4) Entrega
   - WhatsApp (fase 1 simulada via markdown).
   - Futuro: integracao com API do WhatsApp e fluxo de aprovacao.

Seguranca
- Humano-no-loop: acoes de escrita exigem aprovacao explicita.
- Escopos por papel/agent (variaveis de ambiente).
- Log de auditoria para geracao de relatorios e futuras acoes de escrita.

Fluxo de dados (fase 1)
ERP SQL -> Analise do agente -> Relatorio JSON/MD -> Resumo no WhatsApp
