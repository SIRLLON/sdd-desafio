"""
Motor de cálculo de reembolso de despesas - Regras e Validações.
"""
import re
from datetime import date, timedelta
from typing import Tuple, Set, List
from src.models import Periodo, DespesaItem

CATEGORIAS_VALIDAS = {
    "alimentacao",
    "transporte_urbano",
    "transporte",
    "hospedagem",
    "coworking"
}

LIMITE_ISENCAO_NOTA_FISCAL_CENTAVOS = 10000  # R$ 100.00 (valores >= 10000 exigem NF)

# Tetos Padrão (Sem Viagem) em Centavos
LIMITES_PADRAO_CENTAVOS = {
    "alimentacao": 6000,        # R$ 60.00
    "transporte_urbano": 8000,  # R$ 80.00
    "transporte": 8000,         # R$ 80.00
    "hospedagem": 25000,        # R$ 250.00 por diária
    "coworking": None           # Sem teto especificado
}

FATOR_AMPLIACAO_VIAGEM = 1.5  # +50% nos limites em viagem (RN-006)


def calcular_diferenca_meses(data_despesa: date, inicio_competencia: date) -> int:
    """Calcula a diferença em meses calendários entre a data da despesa e o início da competência."""
    return (inicio_competencia.year - data_despesa.year) * 12 + (inicio_competencia.month - data_despesa.month)


def extrair_quantidade_diarias(descricao: str) -> int:
    """
    AMB-010: Extrai o número de diárias/noites da descrição da despesa de hospedagem.
    Retorna 1 por padrão se não for explicitado.
    Ex: 'Hotel Rio - 2 diarias' -> 2, 'Airbnb 3 noites' -> 3
    """
    match = re.search(r'(\d+)\s*(?:di[áa]rias?|noites?)', descricao, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 1


def obter_limites_categoria(categoria: str, em_viagem: bool = False) -> int | None:
    """
    Retorna o limite em centavos para a categoria.
    Aplica o acréscimo de 50% (`FATOR_AMPLIACAO_VIAGEM`) se `em_viagem` for True.
    """
    cat_norm = categoria.strip().lower()
    teto_base = LIMITES_PADRAO_CENTAVOS.get(cat_norm)
    if teto_base is None:
        return None
    if em_viagem:
        return int(teto_base * FATOR_AMPLIACAO_VIAGEM)
    return teto_base


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
    meses_atraso = calcular_diferenca_meses(despesa.data, periodo.inicio)
    if meses_atraso > 3:
        return False, f"Recusado: Data da despesa ({despesa.data}) fora do prazo de competência (mais de 3 meses de atraso)."

    # RN-012 / AMB-011: Fins de semana são válidos
    return True, ""


def validar_nota_fiscal(despesa: DespesaItem) -> Tuple[bool, str]:
    """
    RN-005 / AMB-003: Valida a obrigatoriedade de Nota Fiscal para valores >= R$ 100,00 (10000 centavos).
    Retorna (valida: bool, motivo_recusa: str).
    """
    if despesa.valor_centavos >= LIMITE_ISENCAO_NOTA_FISCAL_CENTAVOS and not despesa.tem_nota_fiscal:
        valor_fmt = f"{despesa.valor_centavos / 100:.2f}"
        return False, f"Recusado: Ausência de Nota Fiscal obrigatória para despesa de R$ {valor_fmt} (exigida para valores >= R$ 100,00)."
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


class DetectorViagem:
    """
    RN-006 / AMB-004: Detecta o estado de 'Em Viagem' baseado na presença de despesas de hospedagem elegíveis.
    """
    def __init__(self):
        self.dias_em_viagem: Set[date] = set()

    def registrar_hospedagens(self, despesas: List[DespesaItem]) -> None:
        """
        Analisa a lista de despesas e mapeia todos os dias sob cobertura de hospedagem.
        """
        for d in despesas:
            cat_norm = d.categoria.strip().lower()
            if cat_norm == "hospedagem":
                # Verifica se a hospedagem seria reprovada na NF antes de contar como viagem
                if d.valor_centavos >= LIMITE_ISENCAO_NOTA_FISCAL_CENTAVOS and not d.tem_nota_fiscal:
                    continue
                
                num_diarias = extrair_quantidade_diarias(d.descricao)
                for dia_offset in range(num_diarias):
                    dia_coberto = d.data + timedelta(days=dia_offset)
                    self.dias_em_viagem.add(dia_coberto)

    def estam_em_viagem(self, data_despesa: date) -> bool:
        """Retorna True se o dia da despesa estiver dentro de um período em viagem."""
        return data_despesa in self.dias_em_viagem
