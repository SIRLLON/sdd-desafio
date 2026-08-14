"""
Parser de dados de entrada JSON e Utilitários Monetários em Centavos.
"""
import json
import os
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from typing import Tuple, List, Dict, Optional
from src.models import Colaborador, Periodo, DespesaItem


def float_to_cents(value: float) -> int:
    """
    Converte um valor float (ex: 72.50) para um inteiro em centavos (ex: 7250)
    utilizando arredondamento financeiro Half-Up.
    """
    d = Decimal(str(value))
    cents = (d * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(cents)


def cents_to_float(cents: int) -> float:
    """
    Converte um valor em centavos inteiros (ex: 7250) para float (ex: 72.50).
    """
    d = Decimal(str(cents)) / Decimal("100")
    return float(d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


class GerenciadorCambio:
    """
    RN-018 / AMB-016, AMB-017: Gerencia as taxas de câmbio PTAX por data e realiza fallbacks.
    """
    def __init__(self, taxas: Dict[date, Dict[str, float]]):
        self.taxas = taxas

    @classmethod
    def carregar(cls, filepath: str) -> "GerenciadorCambio":
        if not os.path.exists(filepath):
            return cls(taxas={})

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        taxas_dict: Dict[date, Dict[str, float]] = {}
        for dt_str, cotacoes in data.get("taxas", {}).items():
            dt = datetime.strptime(dt_str, "%Y-%m-%d").date()
            taxas_dict[dt] = {moeda.upper(): float(rate) for moeda, rate in cotacoes.items()}

        return cls(taxas=taxas_dict)

    def obter_taxa(self, moeda: str, data_despesa: date) -> Optional[float]:
        """
        Retorna a taxa PTAX da moeda para a data.
        BRL retorna sempre 1.0.
        Se a data não possuir cotação, realiza fallback para a última data útil anterior.
        Se a moeda não for encontrada ou não possuir suporte, retorna None.
        """
        moeda_norm = moeda.strip().upper()
        if moeda_norm == "BRL":
            return 1.0

        if not self.taxas:
            return None

        # Se a data exata possui cotação para a moeda
        if data_despesa in self.taxas and moeda_norm in self.taxas[data_despesa]:
            return self.taxas[data_despesa][moeda_norm]

        # AMB-016: Fallback para a última cotação disponível anterior
        datas_disponiveis = [d for d in sorted(self.taxas.keys()) if d <= data_despesa]
        for dt in reversed(datas_disponiveis):
            if moeda_norm in self.taxas[dt]:
                return self.taxas[dt][moeda_norm]

        return None


def parse_input_file(
    filepath: str,
    gerenciador_cambio: Optional[GerenciadorCambio] = None
) -> Tuple[Colaborador, Periodo, List[DespesaItem]]:
    """
    Lê o arquivo JSON de entrada e constrói as entidades com conversão para centavos BRL.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    colab_data = data["colaborador"]
    colaborador = Colaborador(
        id=str(colab_data["id"]),
        nome=str(colab_data["nome"]),
        centro_custo=str(colab_data["centro_custo"])
    )

    per_data = data["periodo"]
    comp_str = per_data["competencia"]
    comp_year, comp_month = map(int, comp_str.split("-"))
    
    # Define início e fim do mês de competência se omitidos
    inicio_default = date(comp_year, comp_month, 1)
    if comp_month == 12:
        fim_default = date(comp_year, 12, 31)
    else:
        fim_default = date(comp_year, comp_month + 1, 1) - Decimal("1")
        # Se for date real:
        from datetime import timedelta
        fim_default = date(comp_year, comp_month + 1, 1) - timedelta(days=1)

    inicio_dt = datetime.strptime(per_data["inicio"], "%Y-%m-%d").date() if "inicio" in per_data else inicio_default
    fim_dt = datetime.strptime(per_data["fim"], "%Y-%m-%d").date() if "fim" in per_data else fim_default

    periodo = Periodo(
        competencia=comp_str,
        inicio=inicio_dt,
        fim=fim_dt
    )

    if gerenciador_cambio is None:
        cambio_path = os.path.join("exemplos", "envelope", "cambio.json")
        gerenciador_cambio = GerenciadorCambio.carregar(cambio_path)

    despesas: List[DespesaItem] = []
    for d in data.get("despesas", []):
        dt_despesa = datetime.strptime(d["data"], "%Y-%m-%d").date()
        moeda = str(d.get("moeda", "BRL")).strip().upper()
        valor_orig = float(d["valor"])

        taxa = gerenciador_cambio.obter_taxa(moeda, dt_despesa)
        if taxa is None:
            # Se a moeda não tiver cotação, define valor em centavos como 0 para forçar recusa por erro de câmbio
            val_centavos = 0
        else:
            val_brl_float = valor_orig * taxa
            val_centavos = float_to_cents(val_brl_float)

        despesa_item = DespesaItem(
            id=str(d["id"]),
            data=dt_despesa,
            categoria=str(d["categoria"]),
            descricao=str(d.get("descricao", "")),
            fornecedor=str(d.get("fornecedor", "")),
            valor_original=valor_orig,
            moeda=moeda,
            valor_centavos=val_centavos,
            tem_nota_fiscal=bool(d.get("tem_nota_fiscal", False))
        )
        despesas.append(despesa_item)

    return colaborador, periodo, despesas
