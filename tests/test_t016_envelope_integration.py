"""
Testes para T-016 — Teste de Integração Ponta a Ponta com despesas-envelope.json e despesas-envelope-cc-desconhecido.json.
Atende: Requisitos do Envelope Lacrado (Dia 2)
"""
import os
from src.parser import parse_input_file, GerenciadorCambio
from src.engine import processar_relatorio_despesas, GerenciadorPolitica
from src.formatter import construir_relatorio_saida


def test_integracao_envelope_comercial():
    """Valida o processamento completo do dataset despesas-envelope.json (CC-COMERCIAL)."""
    env_dir = os.path.join("exemplos", "envelope")
    input_file = os.path.join(env_dir, "despesas-envelope.json")
    pol_file = os.path.join(env_dir, "politica-v4.json")
    cam_file = os.path.join(env_dir, "cambio.json")

    cambio = GerenciadorCambio.carregar(cam_file)
    politica = GerenciadorPolitica.carregar(pol_file)

    colaborador, periodo, despesas = parse_input_file(input_file, cambio)
    assert len(despesas) == 10

    resultados = processar_relatorio_despesas(colaborador, periodo, despesas, politica)
    relatorio = construir_relatorio_saida(colaborador, periodo, resultados)

    assert relatorio["colaborador"]["centro_custo"] == "CC-COMERCIAL"
    assert relatorio["resumo"]["total_despesas"] == 10

    itens_map = {item["id"]: item for item in relatorio["itens"]}

    # e-001: representacao R$ 340.00 -> APROVADO_PARCIAL (teto R$ 300.00, recusado R$ 40.00)
    assert itens_map["e-001"]["status"] == "APROVADO_PARCIAL"
    assert itens_map["e-001"]["valor_aprovado"] == 300.00
    assert itens_map["e-001"]["valor_recusado"] == 40.00

    # e-002: 22 EUR em 14/07 (R$ 130.46 BRL sem viagem) -> APROVADO_PARCIAL (teto alimentacao R$ 90.00, cortado R$ 40.46)
    assert itens_map["e-002"]["status"] == "APROVADO_PARCIAL"
    assert itens_map["e-002"]["valor_aprovado"] == 90.00
    assert itens_map["e-002"]["valor_recusado"] == 40.46

    # e-003: 14.50 EUR em 15/07 sem NF (R$ 85.26 BRL) -> APROVADO (isento de NF e <= R$ 90.00 teto)
    assert itens_map["e-003"]["status"] == "APROVADO"

    # e-004: 30 EUR em 18/07 Sábado (R$ 178.80 BRL sem viagem) -> APROVADO_PARCIAL (teto alimentacao R$ 90.00)
    assert itens_map["e-004"]["status"] == "APROVADO_PARCIAL"
    assert itens_map["e-004"]["valor_aprovado"] == 90.00

    # e-005: 40 USD em 20/07 sem NF (R$ 220.00 BRL) -> RECUSADO por falta de NF
    assert itens_map["e-005"]["status"] == "RECUSADO"

    # e-006: 55 GBP sem cotação -> RECUSADO
    assert itens_map["e-006"]["status"] == "RECUSADO"

    # e-007: Hospedagem R$ 1200.00 3 noites -> APROVADO (teto 3 * R$ 400 = 1200) e ativa viagem de 22/07 a 24/07!
    assert itens_map["e-007"]["status"] == "APROVADO"

    # e-008: Almoco R$ 95.00 em 23/07 em viagem -> APROVADO (teto em viagem R$ 135.00)
    assert itens_map["e-008"]["status"] == "APROVADO"

    # e-009: Coworking R$ 120.00 em 24/07 -> APROVADO
    assert itens_map["e-009"]["status"] == "APROVADO"

    # e-010: Almoco R$ 88.00 em 27/07 sem viagem -> APROVADO (teto R$ 90.00)
    assert itens_map["e-010"]["status"] == "APROVADO"


def test_integracao_envelope_cc_desconhecido():
    """Valida o processamento do dataset despesas-envelope-cc-desconhecido.json (CC-SUPORTE-N2)."""
    env_dir = os.path.join("exemplos", "envelope")
    input_file = os.path.join(env_dir, "despesas-envelope-cc-desconhecido.json")
    pol_file = os.path.join(env_dir, "politica-v4.json")
    cam_file = os.path.join(env_dir, "cambio.json")

    cambio = GerenciadorCambio.carregar(cam_file)
    politica = GerenciadorPolitica.carregar(pol_file)

    colaborador, periodo, despesas = parse_input_file(input_file, cambio)
    assert len(despesas) == 4

    resultados = processar_relatorio_despesas(colaborador, periodo, despesas, politica)
    relatorio = construir_relatorio_saida(colaborador, periodo, resultados)

    itens_map = {item["id"]: item for item in relatorio["itens"]}

    # f-001: Almoco R$ 58.00 -> APROVADO (teto padrao R$ 60.00)
    assert itens_map["f-001"]["status"] == "APROVADO"

    # f-002: Hospedagem R$ 310.00 1 diaria -> APROVADO (teto em viagem R$ 375.00 = 250 * 1.5)
    assert itens_map["f-002"]["status"] == "APROVADO"
    assert itens_map["f-002"]["valor_aprovado"] == 310.00

    # f-003: Representacao R$ 190.00 em CC-SUPORTE-N2 -> RECUSADO (categoria não autorizada para o CC)
    assert itens_map["f-003"]["status"] == "RECUSADO"

    # f-004: Corrida 12 USD em 21/07 (R$ 65.76 BRL) -> APROVADO (teto transporte padrao R$ 80 BRL)
    assert itens_map["f-004"]["status"] == "APROVADO"
