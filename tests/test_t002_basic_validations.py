"""
Testes para T-002 — Validações Básicas (Categoria, Competência, Datas e Sanidade de Dados).
Atende: RN-007, RN-009, RN-012, RN-013, RN-014, AMB-005, AMB-007, AMB-011, AMB-012, AMB-013
"""
from datetime import date
from src.models import Periodo, DespesaItem
from src.engine import validar_despesa_basica, CATEGORIAS_VALIDAS


def test_validacao_categoria_invalida():
    """RN-009 / AMB-007: Categorias fora da política são recusadas."""
    periodo = Periodo("2026-07", date(2026, 7, 1), date(2026, 7, 31))
    despesa = DespesaItem("d-test", date(2026, 7, 5), "lazer", "Cinema", "CineMax", 5000, True)
    
    valida, motivo = validar_despesa_basica(despesa, periodo)
    assert not valida
    assert "Categoria não permitida" in motivo


def test_validacao_categoria_case_insensitive():
    """RN-009 / AMB-007: Comparação de categoria é insensível a maiúsculas/minúsculas."""
    periodo = Periodo("2026-07", date(2026, 7, 1), date(2026, 7, 31))
    despesa = DespesaItem("d-014", date(2026, 7, 31), "ALIMENTACAO", "Jantar", "Restaurante", 6100, True)
    
    valida, motivo = validar_despesa_basica(despesa, periodo)
    assert valida
    assert motivo == ""


def test_validacao_prazo_competencia_3_meses():
    """RN-007 / AMB-005: Despesas até 3 meses antes da competência são aceitas; anteriores são recusadas."""
    periodo = Periodo("2026-07", date(2026, 7, 1), date(2026, 7, 31))
    
    # 2026-04-15 está dentro da janela de 3 meses (abril a julho)
    despesa_abril = DespesaItem("d-008", date(2026, 4, 15), "alimentacao", "Almoço abril", "Tavola", 4100, True)
    valida, _ = validar_despesa_basica(despesa_abril, periodo)
    assert valida

    # 2026-03-31 tem mais de 3 meses de atraso
    despesa_marco = DespesaItem("d-old", date(2026, 3, 31), "alimentacao", "Almoço março", "Tavola", 4100, True)
    valida_old, motivo_old = validar_despesa_basica(despesa_marco, periodo)
    assert not valida_old
    assert "fora do prazo de competência" in motivo_old.lower()


def test_validacao_data_futura_ou_apos_periodo():
    """RN-013 / AMB-012: Despesas com data posterior ao fim do período da competência são recusadas."""
    periodo = Periodo("2026-07", date(2026, 7, 1), date(2026, 7, 31))
    despesa_futura = DespesaItem("d-fut", date(2026, 8, 1), "alimentacao", "Almoço agosto", "Tavola", 4100, True)
    
    valida, motivo = validar_despesa_basica(despesa_futura, periodo)
    assert not valida
    assert "posterior ao período" in motivo.lower()


def test_validacao_fim_de_semana_permitido():
    """RN-012 / AMB-011: Gastos em fins de semana (sábado/domingo) são válidos."""
    periodo = Periodo("2026-07", date(2026, 7, 1), date(2026, 7, 31))
    despesa_sabado = DespesaItem("d-012", date(2026, 7, 18), "alimentacao", "Plantão sábado", "Padaria", 4720, True)
    
    valida, motivo = validar_despesa_basica(despesa_sabado, periodo)
    assert valida
    assert motivo == ""


def test_validacao_valor_zero():
    """RN-014 / AMB-013: Despesas com valor zero (0.00) são recusadas por inconsistência."""
    periodo = Periodo("2026-07", date(2026, 7, 1), date(2026, 7, 31))
    despesa_zero = DespesaItem("d-zero", date(2026, 7, 10), "alimentacao", "Item zerado", "Loja", 0, True)
    
    valida, motivo = validar_despesa_basica(despesa_zero, periodo)
    assert not valida
    assert "inválido ou zerado" in motivo.lower()
