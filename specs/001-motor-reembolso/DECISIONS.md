# Log de Decisões e Mudanças de Spec

> Uma entrada **toda vez** que a spec mudar. Este arquivo é a prova de que a spec
> foi tratada como artefato vivo e não como cerimônia de abertura.

Ordem cronológica inversa: a mais recente primeiro.

---

## D-001 — Criação da Spec Inicial v1.0 e Resolução de Ambiguidades · 2026-08-14

**Gatilho:** Análise inicial da Política de Reembolso v3 em confronto com os dados reais de `exemplos/despesas-exemplo.json`.

**O que mudou na spec:**
- Definição formal das Regras de Negócio `RN-001` a `RN-011`.
- Resolução e registro formal das 10 ambiguidades identificadas (`AMB-001` a `AMB-010`), abrangendo:
  - Aplicação de limite diário acumulado por data/categoria (`AMB-001`).
  - Corte proporcional para reembolso parcial (`AMB-002`).
  - Obrigatoriedade de Nota Fiscal para valores >= R$ 100,00 (`AMB-003`).
  - Caracterização de "Em Viagem" via presença de Hospedagem (+50% nos limites) (`AMB-004`).
  - Janela retroativa de até 3 meses para competência (`AMB-005`).
  - Desduplicação por (data, categoria, valor) mantendo primeiro ID (`AMB-006`).
  - Inclusão de `coworking` e tolerância a maiúsculas/minúsculas (`AMB-007`).
  - Arredondamento padrão para 2 casas decimais (`AMB-008`).
  - Estornos como abatimento do acumulado diário (`AMB-009`).
  - Cálculo de diárias múltiplas para hospedagem (`AMB-010`).
- Estabelecimento da matriz de precedência na avaliação de regras (Seção 8).

**Por quê:** A política enviada pelo RH continha múltiplas ambiguidades e omissões operacionais que impediam um algoritmo determinístico sem definições explícitas de escopo, ordem e limites.

**O que isso invalidou:** N/A (especificação inicial).

**Tasks afetadas:** Inicialização das tasks T-001 a T-008 (a definir no `plan.md` e `tasks.md`).

**Custo:** Elaboração e homologação inicial da spec.md v1.0.
