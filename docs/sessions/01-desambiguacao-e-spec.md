# Sessão 01 — Desambiguação da Política e Criação da Spec.md

**Data:** 2026-08-14
**Participantes:** Desenvolvedor & Assistente IA (Antigravity/Gemini)
**Foco:** Leitura da Política de Reembolso v3, confronto com `despesas-exemplo.json`, desambiguação de 13 regras e escrita da `spec.md` v1.0 e v1.1.

---

## 1. Prompt do Usuário
> "preciso resolver o desafio, me ajude utilizando o ciclo sdd. se baseie nos arquivos GEMINI, DESAFIO, README, RUBRICA E use o despesasa-exemplo.json para servir de exemplo do que sera de entrada no desafio.
> primeiro preciso de ajuda montar a spec.md vamos criar juntos e eu vou revisando.
> Para adiantar, tenho algumas ambiguidades para documentar:
> - regra 1,2,3: eh por soma do dia (ex: 70 -> 60 max por ordem de id)
> - regra 4: reembolso ate o teto, o que passar nao sera feito
> - regra 5: ate 99,99 sem NF. de 100 em diante com NF
> - regra 6: hospedagem caracteriza viagem, inclui transporte e alimentacao no periodo, tetos +50%
> - regra 7: ate 3 meses apos data da despesa
> - regra 8: duplicatas (mesmo valor, data e categoria)
> - regra 9: categorias transporte, alimentacao, hospedagem, coworking
> - regra 10: arredondamento padrao 2 casas decimais."

---

## 2. Análise e Discussão
* O assistente leu os arquivos `DESAFIO.md`, `RUBRICA.md`, `README.md` e `exemplos/despesas-exemplo.json`.
* Identificou-se que a Política do RH possui lacunas que precisam ser explicitadas sem vazamento de solução técnica.
* Mapeamento inicial de ambiguidades:
  * `AMB-001`: Aplicação do limite por dia acumulado por colaborador + categoria.
  * `AMB-002`: Reembolso parcial (aprova até o limite e corta o excedente).
  * `AMB-003`: NF obrigatória a partir de R$ 100,00 inclusivo (`>= 100.00`).
  * `AMB-004`: "Em Viagem" inferido pela presença de Hospedagem (tetos sobem +50%).
  * `AMB-005`: Prazo de competência de até 3 meses retroativos.
  * `AMB-006`: Duplicata = mesmo valor, data e categoria. Mantém menor ID.
  * `AMB-007`: Categorias permitidas e tratamento de Coworking.
  * `AMB-008`: Arredondamento Half-Up para 2 casas decimais.
  * `AMB-009`: Estornos (valores negativos) abatem o acumulado do dia.
  * `AMB-010`: Hospedagem cobrindo múltiplas diárias num único lançamento (`d-010`).

---

## 3. Segunda Interação — Identificação de Ambiguidades Adicionais
* **Pergunta do Usuário:** *"existe alguma outra ambiguidade que pode estar passando despercebido?"*
* **Análise dos Dados:**
  * `d-012` possui data `2026-07-18` (Sábado, plantão). `AMB-011`: Fins de semana e feriados são válidos? (Decisão: Sim).
  * `AMB-012`: Datas futuras ou após `periodo.fim`? (Decisão: Recusadas).
  * `AMB-013`: Despesas com valor zerado (`0.00`) ou dados corrompidos? (Decisão: Recusadas).

---

## 4. Ações e Entregáveis Gerados
* Criação de `specs/001-motor-reembolso/spec.md` (v1.0 e v1.1).
* Atualização do log em `specs/001-motor-reembolso/DECISIONS.md` (`D-001` e `D-002`).
* **Commits Git:**
  * `a0f47fe` — `docs(spec): elabora spec.md v1.0 com 10 ambiguidades resolvidas e regras RN-001 a RN-011`
  * `96b7090` — `docs(spec): adiciona ambiguidades AMB-011 a AMB-013 e regras RN-012 a RN-014`
