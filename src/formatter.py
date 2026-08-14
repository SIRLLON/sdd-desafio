"""
Formatador de relatórios de saída em dicionário/JSON conforme o esquema da spec.md.
"""
import json
from typing import List, Dict, Any
from src.models import Colaborador, Periodo, ResultadoItem
from src.parser import cents_to_float


def construir_relatorio_saida(
    colaborador: Colaborador,
    periodo: Periodo,
    resultados: List[ResultadoItem]
) -> Dict[str, Any]:
    """
    Constrói a estrutura do relatório final no formato especificado na Seção 4 da spec.md,
    efetuando o somatório bruto dos itens e convertendo valores em centavos para floats de 2 casas decimais.
    """
    total_solicitado_cents = sum(r.valor_solicitado_centavos for r in resultados)
    total_aprovado_cents = sum(r.valor_aprovado_centavos for r in resultados)
    total_recusado_cents = sum(r.valor_recusado_centavos for r in resultados)

    despesas_aprovadas = sum(1 for r in resultados if r.status in ("APROVADO", "APROVADO_PARCIAL"))
    despesas_recusadas = sum(1 for r in resultados if r.status == "RECUSADO")

    itens_saida = []
    for r in resultados:
        itens_saida.append({
            "id": r.id,
            "status": r.status,
            "valor_solicitado": cents_to_float(r.valor_solicitado_centavos),
            "valor_aprovado": cents_to_float(r.valor_aprovado_centavos),
            "valor_recusado": cents_to_float(r.valor_recusado_centavos),
            "justificativas": r.justificativas
        })

    return {
        "colaborador": {
            "id": colaborador.id,
            "nome": colaborador.nome,
            "centro_custo": colaborador.centro_custo
        },
        "periodo": {
            "competencia": periodo.competencia
        },
        "resumo": {
            "total_solicitado": cents_to_float(total_solicitado_cents),
            "total_aprovado": cents_to_float(total_aprovado_cents),
            "total_recusado": cents_to_float(total_recusado_cents),
            "total_despesas": len(resultados),
            "despesas_aprovadas": despesas_aprovadas,
            "despesas_recusadas": despesas_recusadas
        },
        "itens": itens_saida
    }


def salvar_relatorio_json(relatorio: Dict[str, Any], filepath: str) -> None:
    """Escreve a estrutura de dicionário em um arquivo JSON com formatação amigável."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)
