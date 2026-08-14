"""
Testes para T-015 — Validações de Pipeline com Moedas Convertidas e Validação de NF em BRL.
Atende: RN-005, RN-006, RN-018, RN-019, AMB-018, AMB-019
"""
import os
from src.parser import parse_input_file
from src.engine import processar_relatorio_despesas, GerenciadorPolitica


def test_pipeline_envelope_v4():
    """Testa obrigatoriedade de NF em BRL convertido e recusa de moeda não cadastrada sob a Política v4."""
    filepath = os.path.join("exemplos", "envelope", "despesas-envelope.json")
    politica_path = os.path.join("exemplos", "envelope", "politica-v4.json")
    
    colaborador, periodo, despesas = parse_input_file(filepath)
    gerenciador_politica = GerenciadorPolitica.carregar(politica_path)

    resultados = processar_relatorio_despesas(colaborador, periodo, despesas, gerenciador_politica)
    itens_map = {res.id: res for res in resultados}

    # e-003: 14.50 EUR (15/07) sem NF -> R$ 85.26 BRL (< R$ 100.00 é isenta) -> APROVADO
    assert itens_map["e-003"].status == "APROVADO"

    # e-005: 40.00 USD (20/07) sem NF -> R$ 220.00 BRL (>= R$ 100.00 exige NF) -> RECUSADO por falta de NF
    assert itens_map["e-005"].status == "RECUSADO"
    assert "Ausência de Nota Fiscal" in itens_map["e-005"].justificativas[0]

    # e-006: 55.00 GBP (21/07) sem taxa -> RECUSADO por moeda sem cotação
    assert itens_map["e-006"].status == "RECUSADO"
    assert "GBP" in itens_map["e-006"].justificativas[0]
