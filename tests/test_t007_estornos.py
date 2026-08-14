"""
Testes para T-007 — Processamento de Estornos (Valores Negativos).
Atende: RN-011, AMB-009
"""
from datetime import date
from src.models import DespesaItem
from src.engine import CalculadorLimitesDiarios


def test_estorno_abate_acumulado_diario():
    """RN-011 / AMB-009: Estornos (valores negativos) são aprovados como créditos e abatem do acumulado diário."""
    calculador = CalculadorLimitesDiarios()

    # d-009: Estorno de R$ -45.00 (-4500 centavos) no dia 2026-07-11 em transporte
    d009 = DespesaItem("d-009", date(2026, 7, 11), "transporte_urbano", "Estorno corrida", "TaxiApp", -4500, False)
    res_009 = calculador.processar_despesa(d009, limite_diario_centavos=8000)

    assert res_009.status == "APROVADO"
    assert res_009.valor_aprovado_centavos == -4500
    assert res_009.valor_recusado_centavos == 0

    # Verifica se o acumulado do dia no transporte ficou negativo (-4500 centavos)
    acumulado = calculador.acumulado_diario[(date(2026, 7, 11), "transporte_urbano")]
    assert acumulado == -4500

    # Lança corrida de R$ 100.00 (10000 centavos) no mesmo dia com nota fiscal
    # Teto R$ 80.00 (8000 centavos). Com estorno de -4500, o saldo disponível é 8000 - (-4500) = 12500 centavos!
    # A corrida de 10000 centavos cabe inteira no novo saldo disponível!
    d_corrida = DespesaItem("d-corrida", date(2026, 7, 11), "transporte_urbano", "Corrida longa", "TaxiApp", 10000, True)
    res_corrida = calculador.processar_despesa(d_corrida, limite_diario_centavos=8000)

    assert res_corrida.status == "APROVADO"
    assert res_corrida.valor_aprovado_centavos == 10000
