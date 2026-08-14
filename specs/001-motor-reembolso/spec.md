# Spec — Motor de Cálculo de Reembolso

**Versão:** 2.0 · **Status:** aprovado · **Última alteração:** 2026-08-14

---

## 1. Problema

A empresa realiza a análise e o cálculo de reembolso de despesas de colaboradores através de um processo manual em planilhas. Essa abordagem gera demora no processamento, inconsistências na aplicação da política corporativa e alto risco de erros humanos no cômputo de limites, moedas estrangeiras e elegibilidade por centro de custo.

## 2. Objetivo

Prover um motor automatizado e determinístico de cálculo de reembolso que receba um conjunto de despesas de um colaborador, leia dinamicamente as tabelas de políticas por Centro de Custo (`politica-v4.json`) e cotações de câmbio (`cambio.json`), aplique rigorosamente as regras da política de reembolso (incluindo tratamento de limites por CC, moedas internacionais, duplicatas, notas fiscais, estornos, fins de semana e viagens) e gere um relatório detalhado de aprovações, recusas parciais ou totais com justificativas explícitas.

## 3. Fora de escopo

- Integração direta com gateways de pagamento ou sistemas bancários.
- Leitura automatizada ou OCR de imagens de notas fiscais (o campo `tem_nota_fiscal` é fornecido pronto na entrada).
- Interface gráfica (GUI) ou painel web (o sistema opera exclusivamente via interface de linha de comando CLI).
- Autenticação, autorização de usuários ou controle de permissões.
- Fila de aprovação manual com workflow de gestores (item C opcional).

---

## 4. Entrada e saída

### Entrada

A entrada é um arquivo JSON no formato definido em `exemplos/despesas-exemplo.json` ou `exemplos/envelope/despesas-envelope.json`.

**Campos da Entrada:**

| Campo | Tipo | Significado | Obrigatório |
|---|---|---|---|
| `colaborador.id` | String | Identificador único do colaborador | Sim |
| `colaborador.nome` | String | Nome completo do colaborador | Sim |
| `colaborador.centro_custo` | String | Código do centro de custo | Sim |
| `periodo.competencia` | String | Ano e mês de referência no formato `YYYY-MM` | Sim |
| `periodo.inicio` | String | Data de início do período analisado (`YYYY-MM-DD`) | Sim |
| `periodo.fim` | String | Data de término do período analisado (`YYYY-MM-DD`) | Sim |
| `despesas` | Array de Objetos | Lista de despesas submetidas | Sim |
| `despesas[].id` | String | Identificador único da despesa | Sim |
| `despesas[].data` | String | Data de ocorrência da despesa (`YYYY-MM-DD`) | Sim |
| `despesas[].categoria` | String | Categoria da despesa | Sim |
| `despesas[].descricao` | String | Descrição detalhada do gasto | Sim |
| `despesas[].fornecedor` | String | Nome do estabelecimento/fornecedor | Sim |
| `despesas[].valor` | Number | Valor monetário na moeda informada | Sim |
| `despesas[].moeda` | String | Código ISO 4217 da moeda (`BRL`, `USD`, `EUR`). Omitido assume `BRL` | Não |
| `despesas[].tem_nota_fiscal` | Boolean | Indica se possui comprovante fiscal anexado | Sim |

---

### Saída

A saída é um arquivo JSON gerado pelo motor com a consolidação dos reembolsos e o detalhamento de cada item (valores expressos na moeda base BRL).

**Campos da Saída:**

