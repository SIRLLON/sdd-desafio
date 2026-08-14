"""
Motor de cálculo de reembolso de despesas - Regras e Validações.
"""
from datetime import date
from typing import Tuple, Set
from src.models import Periodo, DespesaItem

CATEGORIAS_VALIDAS = {
    "alimentacao",
    "transporte_urbano",
    "transporte",
    "hospedagem",
    "coworking"
}


def calcular_diferenca_meses(data_despesa: date, inicio_competencia: date) -> int:
    """Calcula a diferença em meses calendários entre a data da despesa e o início da competência."""
    return (inicio_competencia.year - data_despesa.year) * 12 + (inicio_competencia.month - data_despesa.month)


def validar_despesa_basica(despesa: DespesaItem, periodo: Periodo) -> Tuple[bool, str]:
    """
    Executa validações básicas de sanidade (RN-007, RN-009, RN-012, RN-013, RN-014).
    Retorna (valida: bool, motivo_recusa: str).
    """
    # RN-014: Sanidade de dados e valor zerado (exceto estornos que possuem valor negativo)
    if despesa.valor_centavos == 0:
        return False, "Recusado: valor de despesa inválido ou zerado."

    # RN-009 / AMB-007: Validação de Categoria (case-insensitive)
    categoria_norm = despesa.categoria.strip().lower()
    if categoria_norm not in CATEGORIAS_VALIDAS:
        return False, f"Recusado: Categoria não permitida na política ('{despesa.categoria}')."

    # RN-013 / AMB-012: Data posterior ao fim da competência
    if despesa.data > periodo.fim:
        return False, f"Recusado: Data da despesa ({despesa.data}) é posterior ao período de competência ({periodo.fim})."

    # RN-007 / AMB-005: Prazo de competência (até 3 meses retroativos)
    # Ex: Competência 2026-07 (início 2026-07-01). Limite: 3 meses atrás (2026-04-01).
    meses_atraso = calcular_diferenca_meses(despesa.data, periodo.inicio)
    if meses_atraso > 3:
        return False, f"Recusado: Data da despesa ({despesa.data}) fora do prazo de competência (mais de 3 meses de atraso)."

    # RN-012 / AMB-011: Fins de semana são válidos
    return True, ""


class DetectorDuplicatas:
    """
    Detector determinístico de duplicatas por assinatura (Data, Categoria, Valor) (RN-008, AMB-006).
    Mantém a primeira ocorrência e recusa as posteriores.
    """
    def __init__(self):
        self.assinaturas_vistas: Set[Tuple[date, str, int]] = set()

    def verificar_e_registrar(self, despesa: DespesaItem) -> Tuple[bool, str]:
        """
        Retorna (duplicada: bool, motivo: str).
        Registra a assinatura se for inédita.
        """
        categoria_norm = despesa.categoria.strip().lower()
        assinatura = (despesa.data, categoria_norm, despesa.valor_centavos)

        if assinatura in self.assinaturas_vistas:
            return True, f"Recusado: Despesa duplicada (mesma data {despesa.data}, categoria '{despesa.categoria}' e valor)."

        self.assinaturas_vistas.add(assinatura)
        return False, ""
