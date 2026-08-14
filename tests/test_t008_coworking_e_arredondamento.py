"""
Testes para T-008 — Categoria Coworking, Arredondamento Half-Up e Precisão Decimal.
Atende: RN-009, RN-010, AMB-007, AMB-008
"""
from datetime import date
from src.parser import float_to_cents
from src.models import DespesaItem
from src.engine import CalculadorLimitesDiarios, validar_nota_fiscal, cents_to_float


def test_coworking_e_arredondamento_half_up():
    """RN-009, RN-010 / AMB-007, AMB-008: Coworking aprovado 100% (com NF); Float 33.333 convertido para 3333 centavos e de volta para 33.33."""
    # d-005: Coworking R$ 89.00 (8900 centavos) com NF -> Aprovado 100%
    d005 = DespesaItem("d-005", date(2026, 7, 7), "coworking", "Espaço compartilhado", "HubOffice", 8900, True)
    valida_nf, _ = validar_nota_fiscal(d005)
    assert valida_nf

    calculador = CalculadorLimitesDiarios()
    res_005 = calculador.processar_despesa(d005, limite_diario_centavos=None)
    assert res_005.status == "APROVADO"
    assert res_005.valor_aprovado_centavos == 8900

    # d-011: R$ 33.333 -> float_to_cents(33.333) = 3333 centavos -> cents_to_float(3333) = 33.33
    cents_011 = float_to_cents(33.333)
    assert cents_011 == 3333
    assert cents_to_float(cents_011) == 33.33