| Campo | Tipo | Significado |
|---|---|---|
| `colaborador.id` | String | Identificador do colaborador |
| `colaborador.nome` | String | Nome do colaborador |
| `colaborador.centro_custo` | String | Centro de custo |
| `periodo.competencia` | String | Competência do relatório |
| `resumo.total_solicitado` | Number | Soma dos valores convertidos em BRL de todas as despesas |
| `resumo.total_aprovado` | Number | Soma total a ser reembolsada em BRL ao colaborador |
| `resumo.total_recusado` | Number | Soma dos valores cortados ou rejeitados em BRL |
| `resumo.total_despesas` | Integer | Quantidade de despesas processadas |
| `resumo.despesas_aprovadas` | Integer | Quantidade de despesas totalmente ou parcialmente aprovadas |
| `resumo.despesas_recusadas` | Integer | Quantidade de despesas 100% recusadas |
| `itens` | Array de Objetos | Resultado individual de cada despesa |
| `itens[].id` | String | Identificador da despesa |
| `itens[].status` | String | Status final: `APROVADO`, `APROVADO_PARCIAL`, `RECUSADO` |
| `itens[].valor_solicitado` | Number | Valor em BRL equivalente à despesa lançada |
| `itens[].valor_aprovado` | Number | Valor final concedido para reembolso em BRL |
| `itens[].valor_recusado` | Number | Valor retido ou cortado em BRL |
| `itens[].justificativas` | Array de Strings | Lista de motivos de aprovação/recusa ou cortes aplicados |

---

## 5. Regras de negócio

### RN-001 — Limite Diário de Alimentação
**Regra:** Despesas na categoria `alimentacao` possuem teto diário definido pela tabela do Centro de Custo do colaborador (ex: R$ 90,00 no `CC-COMERCIAL`, R$ 75,00 no `CC-ENG-PLATAFORMA`, R$ 60,00 no padrão).
**Origem:** Política de Reembolso v4.
**Aceite:** Despesa de R$ 80,00 em alimentação para `CC-COMERCIAL` é totalmente aprovada (teto R$ 90,00).

### RN-002 — Limite Diário de Transporte Urbano
**Regra:** Despesas na categoria `transporte_urbano` possuem teto diário definido pelo Centro de Custo (ex: R$ 150,00 no `CC-COMERCIAL`, R$ 80,00 no `CC-ENG-PLATAFORMA`).
**Origem:** Política de Reembolso v4.
**Aceite:** Despesa de R$ 100,00 em transporte no `CC-COMERCIAL` é totalmente aprovada.

### RN-003 — Limite Diário de Hospedagem
**Regra:** Despesas na categoria `hospedagem` possuem teto por diária definido pelo Centro de Custo (ex: R$ 400,00/diária no `CC-COMERCIAL`, R$ 250,00 no padrão). Para estadias cobrindo múltiplas diárias, o teto é `quantidade_diarias * limite_diaria`.
**Origem:** Política de Reembolso v4.
**Aceite:** Lançamento de 3 diárias no `CC-COMERCIAL` possui teto base de R$ 1.200,00 (3 * R$ 400,00).

### RN-004 — Reembolso Parcial por Excedente de Teto
**Regra:** Quando uma despesa ultrapassa o limite diário disponível para sua categoria no Centro de Custo, a parcela dentro do teto é aprovada (`status: APROVADO_PARCIAL`) e o excedente é cortado.
**Origem:** Política de Reembolso v3/v4.
**Aceite:** Despesa de R$ 340,00 com teto disponível de R$ 300,00 gera `valor_aprovado: 300.00` e `valor_recusado: 40.00`.

### RN-005 — Obrigatoriedade de Comprovante Fiscal (Nota Fiscal)
**Regra:** Despesas cujo valor em BRL seja igual ou superior a R$ 100,00 (`valor_brl >= 100.00`) exigem obrigatoriamente `tem_nota_fiscal: true`. Se `tem_nota_fiscal` for `false`, a despesa é 100% recusada. Despesas até R$ 99,99 BRL são isentas.
**Origem:** Política de Reembolso v4.
**Aceite:** Despesa de 40.00 USD sem NF com câmbio R$ 5.50 (R$ 220.00 BRL) é RECUSADA por falta de NF.

