# Log de Decisões e Mudanças de Spec

> Uma entrada **toda vez** que a spec mudar. Este arquivo é a prova de que a spec
> foi tratada como artefato vivo e não como cerimônia de abertura.

Ordem cronológica inversa: a mais recente primeiro.

---

## D-003 — Absorção do Envelope Lacrado (Política v4 e Câmbio PTAX) · 2026-08-14

**Gatilho:** Recebimento do Comunicado do RH do Dia 2 com a Política de Reembolso v4 (`politica-v4.json`), Cotações PTAX (`cambio.json`) e despesas em moedas estrangeiras.

**O que mudou na spec:**
- Transição da `spec.md` da v1.1 para a v2.0.
- Adição das Regras de Negócio `RN-015` a `RN-019`:
  - `RN-015`: Limites dinâmicos por Centro de Custo com fallback para tabela `padrao`.
  - `RN-016`: Restrição absoluta (`limite: 0.00`) para categorias proibidas por CC (ex: `hospedagem` em `CC-ENG-PLATAFORMA`).
  - `RN-017`: Suporte à categoria `representacao` em CC autorizado (`CC-COMERCIAL`).
  - `RN-018`: Conversão de moedas estrangeiras (`USD`, `EUR`) por PTAX com fallback de data anterior para fins de semana/feriados. Recusa para moeda sem cotação (`GBP`).
  - `RN-019`: Testes de Nota Fiscal (>= R$ 100,00 BRL) e limites executados sobre o valor convertido em BRL.
- Registro e solução das ambiguidades `AMB-014` a `AMB-019`.

**Por quê:** A Política v4 descentralizou os limites por centro de custo e passou a aceitar despesas internacionais, exigindo conversão PTAX e limites dinâmicos sem alterar o motor determinístico.

**O que isso invalidou:**
- Limites numéricos estáticos e imutáveis no código (`LIMITES_PADRAO_CENTAVOS`).
- Assunção de que toda entrada vinha exclusivamente em `BRL`.

**Tasks afetadas:**
- Criação das tasks `T-013` a `T-017` no `tasks.md`.

**Custo:** Atualização de `spec.md` v2.0, `DECISIONS.md`, `tasks.md`, `plan.md` e refatoração modular do motor.

---

## D-002 — Inclusão de Ambiguidades AMB-011 a AMB-013 e Regras RN-012 a RN-014 · 2026-08-14

**Gatilho:** Análise aprofundada dos casos de borda e do item `d-012` em `exemplos/despesas-exemplo.json` (gastos em fins de semana) e validação de datas limites e sanidade de dados.

**O que mudou na spec:**
- Adição das Regras de Negócio `RN-012` (fins de semana), `RN-013` (datas futuras/após período) e `RN-014` (dados nulos ou zerados).
- Adição e desambiguação formal de `AMB-011`, `AMB-012` e `AMB-013`.

**Por quê:** Garantir cobertura total de casos limites que podem ocorrer em conjuntos ocultos do avaliador.

**O que isso invalidou:** N/A (expansão compatível com a v1.0).

**Tasks afetadas:** Expansão dos casos de teste nas tasks de homologação.

**Custo:** Atualização e homologação da spec.md v1.1.

---

## D-001 — Criação da Spec Inicial v1.0 e Resolução de Ambiguidades · 2026-08-14

**Gatilho:** Análise inicial da Política de Reembolso v3 em confronto com os dados reais de `exemplos/despesas-exemplo.json`.

**O que mudou na spec:**
- Definição formal das Regras de Negócio `RN-001` a `RN-011`.
- Resolução e registro formal das 10 ambiguidades identificadas (`AMB-001` a `AMB-010`).

**Por quê:** A política enviada pelo RH continha múltiplas ambiguidades e omissões operacionais.

**O que isso invalidou:** N/A (especificação inicial).

**Tasks afetadas:** Inicialização das tasks T-001 a T-008.

**Custo:** Elaboração e homologação inicial da spec.md v1.0.
