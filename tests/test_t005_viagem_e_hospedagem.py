"""
Testes para T-005 — Período 'Em Viagem' (+50% nos limites) e Múltiplas Diárias de Hospedagem.
Atende: RN-003, RN-006, AMB-004, AMB-010
"""
from datetime import date
from src.models import DespesaItem
from src.engine import extrair_quantidade_diarias, DetectorViagem, obter_limites_categoria


def test_extrair_quantidade_diarias():
    """AMB-010: Extração de diárias a partir da descrição ou fallback para 1."""
    assert extrair_quantidade_diarias("Hotel Rio - 2 diarias") == 2
    assert extrair_quantidade_diarias("Airbnb 3 noites") == 3
    assert extrair_quantidade_diarias("Hotel Executivo") == 1
    assert extrair_quantidade_diarias("Pousada 1 diária") == 1


def test_estado_viagem_amplia_limites_50_porcento():
    """RN-006 / AMB-004: Hospedagem válida ativa o período de viagem (+50% nos tetos)."""
    d010 = DespesaItem("d-010", date(2026, 7, 14), "hospedagem", "Hotel Rio - 2 diarias", "Hotel Copa Sul", 48000, True)
    
    detector = DetectorViagem()
    detector.registrar_hospedagens([d010])

    # No dia 2026-07-14 (dia da hospedagem), o colaborador está em viagem
    assert detector.estam_em_viagem(date(2026, 7, 14))
    # No dia 2026-07-15 (coberto pelas 2 diárias), o colaborador está em viagem
    assert detector.estam_em_viagem(date(2026, 7, 15))
    # No dia 2026-07-17 (fora das 2 diárias), o colaborador NÃO está em viagem
    assert not detector.estam_em_viagem(date(2026, 7, 17))

    # Limites em viagem (+50%):
    limite_alim_viagem = obter_limites_categoria("alimentacao", em_viagem=True)
    assert limite_alim_viagem == 9000  # R$ 90.00 (60.00 * 1.5)

    limite_transp_viagem = obter_limites_categoria("transporte_urbano", em_viagem=True)
    assert limite_transp_viagem == 12000  # R$ 120.00 (80.00 * 1.5)

    limite_hosp_viagem = obter_limites_categoria("hospedagem", em_viagem=True)
    assert limite_hosp_viagem == 37500  # R$ 375.00 (250.00 * 1.5)