### RN-006 — Limites Ampliados em Viagem (+50%)
**Regra:** A presença de uma despesa válida e aprovável de `hospedagem` estabelece o estado de "Em Viagem" para o período. Em viagem, os tetos diários do Centro de Custo recebem acréscimo de +50%.
**Origem:** Política de Reembolso v4.
**Aceite:** Em viagem no `CC-COMERCIAL`, o teto de Alimentação sobe para R$ 135,00/dia (R$ 90 + 50%).

### RN-007 — Prazo de Competência para Lançamento (até 3 meses)
**Regra:** A data da despesa deve estar dentro da janela de até 3 meses retroativos a contar da competência.
**Origem:** Política de Reembolso v3/v4.
**Aceite:** Em relatório `2026-07`, despesas até `2026-04-01` são aceitas.

### RN-008 — Detecção e Tratamento de Duplicatas
**Regra:** Despesas com mesmo valor em moeda original, mesma data e mesma categoria para o mesmo colaborador são duplicatas. A primeira ocorrência é mantida; posteriores são 100% recusadas ("Despesa duplicada").
**Origem:** Política de Reembolso v3/v4.
**Aceite:** Segunda ocorrência idêntica é recusada.

### RN-009 — Validação de Categorias Permitidas e Coworking
**Regra:** As categorias válidas dependem do Centro de Custo do colaborador. `coworking` é válida e sem teto tabelado. Comparação case-insensitive.
**Origem:** Política de Reembolso v4.
**Aceite:** Categoria `coworking` é aprovada 100% se possuir NF respeitando o limite.

### RN-010 — Arredondamento Monetário Padrão
**Regra:** Todos os cálculos e valores exibidos no JSON final são arredondados para 2 casas decimais (half-up).
**Origem:** Padrão de precisão financeira.
**Aceite:** Cotações e centavos BRL arredondam precisamente.

### RN-011 — Processamento de Estornos (Valores Negativos)
**Regra:** Lançamentos com valor negativo representam estornos e abatem do acumulado do dia.
**Origem:** Política de Reembolso v3/v4.
**Aceite:** Estorno de R$ -45,00 abate R$ 45,00 da categoria no dia.

### RN-012 — Elegibilidade de Fins de Semana e Feriados
**Regra:** Despesas em fins de semana/feriados são elegíveis se cumprirem as demais regras.
**Origem:** Análise prática.
**Aceite:** Jantar de sábado (`e-004`) em viagem com NF é aprovado.

### RN-013 — Validação de Datas Futuras/Fora da Competência
**Regra:** Despesas com data posterior ao `periodo.fim` são 100% recusadas.
**Origem:** Integridade temporal.
**Aceite:** Data posterior ao fim do mês é recusada.

### RN-014 — Validação de Consistência dos Dados
**Regra:** Despesas com `valor == 0.00` ou dados corrompidos são 100% recusadas.
**Origem:** Qualidade de dados.
**Aceite:** Valor zerado é recusado.

### RN-015 — Leitura Dinâmica de Limites por Centro de Custo
**Regra:** Os limites de cada categoria são carregados dinamicamente do arquivo de política (`politica-v4.json`). Se o centro de custo informado no colaborador não constar na tabela, utiliza-se a política `padrao`.
**Origem:** Política de Reembolso v4, Item A.
**Aceite:** Colaborador no `CC-SUPORTE-N2` (não cadastrado) recebe os limites da política `padrao` (R$ 60 alimentacao, R$ 80 transporte, R$ 250 hospedagem).

### RN-016 — Restrição Absoluta de Categoria por Centro de Custo (Limite R$ 0,00)
**Regra:** Quando o limite de uma categoria na tabela do Centro de Custo for R$ 0,00 (ex: `hospedagem` em `CC-ENG-PLATAFORMA`), qualquer lançamento dessa categoria para colaboradores desse centro é 100% RECUSADO com o motivo "Categoria não reembolsável para o centro de custo". Hospedagem com limite 0 não ativa estado de viagem.
**Origem:** Política de Reembolso v4, Item A.
**Aceite:** Hospedagem no `CC-ENG-PLATAFORMA` é recusada 100%.

