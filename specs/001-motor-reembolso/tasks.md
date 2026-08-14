# Tasks — Motor de Cálculo de Reembolso

> Cada task é pequena o bastante para virar **um commit**. Se você não consegue
> descrever o critério de aceite como "o teste X passa", a task está grande demais.
>
> Marque `[x]` conforme conclui — ao longo do caminho, não tudo no fim. O histórico
> de quando cada task foi marcada é lido na correção.

**Formato do commit:** `feat(T-003): <descrição>` · `test(T-003): <descrição>`

---

## Fase 1 — Fundação e Modelagem (T-001 a T-003)

- [x] **T-001** — Configurar estrutura inicial do projeto Python, CLI básica e conversor de valores monetários para inteiros em centavos.
  - **Atende:** RN-010, RN-014, AMB-008, AMB-013
  - **Aceite:** Teste `test_cli_parse_input_to_cents` carrega JSON e converte `valor: 72.50` em `7250` centavos, rejeitando arquivo inexistente ou JSON corrompido.
  - **Commit:** `2e02a10`

- [x] **T-002** — Implementar validações básicas de entrada (Categorias permitidas, Competência retroativa/futura e sanidade de dados).
  - **Atende:** RN-007, RN-009, RN-012, RN-013, RN-014, AMB-005, AMB-007, AMB-011, AMB-012, AMB-013
  - **Aceite:** Teste `test_validacoes_basicas_categoria_e_datas` rejeita categoria `lazer`, data > 3 meses ou no futuro e `valor == 0`, mas aceita plantão de sábado (`d-012`) e insensibilidade a caixa (`ALIMENTACAO`).
  - **Commit:** `66a25b7`

- [x] **T-003** — Implementar detector de despesas duplicadas por assinatura (Data, Categoria, Valor).
  - **Atende:** RN-008, AMB-006
  - **Aceite:** Teste `test_desduplicacao_mantem_primeira_ocorrencia` aceita `d-006` e recusa `d-007` com o motivo "Despesa duplicada".
  - **Commit:** `e5dbf0d`

---

## Fase 2 — Regras de Negócio e Limites (T-004 a T-007)

- [x] **T-004** — Implementar regra de obrigatoriedade de Nota Fiscal para valores >= R$ 100,00.
  - **Atende:** RN-005, AMB-003
  - **Aceite:** Teste `test_comprovante_fiscal_obrigatorio_acima_100` recusa `d-003` (R$ 100.00 sem NF) e `d-004` (R$ 100.01 sem NF), mas aprova gasto de R$ 99.99 sem NF.
  - **Commit:** `7659fa4`

- [x] **T-005** — Implementar detector de período "Em Viagem" (+50% nos limites) e cálculo de múltiplas diárias de hospedagem.
  - **Atende:** RN-003, RN-006, AMB-004, AMB-010
  - **Aceite:** Teste `test_estado_viagem_amplia_limites_50_porcento` identifica hospedagem (`d-010`), estende viagem e aplica limites de R$ 90/dia (alimentação), R$ 120/dia (transporte) e R$ 375/diária (hospedagem).
  - **Commit:** `55aa6f3`

- [x] **T-006** — Implementar controle de acumulado diário e concessão de Reembolso Parcial por corte de excedente.
  - **Atende:** RN-001, RN-002, RN-004, AMB-001, AMB-002
  - **Aceite:** Teste `test_limite_diario_acumulado_e_reembolso_parcial` aprova R$ 60.00 e corta R$ 12.50 para `d-001` (R$ 72.50), e recusa 100% `d-002` (R$ 38.00) por teto diário esgotado.
  - **Commit:** `98a894e`

- [x] **T-007** — Implementar processamento de estornos (Valores Negativos) e recomposição de saldo diário.
  - **Atende:** RN-011, AMB-009
  - **Aceite:** Teste `test_estorno_abate_acumulado_diario` aprova o crédito de `d-009` (R$ -45.00) e abate 4500 centavos do acumulado do dia em transporte.
  - **Commit:** `ba28327`

