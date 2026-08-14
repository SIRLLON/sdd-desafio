"""
Testes para T-004 — Obrigatoriedade de Comprovante Fiscal (Nota Fiscal).
Atende: RN-005, AMB-003
"""
from datetime import date
from src.models import DespesaItem
from src.engine import validar_nota_fiscal


def test_comprovante_fiscal_obrigatorio_acima_100():
    """RN-005 / AMB-003: Valores >= R$ 100,00 exigem Nota Fiscal. Valores <= R$ 99,99 são isentos."""
    # R$ 100.00 (10000 centavos) sem nota -> Recusada
    d003 = DespesaItem("d-003", date(2026, 7, 6), "transporte_urbano", "Corrida aeroporto", "TaxiApp", 10000, False)
    valida_003, motivo_003 = validar_nota_fiscal(d003)
    assert not valida_003
    assert "nota fiscal" in motivo_003.lower()

    # R$ 100.01 (10001 centavos) sem nota -> Recusada
    d004 = DespesaItem("d-004", date(2026, 7, 6), "transporte_urbano", "Corrida hotel", "TaxiApp", 10001, False)
    valida_004, motivo_004 = validar_nota_fiscal(d004)
    assert not valida_004
    assert "nota fiscal" in motivo_004.lower()

    # R$ 99.99 (9999 centavos) sem nota -> Aprovada (isenta)
    d_isenta = DespesaItem("d-isenta", date(2026, 7, 6), "transporte_urbano", "Corrida curta", "TaxiApp", 9999, False)
    valida_isenta, motivo_isenta = validar_nota_fiscal(d_isenta)
    assert valida_isenta
    assert motivo_isenta == ""

    # R$ 100.00 com nota -> Aprovada
    d_com_nota = DespesaItem("d-com-nota", date(2026, 7, 6), "transporte_urbano", "Corrida aeroporto", "TaxiApp", 10000, True)
    valida_com_nota, motivo_com_nota = validar_nota_fiscal(d_com_nota)
    assert valida_com_nota
    assert motivo_com_nota == ""