### RN-017 — Categoria Representação
**Regra:** A categoria `representacao` é válida exclusivamente para centros de custo que a possuam em sua tabela (ex: `CC-COMERCIAL` com teto de R$ 300,00/dia). Se um colaborador de outro centro de custo sem a categoria `representacao` (ex: `CC-SUPORTE-N2`) lançar `representacao`, a despesa é 100% RECUSADA.
**Origem:** Política de Reembolso v4, Item A.
**Aceite:** Item `e-001` (`representacao` no `CC-COMERCIAL`) é elegível. Item `f-003` (`representacao` no `CC-SUPORTE-N2`) é RECUSADO.

### RN-018 — Conversão de Moeda Estrangeira via PTAX (Câmbio)
**Regra:** Quando o campo `moeda` for informado e diferente de `BRL`:
- Busca-se a taxa de câmbio da moeda para a data da despesa em `cambio.json`.
- Se a data não tiver cotação (ex: fins de semana / feriados bancários), adota-se a **última cotação disponível anterior** à data.
- Se a moeda não tiver taxa cadastrada no arquivo de câmbio (ex: `GBP`), a despesa é 100% RECUSADA ("Sem taxa de câmbio disponível para a moeda").
**Origem:** Política de Reembolso v4, Item B.
**Aceite:** `e-002` (22 EUR em 14/07 com EUR=5.93) -> R$ 130.46 BRL. `e-004` (30 EUR em 18/07 Sábado) -> utiliza taxa de 17/07 (5.96) = R$ 178.80 BRL. `e-006` (55 GBP) -> RECUSADA por ausência de taxa para GBP.

### RN-019 — Avaliação de Limites e Nota Fiscal sobre o Valor Convertido em BRL
**Regra:** O valor da despesa na moeda original é convertido imediatamente para BRL (`valor_brl_centavos = float_to_cents(valor_original * taxa)`). Todas as validações subsequentes (exigência de Nota Fiscal >= R$ 100,00 e limites diários) são realizadas sobre esse valor em BRL.
**Origem:** Política de Reembolso v4, Item B.
**Aceite:** `e-003` (14.50 EUR * 5.88 = R$ 85.26 BRL < R$ 100.00) -> Aprovado sem NF. `e-005` (40.00 USD * 5.50 = R$ 220.00 BRL >= R$ 100.00) sem NF -> Recusado por falta de NF em BRL.

---

## 6. Ambiguidades identificadas e decisões

*(Mantidas AMB-001 a AMB-013 da v1.1 e adicionadas AMB-014 a AMB-019)*

### AMB-014 — Categoria ausente na tabela do Centro de Custo
**Texto original do RH:** "Alguns centros de custo não têm entrada na tabela. Nesse caso, aplica-se a política padrão."
**O que não está claro:** E quando o centro de custo EXISTE na tabela, mas uma categoria específica não está no objeto dele (ex: `hospedagem` no `CC-ADM` ou `representacao` no `padrao`)?
**Decisão:** Se a categoria não estiver no Centro de Custo, busca no `padrao`. Se não estiver no Centro de Custo **nem** no `padrao`, a categoria é considerada não autorizada para o CC e é 100% RECUSADA.
**Justificativa:** Proteção do orçamento corporativo impedindo lançamentos não previstos para aquela diretoria.
**Regra afetada:** RN-015, RN-017.

### AMB-015 — Hospedagem com limite R$ 0,00 e status "Em Viagem"
**Texto original do RH:** "CC-ENG-PLATAFORMA não reembolsa hospedagem de forma alguma."
**O que não está claro:** Uma hospedagem lançada por um colaborador desse CC (que será recusada) ativa a ampliação de 50% de viagem para alimentação/transporte?
**Decisão:** Hospedagem com limite R$ 0,00 ou recusada por política de CC **não ativa** o status de viagem.
**Justificativa:** Se a viagem não foi aprovada nem financiada pelo centro de custo, os tetos adicionais não são concedidos.
**Regra afetada:** RN-006, RN-016.

