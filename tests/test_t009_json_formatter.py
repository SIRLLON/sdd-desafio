"""
Testes para T-009 — Formatação de Saída JSON e Resumo Consolidado.
Atende: Seção 4 da spec.md (Campos de Saída e Resumo)
"""
from datetime import date
from src.models import Colaborador, Periodo, ResultadoItem
from src.formatter import construir_relatorio_saida


def test_geracao_json_saida_estrutura():
    """Valida a estrutura do dicionário/JSON de saída e os totais consolidados do resumo."""
    colaborador = Colaborador("c-0417", "Marina Volpi", "CC-ENG-PLATAFORMA")
    periodo = Periodo("2026-07", date(2026, 7, 1), date(2026, 7, 31))

    itens = [
        ResultadoItem("d-001", "APROVADO_PARCIAL", 7250, 6000, 1250, ["Aprovado parcialmente até o teto diário."]),
        ResultadoItem("d-002", "RECUSADO", 3800, 0, 3800, ["Recusado: teto diário já atingido."]),
        ResultadoItem("d-005", "APROVADO", 8900, 8900, 0, ["Aprovado integralmente."])
    ]

    saida = construir_relatorio_saida(colaborador, periodo, itens)

    assert saida["colaborador"]["id"] == "c-0417"
    assert saida["periodo"]["competencia"] == "2026-07"
    
    resumo = saida["resumo"]
    # 72.50 + 38.00 + 89.00 = 199.50
    assert resumo["total_solicitado"] == 199.50
    # 60.00 + 0 + 89.00 = 149.00
    assert resumo["total_aprovado"] == 149.00
    # 12.50 + 38.00 + 0 = 50.50
    assert resumo["total_recusado"] == 50.50
    assert resumo["total_despesas"] == 3
    assert resumo["despesas_aprovadas"] == 2
    assert resumo["despesas_recusadas"] == 1

    assert len(saida["itens"]) == 3
    assert saida["itens"][0]["id"] == "d-001"
    assert saida["itens"][0]["valor_solicitado"] == 72.50
    assert saida["itens"][0]["valor_aprovado"] == 60.00
    assert saida["itens"][0]["valor_recusado"] == 12.50
