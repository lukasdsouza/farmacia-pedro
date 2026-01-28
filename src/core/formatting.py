from datetime import datetime


def to_markdown(report: dict) -> str:
    lines = []
    lines.append("# Relatorio da Camada de Leitura")
    lines.append("")
    lines.append(f"Gerado em: {report.get('gerado_em')}")
    lines.append("")

    def section(title: str):
        lines.append(f"## {title}")
        lines.append("")

    section("Operacional")
    op = report.get("operacional", {})
    lines.append("### Estoque baixo")
    for item in op.get("estoque_baixo", []):
        lines.append(f"- {item['sku']} - {item['nome']} (estoque={item['estoque']})")
    lines.append("")
    lines.append("### Pedidos recentes")
    for item in op.get("pedidos_recentes", []):
        lines.append(f"- {item['pedido_id']} - {item['status']} - {item['cliente']}")
    lines.append("")

    section("Auditoria de Entrada")
    audit = report.get("auditoria_entrada", {})
    for item in audit.get("margem_baixa", []):
        lines.append(
            f"- {item['sku']} - {item['nome']} margem={item['margem_pct']}% custo_nota={item['custo_unitario']}"
        )
    lines.append("")

    section("Estrategista")
    strat = report.get("estrategista", {})
    lines.append("### Quedas de giro por regiao")
    for item in strat.get("quedas_giro", []):
        lines.append(
            f"- {item['regiao']} variacao={item['variacao_pct']}% (anterior={item['total_anterior']}, atual={item['total_atual']})"
        )
    lines.append("")
    lines.append("### Alertas de concorrencia")
    for item in strat.get("alertas_concorrencia", []):
        lines.append(
            f"- {item['sku']} - nosso={item['preco_nosso']} concorrente={item['concorrente']}:{item['preco_concorrente']}"
        )
    lines.append("")

    section("Estoque")
    inv = report.get("estoque", {})
    lines.append("### Estoque parado")
    for item in inv.get("estoque_parado", []):
        lines.append(
            f"- {item['sku']} - {item['nome']} ultima_venda={item['ultima_venda']} dias_sem_venda={item['dias_sem_venda']}"
        )
    lines.append("")
    lines.append("### Sugestoes de compra")
    for item in inv.get("recompras", []):
        lines.append(
            f"- {item['sku']} - {item['nome']} quantidade_recompra={item['quantidade_recompra']}"
        )
    lines.append("")

    section("Alertas de Regras de Negocio")
    rules = report.get("regras", {})
    for item in rules.get("alertas_bonus", []):
        lines.append(f"- Bonus: {item['sku']} - {item['nome']} markup={item['markup_pct']}%")
    lines.append("")

    return "\n".join(lines)