### AMB-016 — Data de despesa sem publicação de cotação PTAX (Fins de semana)
**Texto original do RH:** "A conversão usa a taxa da data da despesa, não a taxa de hoje. As taxas estão em cambio.json."
**O que não está claro:** O arquivo `cambio.json` só possui taxas em dias úteis bancários. Como converter uma despesa em moeda estrangeira realizada em um sábado (ex: `e-004` em 18/07/2026)?
**Decisão:** Quando a data da despesa não contiver taxa cadastrada, utiliza-se a **última taxa de câmbio disponível no histórico anterior** à data.
**Justificativa:** Norma contábil padrão: na ausência de PTAX no dia não útil, aplica-se a cotação do último fechamento útil anterior.
**Regra afetada:** RN-018.

### AMB-017 — Moeda estrangeira não constante na tabela de câmbio
**Texto original do RH:** "Colaboradores em viagem internacional lançam despesas em moeda estrangeira... As taxas estão em cambio.json."
**O que não está claro:** O que fazer quando o lançamento vier em uma moeda não presente em `cambio.json` (ex: `GBP` no item `e-006`)?
**Decisão:** Se a moeda for diferente de `BRL` e não possuir cotação em `cambio.json`, a despesa é 100% RECUSADA com o motivo "Sem taxa de câmbio disponível para a moeda GBP".
**Justificativa:** Impossibilidade de realizar conversão oficial auditável sem taxa homologada.
**Regra afetada:** RN-018.

### AMB-018 — Momento e precisão da conversão monetária
**Texto original do RH:** "Os limites da política são sempre em BRL. Uma despesa em EUR é convertida antes de ser comparada ao limite."
**O que não está claro:** Em que momento ocorre a conversão e como os centavos são tratados?
**Decisão:** A conversão ocorre no **parsing da entrada**: `valor_brl_centavos = float_to_cents(valor_original * taxa_cambio)`. É esse valor em BRL que passa pelas validações de NF e limites.
**Justificativa:** Unifica o pipeline de cálculo em moeda nacional corrente BRL.
**Regra afetada:** RN-018, RN-019.

### AMB-019 — Obrigatoriedade de Nota Fiscal (R$ 100,00) em compras internacionais
**Texto original do RH:** "Nota fiscal é obrigatória acima de R$ 100."
**O que não está claro:** A régua de R$ 100,00 aplica-se ao valor na moeda estrangeira (ex: 22.00 EUR) ou ao valor convertido em BRL?
**Decisão:** A régua de R$ 100,00 aplica-se exclusivamente ao **valor equivalente em BRL** (`valor_brl >= 100.00`).
**Justificativa:** O limite fiscal da política é estipulado em moeda corrente nacional (BRL).
**Regra afetada:** RN-005, RN-019.

---

## 7. Casos de borda

