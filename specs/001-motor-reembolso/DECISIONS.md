# Log de Decisões e Mudanças de Spec

> Uma entrada **toda vez** que a spec mudar. Este arquivo é a prova de que a spec
> foi tratada como artefato vivo e não como cerimônia de abertura.

Ordem cronológica inversa: a mais recente primeiro.

---

## D-002 — Inclusão de Ambiguidades AMB-011 a AMB-013 e Regras RN-012 a RN-014 · 2026-08-14

**Gatilho:** Análise aprofundada dos casos de borda e do item `d-012` em `exemplos/despesas-exemplo.json` (gastos em fins de semana) e validação de datas limites e sanidade de dados.

**O que mudou na spec:**
- Adição das Regras de Negócio `RN-012` (fins de semana), `RN-013` (datas futuras/após período) e `RN-014` (dados nulos ou zerados).
- Adição e desambiguação formal de `AMB-011`, `AMB-012` e `AMB-013`.
- Atualização da tabela de casos de borda (Seção 7) e da ordem sequencial de precedência de avaliação (Seção 8).

**Por quê:** Garantir cobertura total de casos limites que podem ocorrer em conjuntos ocultos do avaliador e blindar a spec contra entradas inconsistentes ou em datas não úteis.

**O que isso invalidou:** N/A (expansão compatível com a v1.0).

**Tasks afetadas:** Expansão dos casos de teste nas tasks de homologação.

**Custo:** Atualização e homologação da spec.md v1.1.

---

## D-001 — Criação da Spec Inicial v1.0 e Resolução de Ambiguidades · 2026-08-14

**Gatilho:** Análise inicial da Política de Reembolso v3 em confronto com os dados reais de `exemplos/despesas-exemplo.json`.

**O que mudou na spec:**
- Definição formal das Regras de Negócio `RN-001` a `RN-011`.
- Resolução e registro formal das 10 ambiguidades identificadas (`AMB-001` a `AMB-010`).
- Estabelecimento da matriz de precedência na avaliação de regras (Seção 8).

**Por quê:** A política enviada pelo RH continha múltiplas ambiguidades e omissões operacionais que impediam um algoritmo determinístico sem definições explícitas.

**O que isso invalidou:** N/A (especificação inicial).

**Tasks afetadas:** Inicialização das tasks T-001 a T-008.

**Custo:** Elaboração e homologação inicial da spec.md v1.0.
