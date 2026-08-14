# Plano Técnico — Motor de Cálculo de Reembolso

**Versão:** 1.0 · **Baseado na spec:** 1.1

---

## 1. Stack

| Escolha | O quê | Por quê | O que descartei e por quê |
|---|---|---|---|
| **Linguagem** | Python 3.12.2 | Excelente suporte a tipagem (`dataclasses`), legibilidade, manipulação nativa de JSON e sem dependências externas complexas. | Node.js / Go (Python oferece prototipagem e testabilidade mais direta para o escopo do desafio). |
| **Testes** | `pytest` | Framework padrão da indústria Python para testes simples, declarativos e fixtures limpas. | `unittest` (mais verboso e com sintaxe legado). |
| **Parsing/validação** | Módulos nativos (`json`, `argparse`, `dataclasses`) | Dispensa pacotes de terceiros, garantindo execução direta e sem riscos de compatibilidade de ambiente. | `pydantic` (desnecessário para o tamanho do esquema e evita dependência externa). |
| **Aritmética monetária** | **Inteiros em centavos (`int`)** | **Prevenção total de erros de precisão de ponto flutuante (IEEE-754)**. Ex: R$ 72.50 é armazenado e calculado como `7250` centavos. | `float` (causa imprecisão em somatórios) / `decimal.Decimal` (funciona, mas inteiros em centavos garantem performance e simplicidade matemática pura). |

---

## 2. Arquitetura

O sistema adota uma arquitetura em **pipeline funcional e modular**, separando rigorosamente I/O, parsing, regras de negócio e formatação de saída:

```
[ Arquivo JSON Entrada ]
           │
           ▼
┌──────────────────────┐
│  Parser & Converter  │ (Converte JSON -> Modelos Internos com Valores em Centavos)
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Pipeline de Regras   │ (Aplica RN-001..RN-014 na ordem determinística de precedência)
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Gerador de Resumo   │ (Consolida Totais Solicitados, Aprovados e Recusados)
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Formotador de Saída  │ (Converte Centavos -> Float de 2 casas decimais e gera JSON)
└──────────┬───────────┘
           │
           ▼
[ Arquivo JSON Saída ]
```

### Fronteiras de Responsabilidade

- **I/O e CLI (`src/cli.py`):** Responsável por ler argumentos da linha de comando, abrir/salvar arquivos e tratar exceções de arquivo não encontrado.
- **Núcleo de Regras (`src/domain/engine.py`):** **100% puro**, sem dependência de I/O ou arquivos. Recebe estruturas de dados na memória e retorna o resultado da avaliação. É nesta camada que residem todas as decisões da `spec.md`.

---

## 3. Modelo de dados

Estruturas internas fortemente tipadas utilizando `dataclasses` nativas do Python:

```python
@dataclass
class Periodo:
    competencia: str
    inicio: date
    fim: date

@dataclass
class DespesaItem:
    id: str
    data: date
    categoria: str  # Normalizada para minúsculo
    descricao: str
    fornecedor: str
    valor_centavos: int  # Ex: R$ 72.50 = 7250
    tem_nota_fiscal: bool

@dataclass
class ResultadoItem:
    id: str
    status: str  # APROVADO, APROVADO_PARCIAL, RECUSADO
    valor_solicitado_centavos: int
    valor_aprovado_centavos: int
    valor_recusado_centavos: int
    justificativas: list[str]
```

---

## 4. Como a política é representada

Os limites e parâmetros da política corporativa são representados como um **objeto/dicionário de configuração imutável**, desacoplado do motor de cálculo.

```python
LIMITES_PADRAO_CENTAVOS = {
    "alimentacao": 6000,       # R$ 60.00 em centavos
    "transporte_urbano": 8000, # R$ 80.00 em centavos
    "hospedagem": 25000,       # R$ 250.00 por diária em centavos
    "coworking": None          # Sem teto em tabela
}

FATOR_VIAGEM = 1.5  # Acréscimo de 50% nos limites em período de viagem
```

*Vantagem:* Se o RH alterar o limite de Alimentação para R$ 70,00 ou o fator de viagem para 60% no futuro, altera-se apenas essa configuração sem modificar o fluxo do motor.

---

## 5. Decisões técnicas

### DT-001 — Representação Interna Monetária em Cents (`int`)
**Contexto:** Operações de soma e subtração em ponto flutuante (`float`) no Python acumulam erros de precisão binária (ex: `0.1 + 0.2 != 0.3`).
**Decisão:** Toda entrada monetária é convertida na leitura para `int` em centavos (`int(round(valor * 100))`). Todos os somatórios e cortes ocorrem em centavos. Na saída JSON, o valor é convertido de volta para `float` com `round(centavos / 100, 2)`.
**Alternativa descartada:** Uso de `float` (causaria imprecisão) ou `Decimal` (adiciona verbosidade sem ganho sobre inteiros).
**Consequência:** Elimina 100% dos erros de arredondamento em somatórios e garante determinismo absoluto.

### DT-002 — Ordem Sequencial de Pipeline de Regras
**Contexto:** Uma despesa pode ferir múltiplas regras ao mesmo tempo (ex: sem nota fiscal E duplicada E fora do prazo).
**Decisão:** O motor aplica um pipeline sequencial com interrupção rápida (*fail-fast*) para recusas totais, seguindo estritamente a Ordem de Precedência definida na Seção 8 da `spec.md`.
**Alternativa descartada:** Avaliar todas as regras em paralelo e mesclar status (geraria inconsistência nos motivos de recusa).
**Consequência:** Resposta predizível e justificativas claras e hierarquizadas.

### DT-003 — Desduplicação Determinística por Ordem de Leitura (ID)
**Contexto:** Despesas duplicadas precisam de critério determinístico de desempate.
**Decisão:** O motor mantém um registro (`set`) das assinaturas `(data, categoria, valor_centavos)` processadas. A primeira ocorrência na lista de entrada é mantida; as subsequentes idênticas são marcadas como duplicatas.
**Alternativa descartada:** Ordenar por valor ou ID antes do processamento (alteraria a cronologia de lançamentos do colaborador).
**Consequência:** Preserva a ordem original do arquivo submetido.

---

## 6. Estratégia de testes

- **Nível:** Testes de Unidade (para cada regra isolada `RN-001` a `RN-014`) e Teste de Integração Ponta a Ponta (executando a CLI contra `exemplos/despesas-exemplo.json`).
- **Cobertura por Requisito:** Cada regra `RN-XXX` e ambiguidade `AMB-YYY` possui no mínimo 1 teste unitário dedicado com nome descritivo (ex: `test_rn_005_nota_fiscal_obrigatoria_acima_100`).
- **Casos de Borda:** Cobertura de todos os cenários descritos na Seção 7 da `spec.md`.
- **Rastreabilidade:** A suíte de testes referencia os IDs das regras em suas docstrings e nomes de funções.

---

## 7. Riscos

| Risco | Probabilidade | O que faço se acontecer |
|---|---|---|
| Incompatibilidade de formato de datas em entradas ocultas | Baixa | Utilizar `datetime.strptime` com fallback seguro e mensagens claras de erro. |
| Descrição de hospedagem com diárias em formato textual não padrão | Média | Utilizar expressões regulares (Regex) para extrair padrões numéricos comuns de diárias (ex: `2 diarias`, `3 noites`, `1 diária`). |
| Modificação de requisitos no Dia 2 (Envelope Lacrado) | Alta | Absorver a mudança via `spec.md` -> `DECISIONS.md` -> `tasks.md` -> `código`, reexecutando os testes da suíte. |