| Caso | Entrada | Comportamento esperado | Regra |
|---|---|---|---|
| Categoria Representação no CC Comercial | `e-001` (R$ 340.00, `representacao`, `CC-COMERCIAL`, teto R$ 300.00) | Aprovado parcial: R$ 300.00 aprovados, R$ 40.00 recusados. | RN-004, RN-017 |
| Despesa EUR com cotação PTAX e com NF | `e-002` (22.00 EUR em 14/07, cotação 5.93 = R$ 130.46 BRL, com NF) | Aprovada integralmente em BRL (R$ 130.46 <= R$ 135.00 teto viagem CC-COMERCIAL). | RN-018, RN-019 |
| Despesa EUR sem NF menor que R$ 100 BRL | `e-003` (14.50 EUR em 15/07, cotação 5.88 = R$ 85.26 BRL, sem NF) | Aprovada em BRL (R$ 85.26 < R$ 100.00 é isenta de NF). | RN-005, RN-019 |
| Despesa EUR em Sábado (Sem PTAX no dia) | `e-004` (30.00 EUR em 18/07 Sábado, cotação fallback de 17/07 = 5.96 -> R$ 178.80 BRL) | Aprovada em BRL usando fallback da cotação de 17/07. | RN-012, RN-018 |
| Despesa USD sem NF acima de R$ 100 BRL | `e-005` (40.00 USD em 20/07, cotação 5.50 = R$ 220.00 BRL, sem NF) | RECUSADA por ausência de Nota Fiscal (R$ 220.00 BRL >= R$ 100.00 BRL). | RN-005, RN-019 |
| Despesa em moeda não cadastrada (GBP) | `e-006` (55.00 GBP no `CC-COMERCIAL`) | RECUSADA 100% por falta de taxa de câmbio para a moeda GBP. | RN-018 |
| Hospedagem 3 noites CC-COMERCIAL em BRL | `e-007` (R$ 1200.00, `hospedagem`, `CC-COMERCIAL`, 3 noites) | Aprovada integralmente (teto 3 * R$ 400 = R$ 1200.00). Ativa viagem. | RN-003, RN-006 |
| Colaborador de CC Desconhecido | `f-001` no `CC-SUPORTE-N2` | Aprovada usando a tabela `padrao` (teto R$ 60.00 alimentacao). | RN-015 |
| Representação em CC Desconhecido | `f-003` (`representacao` no `CC-SUPORTE-N2`) | RECUSADA 100% por categoria não autorizada para o centro de custo. | RN-017 |

---

## 8. Ordem de aplicação das regras

Para cada despesa no arquivo de entrada, a pipeline de avaliação segue a seguinte ordem sequencial:

1. **Conversão de Câmbio e Moeda (RN-018, AMB-016, AMB-017):** Identifica a moeda. Se BRL, taxa = 1.0. Se moeda estrangeira, busca PTAX em `cambio.json` (ou fallback de data anterior). Se moeda não suportada, recusa 100%. Converte o valor para `valor_brl_centavos`.
2. **Consistência de Dados e Valor (RN-014):** Se `valor_brl_centavos == 0` ou dados inválidos, recusa 100%.
3. **Validação de Categoria por Centro de Custo (RN-009, RN-015, RN-016, RN-017, AMB-014):** Verifica se a categoria existe na tabela do CC (ou `padrao`). Se tiver limite R$ 0,00 ou for omitida em CC e padrão, recusa 100%.
4. **Validação de Prazo de Competência e Datas (RN-007, RN-013):** Se anterior a 3 meses ou posterior a `periodo.fim`, recusa 100%.
5. **Detecção de Duplicata (RN-008):** Se for duplicata de despesa processada antes com menor ID, recusa 100%.
6. **Validação de Comprovante Fiscal em BRL (RN-005, AMB-003, AMB-019):** Se `valor_brl_centavos >= 10000` e `tem_nota_fiscal` for `false`, recusa 100%.
7. **Cálculo do Teto Elegível e Estado de Viagem (RN-003, RN-006, RN-012, RN-015, AMB-015):** Determina se o dia está em viagem (+50% nos limites do CC) e calcula o teto diário disponível em BRL.
8. **Aplicação do Limite Acumulado e Reembolso Parcial em BRL (RN-001, RN-002, RN-004, RN-010, RN-011):** Atualiza o acumulado em BRL no dia e aprova total, parcialmente ou recusa.

---

## 9. Critérios de aceite

O motor de reembolso estará aceito na v2.0 quando:

- [ ] Ler arquivos de política externa (`politica-v4.json`) e câmbio (`cambio.json`).
- [ ] Processar com 100% de aprovação nos testes os datasets `despesas-envelope.json` e `despesas-envelope-cc-desconhecido.json`.
- [ ] Manter retrocompatibilidade de execução com a suíte de testes original da v1.1.
- [ ] Passar em 100% dos testes unitários e de integração no `pytest`.

---

## 10. O que fica em aberto

- **Fila de aprovação manual para valores > R$ 500 (Item C opcional):** Como declarado fora de escopo, itens com valor reembolsável > R$ 500 continuam sendo aprovados/processados normalmente pelo motor automático nesta versão.