---

## Fase 3 — Formatador de Saída e Casos de Borda (T-008 a T-010)

- [x] **T-008** — Implementar regra de Coworking e formatação de precisão com arredondamento Half-Up.
  - **Atende:** RN-009, RN-010, AMB-007, AMB-008
  - **Aceite:** Teste `test_coworking_e_arredondamento_half_up` aprova coworking (`d-005`) com NF e arredonda `d-011` (33.333) para `33.33`.
  - **Commit:** `b6744d1`

- [x] **T-009** — Implementar construtor do JSON de saída e gerador do resumo consolidado.
  - **Atende:** Seção 4 da spec.md (Estrutura de Saída)
  - **Aceite:** Teste `test_geracao_json_saida_estrutura` confirma que a saída possui `total_solicitado`, `total_aprovado` e `total_recusado` exatamente iguais ao somatório dos itens.
  - **Commit:** `6a4f1ff`

- [x] **T-010** — Executar teste de integração ponta a ponta com o dataset `exemplos/despesas-exemplo.json`.
  - **Atende:** Seção 9 da spec.md (Critérios de Aceite)
  - **Aceite:** Teste `test_integracao_ponta_a_ponta_exemplo` processa as 14 despesas de exemplo e valida os totais consolidados e justificativas de cada item.
  - **Commit:** `82fa235`

---

## Fase 4 — CLI e Suíte de Regressão Final (T-011 a T-012)

- [x] **T-011** — Implementar a interface CLI final (`calcular --input <file> --output <file>`).
  - **Atende:** Seção 2.5 de DESAFIO.md
  - **Aceite:** Comando `python -m src.cli calcular --input exemplos/despesas-exemplo.json --output resultado.json` executa com retorno código 0 e gera o JSON esperado.
  - **Commit:** `f2065f2`

- [x] **T-012** — Executar suíte completa de testes de regressão e homologar a Matriz de Rastreabilidade.
  - **Atende:** Critério 2 da RUBRICA.md (Rastreabilidade 100%)
  - **Aceite:** `pytest` roda com 100% de aprovação e todos os requisitos da matriz abaixo possuem testes ativos.
  - **Commit:** `f2065f2`

---

## Fase 5 — Envelope Lacrado / Política v4 (T-013 a T-017)

- [x] **T-013** — Implementar leitor de políticas por Centro de Custo (`politica-v4.json`) e resolver fallback `padrao` e restrições R$ 0,00.
  - **Atende:** RN-015, RN-016, RN-017, AMB-014, AMB-015
  - **Aceite:** Teste `test_politica_centro_custo_e_fallback` aceita limites do `CC-COMERCIAL`, aplica fallback para `CC-SUPORTE-N2` e recusa 100% hospedagem em `CC-ENG-PLATAFORMA`.
  - **Commit:** `23435b6`

- [x] **T-014** — Implementar leitor de câmbio PTAX (`cambio.json`), conversor de moedas em centavos BRL e fallback de data anterior.
  - **Atende:** RN-018, RN-019, AMB-016, AMB-017, AMB-018, AMB-019
  - **Aceite:** Teste `test_conversao_moeda_ptax_e_fallback` converte 22 EUR (14/07) para R$ 130.46 BRL, usa cotação de 17/07 para sábado (18/07) e recusa moeda `GBP` sem taxa.
  - **Commit:** `74e81fe`

- [x] **T-015** — Integrar leitura dinâmica de política/câmbio na pipeline e ajustar validação de NF e limites para BRL convertido.
  - **Atende:** RN-005, RN-006, RN-018, RN-019, AMB-018, AMB-019
  - **Aceite:** Teste `test_pipeline_envelope_v4` recusa 40 USD sem NF (R$ 220 BRL >= 100) e aprova 14.50 EUR sem NF (R$ 85.26 BRL < 100).
  - **Commit:** `f064e50`

