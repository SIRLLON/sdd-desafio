"""
Testes para T-006 — Controle de Acumulado Diário e Reembolso Parcial.
Atende: RN-001, RN-002, RN-004, AMB-001, AMB-002
"""
from datetime import date
from src.models import DespesaItem
from src.engine import CalculadorLimitesDiarios


def test_limite_diario_acumulado_e_reembolso_parcial():
    """RN-001, RN-004 / AMB-001, AMB-002: Processa d-001 (72.50) -> aprova 60.00 e corta 12.50; d-002 (38.00) -> recusa 100% por teto esgotado."""
    calculador = CalculadorLimitesDiarios()

    # d-001: R$ 72.50 (7250 centavos) no dia 2026-07-03 em alimentação (teto R$ 60.00 = 6000 centavos)
    d001 = DespesaItem("d-001", date(2026, 7, 3), "alimentacao", "Almoço", "Tavola", 7250, True)
    res_001 = calculador.processar_despesa(d001, limite_diario_centavos=6000)

    assert res_001.status == "APROVADO_PARCIAL"
    assert res_001.valor_aprovado_centavos == 6000
    assert res_001.valor_recusado_centavos == 1250
    assert "Aprovado parcialmente" in res_001.justificativas[0]

    # d-002: R$ 38.00 (3800 centavos) no mesmo dia (2026-07-03) em alimentação -> teto esgotado
    d002 = DespesaItem("d-002", date(2026, 7, 3), "alimentacao", "Jantar", "Cantina", 3800, True)
    res_002 = calculador.processar_despesa(d002, limite_diario_centavos=6000)

    assert res_002.status == "RECUSADO"
    assert res_002.valor_aprovado_centavos == 0
    assert res_002.valor_recusado_centavos == 3800
    assert "teto diário" in res_002.justificativas[0].lower()
