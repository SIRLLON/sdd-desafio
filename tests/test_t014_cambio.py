"""
Testes para T-014 — Leitor de Cotações PTAX (cambio.json) e Conversão para Centavos BRL.
Atende: RN-018, RN-019, AMB-016, AMB-017, AMB-018, AMB-019
"""
import os
from datetime import date
from src.parser import GerenciadorCambio, float_to_cents


def test_conversao_moeda_ptax_e_fallback():
    """Valida conversão de moedas, fallback de cotação para fins de semana e recusa para moedas não cadastradas."""
    filepath = os.path.join("exemplos", "envelope", "cambio.json")
    cambio = GerenciadorCambio.carregar(filepath)

    # 1. BRL para qualquer data -> taxa 1.0 (22.00 BRL = 2200 centavos)
    assert cambio.obter_taxa("BRL", date(2026, 7, 14)) == 1.0

    # 2. EUR em 2026-07-14 -> taxa 5.93. (22.00 * 5.93 = 130.46 BRL -> 13046 centavos)
    taxa_eur = cambio.obter_taxa("EUR", date(2026, 7, 14))
    assert taxa_eur == 5.93
    cents_eur = float_to_cents(22.00 * taxa_eur)
    assert cents_eur == 13046

    # 3. EUR em 2026-07-18 (Sábado) -> Fallback para a cotação de 2026-07-17 (5.96)
    taxa_sabado = cambio.obter_taxa("EUR", date(2026, 7, 18))
    assert taxa_sabado == 5.96
    cents_sabado = float_to_cents(30.00 * taxa_sabado)
    assert cents_sabado == 17880

    # 4. GBP (Moeda não cadastrada) -> None (sem taxa)
    assert cambio.obter_taxa("GBP", date(2026, 7, 21)) is None