- [ ] **T-016** — Homologar integração ponta a ponta com `despesas-envelope.json` e `despesas-envelope-cc-desconhecido.json`.
  - **Atende:** Requisitos do Envelope Lacrado
  - **Aceite:** Teste `test_integracao_envelope_datasets` processa os dois novos arquivos JSON gerando relatórios de saída coerentes.
  - **Commit:** `<hash preenchido depois>`

- [ ] **T-017** — Atualizar CLI para aceitar argumentos opcionais `--politica` e `--cambio` e homologar regressão total.
  - **Atende:** CLI v2.0
  - **Aceite:** CLI executa com sucesso novos e antigos datasets; `pytest` roda 100% verde sem quebrar a v1.1.
  - **Commit:** `<hash preenchido depois>`

---

## Matriz de Rastreabilidade (Requisito → Task → Teste)

| Requisito / Ambiguidade | Task Responsável | Teste de Homologação |
|---|---|---|
| **RN-001** (Limite Alimentação) | `T-006`, `T-013` | `test_limite_diario_acumulado_e_reembolso_parcial` |
| **RN-002** (Limite Transporte) | `T-006`, `T-013` | `test_limite_diario_acumulado_e_reembolso_parcial` |
| **RN-003** (Limite Hospedagem) | `T-005`, `T-013` | `test_estado_viagem_amplia_limites_50_porcento` |
| **RN-004** (Reembolso Parcial) | `T-006` | `test_limite_diario_acumulado_e_reembolso_parcial` |
| **RN-005** (Nota Fiscal >= 100 BRL) | `T-004`, `T-015` | `test_comprovante_fiscal_obrigatorio_acima_100` |
| **RN-006** (Viagem +50%) | `T-005`, `T-013` | `test_estado_viagem_amplia_limites_50_porcento` |
| **RN-007** (Prazo 3 meses) | `T-002` | `test_validacoes_basicas_categoria_e_datas` |
| **RN-008** (Duplicatas) | `T-003` | `test_desduplicacao_mantem_primeira_ocorrencia` |
| **RN-009** (Categorias válidas) | `T-002`, `T-008`, `T-013` | `test_validacoes_basicas_categoria_e_datas` |
| **RN-010** (Arredondamento 2 casas) | `T-001`, `T-008` | `test_coworking_e_arredondamento_half_up` |
| **RN-011** (Estornos / Negativos) | `T-007` | `test_estorno_abate_acumulado_diario` |
| **RN-012** (Fins de Semana) | `T-002`, `T-014` | `test_validacoes_basicas_categoria_e_datas` |
| **RN-013** (Datas Futuras/Fora) | `T-002` | `test_validacoes_basicas_categoria_e_datas` |
| **RN-014** (Sanidade / Zerados) | `T-001`, `T-002` | `test_validacoes_basicas_categoria_e_datas` |
| **RN-015** (Limites por CC / Fallback) | `T-013` | `test_politica_centro_custo_e_fallback` |
| **RN-016** (Proibição Hospedagem CC) | `T-013` | `test_politica_centro_custo_e_fallback` |
| **RN-017** (Categoria Representação) | `T-013` | `test_politica_centro_custo_e_fallback` |
| **RN-018** (Câmbio PTAX / Fallback) | `T-014` | `test_conversao_moeda_ptax_e_fallback` |
| **RN-019** (Validação BRL Convertido) | `T-015` | `test_pipeline_envelope_v4` |
| **AMB-014** (Categoria ausente no CC) | `T-013` | `test_politica_centro_custo_e_fallback` |
| **AMB-015** (Hospedagem 0 e Viagem) | `T-013` | `test_politica_centro_custo_e_fallback` |
| **AMB-016** (PTAX em Fim de Semana) | `T-014` | `test_conversao_moeda_ptax_e_fallback` |
| **AMB-017** (Moeda não cadastrada GBP) | `T-014` | `test_conversao_moeda_ptax_e_fallback` |
| **AMB-018** (Conversão Parsing BRL) | `T-014`, `T-015` | `test_conversao_moeda_ptax_e_fallback` |
| **AMB-019** (NF >= R$ 100 BRL) | `T-015` | `test_pipeline_envelope_v4` |
