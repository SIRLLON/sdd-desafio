"""
Modelos de dados internos do motor de cálculo de reembolso.
"""
from dataclasses import dataclass
from datetime import date
from typing import Optional, List


@dataclass
class Colaborador:
    id: str
    nome: str
    centro_custo: str


@dataclass
class Periodo:
    competencia: str
    inicio: date
    fim: date


@dataclass
class DespesaItem:
    id: str
    data: date
    categoria: str
    descricao: str
    fornecedor: str
    valor_centavos: int
    tem_nota_fiscal: bool


@dataclass
class ResultadoItem:
    id: str
    status: str  # APROVADO, APROVADO_PARCIAL, RECUSADO
    valor_solicitado_centavos: int
    valor_aprovado_centavos: int
    valor_recusado_centavos: int
    justificativas: List[str]
