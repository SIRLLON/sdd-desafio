"""
Testes para T-010 — Teste de Integração Ponta a Ponta com o dataset `exemplos/despesas-exemplo.json`.
Atende: Seção 9 da spec.md (Critérios de Aceite da Spec)
"""
import os
from src.parser import parse_input_file
from src.engine import processar_relatorio_despesas
from src.formatter import construir_relatorio_saida


def test_integracao_ponta_a_ponta_exemplo():
    """Processa o arquivo real despesas-exemplo.json e valida os totais e status de cada uma das 14 despesas."""
    filepath = os.path.join("exemplos", "despesas-exemplo.json")
    colaborador, periodo, despesas = parse_input_file(filepath)

    assert len(despesas) == 14

    resultados = processar_relatorio_despesas(colaborador, periodo, despesas)
    relatorio_saida = construir_relatorio_saida(colaborador, periodo, resultados)

    resumo = relatorio_saida["resumo"]
    assert resumo["total_despesas"] == 14
    assert resumo["total_solicitado"] == 1816.84
    assert resumo["total_aprovado"] == 820.43
    assert resumo["total_recusado"] == 996.41
    assert resumo["despesas_aprovadas"] == 9
    assert resumo["despesas_recusadas"] == 5

    # Mapeia resultados por id para verificação de cada item
    itens_map = {item["id"]: item for item in relatorio_saida["itens"]}

    # d-001: 72.50 alimentacao sem viagem (teto 60.00) -> APROVADO_PARCIAL (aprovado 60.00, recusado 12.50)
    assert itens_map["d-001"]["status"] == "APROVADO_PARCIAL"
    assert itens_map["d-001"]["valor_aprovado"] == 60.00
    assert itens_map["d-001"]["valor_recusado"] == 12.50

    # d-002: 38.00 alimentacao no mesmo dia -> RECUSADO (teto esgotado)
    assert itens_map["d-002"]["status"] == "RECUSADO"

    # d-003: 100.00 sem NF -> RECUSADO por ausência de NF
    assert itens_map["d-003"]["status"] == "RECUSADO"

    # d-004: 100.01 sem NF -> RECUSADO por ausência de NF
    assert itens_map["d-004"]["status"] == "RECUSADO"

    # d-005: 89.00 coworking com NF -> APROVADO
    assert itens_map["d-005"]["status"] == "APROVADO"
    assert itens_map["d-005"]["valor_aprovado"] == 89.00

    # d-006: 54.90 alimentacao -> APROVADO
    assert itens_map["d-006"]["status"] == "APROVADO"

    # d-007: 54.90 duplicata -> RECUSADO
    assert itens_map["d-007"]["status"] == "RECUSADO"

    # d-008: 41.00 alimentacao retroativa de abril em julho -> APROVADO (dentro dos 3 meses)
    assert itens_map["d-008"]["status"] == "APROVADO"

    # d-009: -45.00 estorno -> APROVADO
    assert itens_map["d-009"]["status"] == "APROVADO"

    # d-010: 480.00 hospedagem 2 diarias com NF -> APROVADO (ativa viagem de 14/07 a 15/07)
    assert itens_map["d-010"]["status"] == "APROVADO"

    # d-011: 33.333 alimentacao em viagem no dia 15/07 -> APROVADO 33.33
    assert itens_map["d-011"]["status"] == "APROVADO"
    assert itens_map["d-011"]["valor_aprovado"] == 33.33

    # d-012: 47.20 plantao de sabado -> APROVADO
    assert itens_map["d-012"]["status"] == "APROVADO"

    # d-013: 690.00 hospedagem sem NF -> RECUSADO por falta de NF
    assert itens_map["d-013"]["status"] == "RECUSADO"

    # d-014: 61.00 ALIMENTACAO sem viagem -> APROVADO_PARCIAL (teto 60.00: aprovado 60.00, recusado 1.00)
    assert itens_map["d-014"]["status"] == "APROVADO_PARCIAL"
    assert itens_map["d-014"]["valor_aprovado"] == 60.00
    assert itens_map["d-014"]["valor_recusado"] == 1.00
