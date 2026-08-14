"""
Parser de arquivo JSON de entrada e utilitários monetários para conversão em centavos.
"""
import json
import os
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Tuple, List
from src.models import Colaborador, Periodo, DespesaItem


def float_to_cents(value: float) -> int:
    """
    Converte um valor numérico monetário em float para inteiro em centavos
    utilizando arredondamento matemático padrão (half-up).
    Ex: 72.50 -> 7250, 33.333 -> 3333
    """
    d = Decimal(str(value))
    cents = (d * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(cents)


def parse_input_file(filepath: str) -> Tuple[Colaborador, Periodo, List[DespesaItem]]:
    """
    Lê e valida a existência e estrutura de um arquivo JSON de despesas.
    Retorna os objetos fortemente tipados: Colaborador, Periodo e lista de DespesaItem.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {filepath}")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Formato JSON inválido no arquivo {filepath}: {e}")
    except Exception as e:
        raise ValueError(f"Erro ao ler arquivo {filepath}: {e}")

    colaborador_raw = data.get("colaborador", {})
    colaborador = Colaborador(
        id=str(colaborador_raw.get("id", "")),
        nome=str(colaborador_raw.get("nome", "")),
        centro_custo=str(colaborador_raw.get("centro_custo", ""))
    )

    periodo_raw = data.get("periodo", {})
    inicio_dt = datetime.strptime(periodo_raw.get("inicio", "1970-01-01"), "%Y-%m-%d").date()
    fim_dt = datetime.strptime(periodo_raw.get("fim", "1970-01-01"), "%Y-%m-%d").date()
    periodo = Periodo(
        competencia=str(periodo_raw.get("competencia", "")),
        inicio=inicio_dt,
        fim=fim_dt
    )

    despesas: List[DespesaItem] = []
    for d in data.get("despesas", []):
        data_dt = datetime.strptime(d.get("data", "1970-01-01"), "%Y-%m-%d").date()
        despesa_item = DespesaItem(
            id=str(d.get("id", "")),
            data=data_dt,
            categoria=str(d.get("categoria", "")),
            descricao=str(d.get("descricao", "")),
            fornecedor=str(d.get("fornecedor", "")),
            valor_centavos=float_to_cents(float(d.get("valor", 0.0))),
            tem_nota_fiscal=bool(d.get("tem_nota_fiscal", False))
        )
        despesas.append(despesa_item)

    return colaborador, periodo, despesas
