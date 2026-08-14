# Plano Técnico — Motor de Cálculo de Reembolso

**Versão:** 2.0 · **Baseado na spec:** 2.0

---

## 1. Stack

| Escolha | O quê | Por quê | O que descartei e por quê |
|---|---|---|---|
| **Linguagem** | Python 3.12.2 | Excelente suporte a tipagem (`dataclasses`), legibilidade, manipulação nativa de JSON e sem dependências externas complexas. | Node.js / Go (Python oferece prototipagem e testabilidade mais direta para o escopo do desafio). |
| **Testes** | `pytest` | Framework padrão da indústria Python para testes simples, declarativos e fixtures limpas. | `unittest` (mais verboso e com sintaxe legado). |
| **Parsing/validação** | Módulos nativos (`json`, `argparse`, `dataclasses`) | Dispensa pacotes de terceiros, garantindo execução direta e sem riscos de compatibilidade de ambiente. | `pydantic` (desnecessário para o tamanho do esquema e evita dependência externa). |
| **Aritmética monetária** | **Inteiros em centavos (`int`)** | **Prevenção total de erros de precisão de ponto flutuante (IEEE-754)**. Ex: R$ 72.50 é armazenado e calculated como `7250` centavos. | `float` (causa imprecisão em somatórios) / `decimal.Decimal`. |

---

## 2. Arquitetura

O sistema adota uma arquitetura em **pipeline funcional e modular**, expandida na v2.0 para carregar políticas de centro de custo e tabela de câmbio:

```
[ Arquivo JSON Entrada ]  [ politica-v4.json ]  [ cambio.json ]
           │                       │                  │
           └───────────────┬───────┴──────────────────┘
                           ▼
              ┌──────────────────────┐
              │  Parser & Converter  │ (Converte Moedas -> Centavos BRL via PTAX)
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Pipeline de Regras   │ (Aplica RN-001..RN-019 com limites por CC)
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Gerador de Resumo   │ (Consolida Totais Solicitados, Aprovados e Recusados em BRL)
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Formatador de Saída  │ (Converte Centavos BRL -> Float e gera JSON)
              └──────────┬───────────┘
                         │
                         ▼
              [ Arquivo JSON Saída ]
```

---

## 3. Modelo de dados

Estruturas internas expandidas para suportar moeda original, valor em BRL centavos, política por CC e taxas PTAX:

```python
@dataclass
class DespesaItem:
    id: str
    data: date
    categoria: str
    descricao: str
    fornecedor: str
    valor_original: float
    moeda: str  # BRL, USD, EUR, etc.
    valor_centavos: int  # Convertido para BRL em centavos no parsing
    tem_nota_fiscal: bool

@dataclass
class TabelaPolitica:
    versao: str
    padrao: Dict[str, int]  # categoria -> teto centavos
    centros_custo: Dict[str, Dict[str, int]]  # cc -> {categoria: teto centavos}

@dataclass
class TabelaCambio:
    taxas: Dict[date, Dict[str, float]]  # data -> {moeda: taxa_ptax}
```

---

## 4. Como a política é representada

Na v2.0, a política deixa de ser uma constante rígida no código e passa a ser carregada dinamicamente via `TabelaPolitica`.

- Se a CLI não receber `--politica`, carrega a política v4 padrão em `exemplos/envelope/politica-v4.json`.
- Se a CLI não receber `--cambio`, carrega as taxas em `exemplos/envelope/cambio.json`.

---

## 5. Decisões técnicas

### DT-001 — Conversão PTAX no Parsing Inicial para Centavos BRL
**Contexto:** Despesas internacionais chegam em moedas diversas (USD, EUR).
**Decisão:** No parsing (`parse_input_file`), o motor consulta a `TabelaCambio` para a data da despesa (com fallback para o último dia útil anterior) e converte imediatamente o valor para `int` centavos BRL: `valor_centavos = float_to_cents(valor_original * taxa_ptax)`.
**Consequência:** Todas as regras da pipeline continuam operando 100% em inteiros centavos BRL sem imprecisão.

### DT-002 — Resolução de Limites por Centro de Custo
**Contexto:** Limites variam por Centro de Custo e por categoria.
**Decisão:** A classe `GerenciadorPolitica` busca primeiro `centros_custo[cc][categoria]`. Se omitido, busca em `padrao[categoria]`. Se `limite == 0`, a categoria é proibidíssima (`0.00`). Se não existir em nenhum dos dois, recusa 100%.

---

## 6. Estratégia de testes

- **Testes Unitários de Câmbio e CC:** `tests/test_envelope_v4.py` cobrindo PTAX, fallback de fim de semana, moedas não suportadas (`GBP`) e limites por centro de custo (`CC-COMERCIAL`, `CC-ENG-PLATAFORMA`, `CC-SUPORTE-N2`).
- **Integração:** `test_integracao_envelope` rodando contra `despesas-envelope.json` e `despesas-envelope-cc-desconhecido.json`.
- **Regressão:** Execução contínua da suíte v1.1 para garantir zero regressão nos testes base.
