"""
Testes para T-003 — Detecção e Tratamento de Duplicatas.
Atende: RN-008, AMB-006
"""
from datetime import date
from src.models import DespesaItem
from src.engine import DetectorDuplicatas


def test_desduplicacao_mantem_primeira_ocorrencia():
    """RN-008 / AMB-006: A primeira ocorrência de mesmo valor, data e categoria é mantida; posteriores são recusadas."""
    detector = DetectorDuplicatas()

    d006 = DespesaItem("d-006", date(2026, 7, 9), "alimentacao", "Almoço", "Bistrô Central", 5490, True)
    d007 = DespesaItem("d-007", date(2026, 7, 9), "alimentacao", "Almoço", "Bistrô Central", 5490, True)

    duplicada_006, motivo_006 = detector.verificar_e_registrar(d006)
    assert not duplicada_006
    assert motivo_006 == ""

    duplicada_007, motivo_007 = detector.verificar_e_registrar(d007)
    assert duplicada_007
    assert "duplicada" in motivo_007.lower()


def test_despesas_com_valores_ou_categorias_diferentes_nao_sao_duplicatas():
    """Valida que despesas na mesma data mas com valores ou categorias diferentes não são duplicatas."""
    detector = DetectorDuplicatas()

    d1 = DespesaItem("d-1", date(2026, 7, 9), "alimentacao", "Almoço", "Restaurante A", 5490, True)
    d2 = DespesaItem("d-2", date(2026, 7, 9), "alimentacao", "Jantar", "Restaurante B", 3800, True)
    d3 = DespesaItem("d-3", date(2026, 7, 9), "transporte_urbano", "Táxi", "TaxiApp", 5490, True)

    assert not detector.verificar_e_registrar(d1)[0]
    assert not detector.verificar_e_registrar(d2)[0]
    assert not detector.verificar_e_registrar(d3)[0]
