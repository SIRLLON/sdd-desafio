# Sessão 02 — Plano Técnico (plan.md) e Fatiamento de Tarefas (tasks.md)

**Data:** 2026-08-14
**Participantes:** Desenvolvedor & Assistente IA (Antigravity/Gemini)
**Foco:** Definição da stack técnica, modelagem da arquitetura, decisões técnicas de precisão monetária e criação das tarefas T-001 a T-012.

---

## 1. Prompt do Usuário
> "Com a spec.md, ajude-me a elaborar o `plan.md` e o `tasks.md`. Escolha a stack Python 3.12.2, defina a estratégia de inteiros em centavos para moedas e crie as tarefas T-001 a T-012 mapeando cada requisito RN e AMB da spec com critérios de aceite testáveis."

---

## 2. Decisões Arquiteturais e Técnicas
* **Stack Escolhida:** Python 3.12.2 com `pytest`, `dataclasses` e `argparse`.
* **Aritmética Monetária (DT-001):** Inteiros em Centavos (`int`). Todos os valores de entrada são convertidos (ex: R$ 72.50 -> 7250 centavos) utilizando arredondamento half-up. Previne imprecisões binárias de ponto flutuante (*IEEE-754*).
* **Pipeline Funcional Modular:** Separação rígida entre I/O/CLI (`src/cli.py`), Parser (`src/parser.py`), Núcleo de Regras Puro (`src/engine.py`) e Formatador (`src/formatter.py`).
* **Mapeamento de Tasks:**
  * **Fase 1 (Fundação):** `T-001` (Parser/Centavos), `T-002` (Validações básicas), `T-003` (Duplicatas).
  * **Fase 2 (Regras & Limites):** `T-004` (Nota Fiscal), `T-005` (Viagem/Hospedagem), `T-006` (Acumulado Diário/Parcial), `T-007` (Estornos).
  * **Fase 3 (Formatador & Integração):** `T-008` (Coworking/Arredondamento), `T-009` (Gerador JSON), `T-010` (Integração Exemplo).
  * **Fase 4 (CLI & Regressão):** `T-011` (CLI), `T-012` (Regressão final).

---

## 3. Entregáveis Gerados
* Criação de `specs/001-motor-reembolso/plan.md`.
* Criação de `specs/001-motor-reembolso/tasks.md` contendo a Matriz de Rastreabilidade.
* **Commit Git:**
  * `b4824f1` — `docs(plan,tasks): elabora plano tecnico com Python 3.12.2 (centavos) e fatiamento em tarefas T-001 a T-012`
