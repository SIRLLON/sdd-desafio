"""
Motor de cálculo de reembolso de despesas - Regras e Validações.
"""
import json
import os
import re
from datetime import date, timedelta
from typing import Tuple, Set, List, Dict, Optional
from src.models import Colaborador, Periodo, DespesaItem, ResultadoItem
from src.parser import cents_to_float, float_to_cents

CATEGORIAS_VALIDAS = {
    "alimentacao",
    "transporte_urbano",
    "transporte",
    "hospedagem",
    "coworking",
    "representacao"
}

LIMITE_ISENCAO_NOTA_FISCAL_CENTAVOS = 10000  # R$ 100.00 em BRL (valores >= 10000 exigem NF)

# Tetos Padrão (Sem Viagem) em Centavos (Fallback v3)
LIMITES_PADRAO_CENTAVOS = {
    "alimentacao": 6000,        # R$ 60.00
    "transporte_urbano": 8000,  # R$ 80.00
    "transporte": 8000,         # R$ 80.00
    "hospedagem": 25000,        # R$ 250.00 por diária
    "coworking": None           # Sem teto especificado
}

FATOR_AMPLIACAO_VIAGEM = 1.5  # +50% nos limites em viagem (RN-006)


class GerenciadorPolitica:
    """
    RN-015, RN-016, RN-017 / AMB-014, AMB-015: Gerencia os limites por Centro de Custo carregados de politica-v4.json.
    """
    def __init__(self, padrao: Dict[str, Optional[int]], centros_custo: Dict[str, Dict[str, Optional[int]]]):
        self.padrao = padrao
        self.centros_custo = centros_custo

    @classmethod
    def carregar(cls, filepath: str) -> "GerenciadorPolitica":
        if not os.path.exists(filepath):
            # Fallback se o arquivo de política v4 não for informado
            return cls(
                padrao={k: v for k, v in LIMITES_PADRAO_CENTAVOS.items()},
                centros_custo={}
            )

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        padrao_dict: Dict[str, Optional[int]] = {}
        for cat, info in data.get("padrao", {}).items():
            cat_norm = cat.strip().lower()
            limite = info.get("limite")
            padrao_dict[cat_norm] = float_to_cents(limite) if limite is not None else None

        # Coworking sem teto por padrão se não listado
        if "coworking" not in padrao_dict:
            padrao_dict["coworking"] = None

        centros_custo_dict: Dict[str, Dict[str, Optional[int]]] = {}
        for cc, cats in data.get("centros_custo", {}).items():
            cc_norm = cc.strip().upper()
            centros_custo_dict[cc_norm] = {}
            for cat, info in cats.items():
                cat_norm = cat.strip().lower()
                limite = info.get("limite")
                centros_custo_dict[cc_norm][cat_norm] = float_to_cents(limite) if limite is not None else None

        return cls(padrao=padrao_dict, centros_custo=centros_custo_dict)

    def obter_limite_centavos(self, centro_custo: str, categoria: str, em_viagem: bool = False) -> Optional[int]:
        """
        Retorna o limite em centavos para o Centro de Custo e Categoria.
        Retorna int se houver teto (0 para proibido), None se sem teto (ex: coworking), ou `UNAUTHORIZED` se não permitida.
        """
        cc_norm = centro_custo.strip().upper()
        cat_norm = categoria.strip().lower()

        teto_centavos: Optional[int] = None
        teto_encontrado = False

        if cc_norm in self.centros_custo and cat_norm in self.centros_custo[cc_norm]:
            teto_centavos = self.centros_custo[cc_norm][cat_norm]
            teto_encontrado = True
        elif cat_norm in self.padrao:
            teto_centavos = self.padrao[cat_norm]
            teto_encontrado = True

        if not teto_encontrado:
            return None  # Categoria não cadastrada no CC nem no padrão

        if teto_centavos is None:
            return None

        if teto_centavos == 0:
            return 0  # Proibido (limite 0.00)

        if em_viagem:
            return int(teto_centavos * FATOR_AMPLIACAO_VIAGEM)

        return teto_centavos


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
    Executa validações básicas de sanidade (RN-007, RN-009, RN-012, RN-013, RN-014, RN-018).
    Retorna (valida: bool, motivo_recusa: str).
    """
    # RN-018 / AMB-017: Moeda estrangeira sem cotação de câmbio disponível
    if despesa.moeda != "BRL" and despesa.valor_centavos == 0 and despesa.valor_original > 0:
        return False, f"Recusado: Sem taxa de câmbio disponível para a moeda '{despesa.moeda}'."

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
        valor_fmt = f"{cents_to_float(despesa.valor_centavos):.2f}"
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

    def registrar_hospedagens(self, despesas: List[DespesaItem], gerenciador_politica: Optional[GerenciadorPolitica] = None, centro_custo: str = "") -> None:
        """
        Analisa a lista de despesas e mapeia todos os dias sob cobertura de hospedagem.
        """
        for d in despesas:
            cat_norm = d.categoria.strip().lower()
            if cat_norm == "hospedagem":
                if d.valor_centavos >= LIMITE_ISENCAO_NOTA_FISCAL_CENTAVOS and not d.tem_nota_fiscal:
                    continue
                
                if gerenciador_politica:
                    limite_hosp = gerenciador_politica.obter_limite_centavos(centro_custo, "hospedagem")
                    if limite_hosp == 0:
                        continue  # Hospedagem proibida no CC não ativa viagem (AMB-015)

                num_diarias = extrair_quantidade_diarias(d.descricao)
                for dia_offset in range(num_diarias):
                    dia_coberto = d.data + timedelta(days=dia_offset)
                    self.dias_em_viagem.add(dia_coberto)

    def estam_em_viagem(self, data_despesa: date) -> bool:
        """Retorna True se o dia da despesa estiver dentro de um período em viagem."""
        return data_despesa in self.dias_em_viagem


class CalculadorLimitesDiarios:
    """
    RN-001, RN-002, RN-003, RN-004, RN-011 / AMB-001, AMB-002, AMB-009: Controle de acumulado diário, estornos e reembolso parcial.
    """
    def __init__(self):
        # Mapeia (data, categoria_norm) -> acumulado_centavos
        self.acumulado_diario: Dict[Tuple[date, str], int] = {}

    def processar_despesa(self, despesa: DespesaItem, limite_diario_centavos: int | None) -> ResultadoItem:
        """
        Aplica os limites diários sobre a despesa e atualiza o acumulado do dia.
        Trata estornos (valores negativos - RN-011).
        """
        cat_norm = despesa.categoria.strip().lower()
        chave = (despesa.data, cat_norm)
        acumulado_atual = self.acumulado_diario.get(chave, 0)

        # RN-011 / AMB-009: Estornos (valores negativos)
        if despesa.valor_centavos < 0:
            self.acumulado_diario[chave] = acumulado_atual + despesa.valor_centavos
            return ResultadoItem(
                id=despesa.id,
                status="APROVADO",
                valor_solicitado_centavos=despesa.valor_centavos,
                valor_aprovado_centavos=despesa.valor_centavos,
                valor_recusado_centavos=0,
                justificativas=["Estorno / crédito aprovado integralmente."]
            )

        # RN-016: Se o limite for R$ 0,00 -> Proibido para o Centro de Custo
        if limite_diario_centavos == 0:
            return ResultadoItem(
                id=despesa.id,
                status="RECUSADO",
                valor_solicitado_centavos=despesa.valor_centavos,
                valor_aprovado_centavos=0,
                valor_recusado_centavos=despesa.valor_centavos,
                justificativas=[f"Recusado: categoria '{despesa.categoria}' não é reembolsável para o centro de custo."]
            )

        # Se for hospedagem com múltiplas diárias, ajusta o limite aplicável
        if cat_norm == "hospedagem" and limite_diario_centavos is not None:
            num_diarias = extrair_quantidade_diarias(despesa.descricao)
            limite_diario_centavos = limite_diario_centavos * num_diarias

        # Se não há limite para a categoria (ex: coworking), aprova 100%
        if limite_diario_centavos is None:
            self.acumulado_diario[chave] = acumulado_atual + despesa.valor_centavos
            return ResultadoItem(
                id=despesa.id,
                status="APROVADO",
                valor_solicitado_centavos=despesa.valor_centavos,
                valor_aprovado_centavos=despesa.valor_centavos,
                valor_recusado_centavos=0,
                justificativas=["Aprovado integralmente."]
            )

        saldo_disponivel = limite_diario_centavos - acumulado_atual

        # Se o teto já estiver completamente esgotado
        if saldo_disponivel <= 0:
            return ResultadoItem(
                id=despesa.id,
                status="RECUSADO",
                valor_solicitado_centavos=despesa.valor_centavos,
                valor_aprovado_centavos=0,
                valor_recusado_centavos=despesa.valor_centavos,
                justificativas=[f"Recusado: teto diário da categoria '{despesa.categoria}' já atingido na data."]
            )

        # Se o valor cabe integralmente no saldo disponível
        if despesa.valor_centavos <= saldo_disponivel:
            self.acumulado_diario[chave] = acumulado_atual + despesa.valor_centavos
            return ResultadoItem(
                id=despesa.id,
                status="APROVADO",
                valor_solicitado_centavos=despesa.valor_centavos,
                valor_aprovado_centavos=despesa.valor_centavos,
                valor_recusado_centavos=0,
                justificativas=["Aprovado integralmente."]
            )

        # Se o valor excede o saldo disponível -> Reembolso Parcial (RN-004)
        valor_aprovado = saldo_disponivel
        valor_recusado = despesa.valor_centavos - valor_aprovado
        self.acumulado_diario[chave] = limite_diario_centavos

        teto_fmt = f"{cents_to_float(limite_diario_centavos):.2f}"
        return ResultadoItem(
            id=despesa.id,
            status="APROVADO_PARCIAL",
            valor_solicitado_centavos=despesa.valor_centavos,
            valor_aprovado_centavos=valor_aprovado,
            valor_recusado_centavos=valor_recusado,
            justificativas=[f"Aprovado parcialmente até o teto diário de {despesa.categoria} (R$ {teto_fmt}). Excedente cortado."]
        )


def processar_relatorio_despesas(
    colaborador: Colaborador,
    periodo: Periodo,
    despesas: List[DespesaItem],
    gerenciador_politica: Optional[GerenciadorPolitica] = None
) -> List[ResultadoItem]:
    """
    Executa a pipeline completa de avaliação determinística de reembolso na ordem da Seção 8 da spec.md v2.0.
    Se gerenciador_politica for None, utiliza os limites padrão v3 para manter retrocompatibilidade.
    """
    detector_viagem = DetectorViagem()
    detector_viagem.registrar_hospedagens(despesas, gerenciador_politica, colaborador.centro_custo)

    detector_duplicatas = DetectorDuplicatas()
    calculador_limites = CalculadorLimitesDiarios()

    resultados: List[ResultadoItem] = []

    for d in despesas:
        # Step 1: Validações básicas (Categoria, Prazos, Sanidade)
        valida_basica, motivo_basica = validar_despesa_basica(d, periodo)
        if not valida_basica:
            resultados.append(ResultadoItem(
                id=d.id,
                status="RECUSADO",
                valor_solicitado_centavos=d.valor_centavos,
                valor_aprovado_centavos=0,
                valor_recusado_centavos=d.valor_centavos,
                justificativas=[motivo_basica]
            ))
            continue

        # Step 2: Detecção de Categoria Autorizada para o CC (RN-017 / AMB-014)
        cat_norm = d.categoria.strip().lower()
        if gerenciador_politica is not None:
            limite_base = gerenciador_politica.obter_limite_centavos(colaborador.centro_custo, cat_norm)
            if limite_base is None and cat_norm != "coworking":
                resultados.append(ResultadoItem(
                    id=d.id,
                    status="RECUSADO",
                    valor_solicitado_centavos=d.valor_centavos,
                    valor_aprovado_centavos=0,
                    valor_recusado_centavos=d.valor_centavos,
                    justificativas=[f"Recusado: Categoria '{d.categoria}' não autorizada para o centro de custo '{colaborador.centro_custo}'."]
                ))
                continue

        # Step 3: Detecção de Duplicatas
        duplicada, motivo_duplicada = detector_duplicatas.verificar_e_registrar(d)
        if duplicada:
            resultados.append(ResultadoItem(
                id=d.id,
                status="RECUSADO",
                valor_solicitado_centavos=d.valor_centavos,
                valor_aprovado_centavos=0,
                valor_recusado_centavos=d.valor_centavos,
                justificativas=[motivo_duplicada]
            ))
            continue

        # Step 4: Validação de Comprovante Fiscal
        valida_nf, motivo_nf = validar_nota_fiscal(d)
        if not valida_nf:
            resultados.append(ResultadoItem(
                id=d.id,
                status="RECUSADO",
                valor_solicitado_centavos=d.valor_centavos,
                valor_aprovado_centavos=0,
                valor_recusado_centavos=d.valor_centavos,
                justificativas=[motivo_nf]
            ))
            continue

        # Step 5: Determinação de Limite Elegível e Estado de Viagem
        em_viagem = detector_viagem.estam_em_viagem(d.data)
        if gerenciador_politica is not None:
            limite_diario = gerenciador_politica.obter_limite_centavos(colaborador.centro_custo, d.categoria, em_viagem)
        else:
            limite_diario = obter_limites_categoria(d.categoria, em_viagem)

        # Step 6: Cálculo do Limite Acumulado e Reembolso Parcial/Total
        res = calculador_limites.processar_despesa(d, limite_diario)
        resultados.append(res)

    return resultados
