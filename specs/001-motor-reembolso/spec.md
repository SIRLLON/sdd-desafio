# Spec — Motor de Cálculo de Reembolso

**Versão:** 1.1 · **Status:** aprovado · **Última alteração:** 2026-08-14

---

## 1. Problema

A empresa realiza a análise e o cálculo de reembolso de despesas de colaboradores através de um processo manual em planilhas. Essa abordagem gera demora no processamento, inconsistências na aplicação da política corporativa e alto risco de erros humanos no cômputo de limites e elegibilidade.

## 2. Objetivo

Prover um motor automatizado e determinístico de cálculo de reembolso que receba um conjunto de despesas de um colaborador, aplique rigorosamente as regras da política de reembolso (incluindo tratamento de limites, duplicatas, notas fiscais, estornos, fins de semana e viagens) e gere um relatório detalhado de aprovações, recusas parciais ou totais com justificativas explícitas.

## 3. Fora de escopo

- Integração direta com gateways de pagamento ou sistemas bancários.
- Leitura automatizada ou OCR de imagens de notas fiscais (o campo `tem_nota_fiscal` é fornecido pronto na entrada).
- Interface gráfica (GUI) ou painel web (o sistema opera exclusivamente via interface de linha de comando CLI).
- Autenticação, autorização de usuários ou controle de permissões.
- Persistência em banco de dados de relatórios históricos.

---

## 4. Entrada e saída

### Entrada

A entrada é um arquivo JSON no formato definido em `exemplos/despesas-exemplo.json`.

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
| `despesas[].valor` | Number | Valor monetário original lançado | Sim |
| `despesas[].tem_nota_fiscal` | Boolean | Indica se possui comprovante fiscal anexado | Sim |

---

### Saída

A saída é um arquivo JSON gerado pelo motor com a consolidação dos reembolsos e o detalhamento de cada item.

**Campos da Saída:**

| Campo | Tipo | Significado |
|---|---|---|
| `colaborador.id` | String | Identificador do colaborador |
| `colaborador.nome` | String | Nome do colaborador |
| `colaborador.centro_custo` | String | Centro de custo |
| `periodo.competencia` | String | Competência do relatório |
| `resumo.total_solicitado` | Number | Soma dos valores brutos de todas as despesas |
| `resumo.total_aprovado` | Number | Soma total a ser reembolsada ao colaborador |
| `resumo.total_recusado` | Number | Soma dos valores cortados ou rejeitados |
| `resumo.total_despesas` | Integer | Quantidade de despesas processadas |
| `resumo.despesas_aprovadas` | Integer | Quantidade de despesas totalmente ou parcialmente aprovadas |
| `resumo.despesas_recusadas` | Integer | Quantidade de despesas 100% recusadas |
| `itens` | Array de Objetos | Resultado individual de cada despesa |
| `itens[].id` | String | Identificador da despesa |
| `itens[].status` | String | Status final: `APROVADO`, `APROVADO_PARCIAL`, `RECUSADO` |
| `itens[].valor_solicitado` | Number | Valor original submetido |
| `itens[].valor_aprovado` | Number | Valor final concedido para reembolso |
| `itens[].valor_recusado` | Number | Valor retido ou cortado |
| `itens[].justificativas` | Array de Strings | Lista de motivos de aprovação/recusa ou cortes aplicados |

#### Exemplo de Saída JSON:

```json
{
  "colaborador": {
    "id": "c-0417",
    "nome": "Marina Volpi",
    "centro_custo": "CC-ENG-PLATAFORMA"
  },
  "periodo": {
    "competencia": "2026-07"
  },
  "resumo": {
    "total_solicitado": 2046.93,
    "total_aprovado": 1332.20,
    "total_recusado": 714.73,
    "total_despesas": 14,
    "despesas_aprovadas": 8,
    "despesas_recusadas": 6
  },
  "itens": [
    {
      "id": "d-001",
      "status": "APROVADO_PARCIAL",
      "valor_solicitado": 72.50,
      "valor_aprovado": 60.00,
      "valor_recusado": 12.50,
      "justificativas": ["Aprovado parcialmente até o teto diário de alimentação (R$ 60.00). Excedente cortado."]
    },
    {
      "id": "d-002",
      "status": "RECUSADO",
      "valor_solicitado": 38.00,
      "valor_aprovado": 0.00,
      "valor_recusado": 38.00,
      "justificativas": ["Recusado: teto diário da categoria alimentação já atingido na data."]
    }
  ]
}
```

---

## 5. Regras de negócio

### RN-001 — Limite Diário de Alimentação
**Regra:** Despesas na categoria `alimentacao` possuem teto padrão de R$ 60,00 por dia por colaborador.
**Origem:** Política de Reembolso v3, item 1.
**Aceite:** Duas despesas de R$ 40,00 no mesmo dia resultarão em R$ 40,00 aprovados para a primeira e R$ 20,00 aprovados para a segunda (total R$ 60,00 no dia).

### RN-002 — Limite Diário de Transporte Urbano
**Regra:** Despesas na categoria `transporte_urbano` (ou `transporte`) possuem teto padrão de R$ 80,00 por dia por colaborador.
**Origem:** Política de Reembolso v3, item 2.
**Aceite:** Uma despesa de R$ 90,00 sem viagem aprova R$ 80,00 e recusa R$ 10,00.

### RN-003 — Limite Diário de Hospedagem
**Regra:** Despesas na categoria `hospedagem` possuem teto padrão de R$ 250,00 por diária. Para estadias cobrindo múltiplas diárias, o teto é `quantidade_diarias * limite_diaria`.
**Origem:** Política de Reembolso v3, item 3.
**Aceite:** Lançamento de 2 diárias possui teto base de R$ 500,00 (ou R$ 750,00 se em viagem).

### RN-004 — Reembolso Parcial por Excedente de Teto
**Regra:** Quando uma despesa ultrapassa o limite diário disponível para sua categoria, a parcela dentro do teto é aprovada (`status: APROVADO_PARCIAL`) e a parcela excedente é cortada.
**Origem:** Política de Reembolso v3, item 4.
**Aceite:** Despesa de R$ 72,50 com teto disponível de R$ 60,00 gera `valor_aprovado: 60.00` e `valor_recusado: 12.50`.

### RN-005 — Obrigatoriedade de Comprovante Fiscal (Nota Fiscal)
**Regra:** Despesas com valor monetário igual ou superior a R$ 100,00 (`valor >= 100.00`) exigem obrigatoriamente `tem_nota_fiscal: true`. Se `tem_nota_fiscal` for `false`, a despesa é 100% recusada. Despesas de R$ 0,01 a R$ 99,99 não exigem nota fiscal.
**Origem:** Política de Reembolso v3, item 5.
**Aceite:** Despesa de R$ 100,00 com `tem_nota_fiscal: false` é totalmente RECUSADA por ausência de NF. Despesa de R$ 99,99 com `tem_nota_fiscal: false` é elegível.

### RN-006 — Limites Ampliados em Viagem (+50%)
**Regra:** A presença de uma despesa válida de `hospedagem` estabelece o estado de "Em Viagem" para os dias cobertos por essa hospedagem (a partir da data do registro). Durante o período em viagem, os tetos diários de `alimentacao`, `transporte_urbano` e `hospedagem` recebem acréscimo de 50%:
- Alimentação em viagem: **R$ 90,00/dia** (R$ 60 + 50%)
- Transporte urbano em viagem: **R$ 120,00/dia** (R$ 80 + 50%)
- Hospedagem em viagem: **R$ 375,00/diária** (R$ 250 + 50%)
**Origem:** Política de Reembolso v3, item 6.
**Aceite:** Despesa de alimentação de R$ 72,50 em dia de viagem é aprovada integralmente (R$ 72,50 <= R$ 90,00).

### RN-007 — Prazo de Competência para Lançamento (até 3 meses)
**Regra:** A data da despesa deve estar dentro da janela de até 3 meses retroativos a contar do período de competência informado no relatório. Despesas com data anterior a 3 meses do período são 100% recusadas.
**Origem:** Política de Reembolso v3, item 7.
**Aceite:** Em um relatório de competência `2026-07` (julho), despesas de até `2026-04-01` (abril) são aceitas. Despesas de `2026-03-31` ou anteriores são recusadas.

### RN-008 — Detecção e Tratamento de Duplicatas
**Regra:** Despesas que apresentem exatamente o mesmo **valor**, mesma **data** e mesma **categoria** para o mesmo colaborador são consideradas duplicatas. A primeira ocorrência na ordem de ID é mantida e processada normalmente; as ocorrências subsequentes são 100% recusadas com o motivo "Despesa duplicada".
**Origem:** Política de Reembolso v3, item 8.
**Aceite:** Duas despesas de R$ 54,90 no dia `2026-07-09` de `alimentacao`: a primeira (`d-006`) é processada; a segunda (`d-007`) é recusada como duplicata.

### RN-009 — Validação de Categorias Permitidas
**Regra:** As únicas categorias válidas para reembolso são `alimentacao`, `transporte_urbano` (ou `transporte`), `hospedagem` e `coworking`. A comparação é insensível a maiúsculas/minúsculas. Categorias não reconhecidas são 100% recusadas. `coworking` não possui teto específico em tabela (reembolsável 100% do valor elegível).
**Origem:** Política de Reembolso v3, item 9.
**Aceite:** Categoria `ALIMENTACAO` é aceita como `alimentacao`. Categoria `lazer` é recusada.

### RN-010 — Arredondamento Monetário Padrão
**Regra:** Todos os cálculos numéricos monetários e valores finais exibidos no JSON de saída devem utilizar arredondamento padrão matemático (half-up) para exatamente **duas casas decimais**.
**Origem:** Padrão de precisão financeira corporativa.
**Aceite:** Valor `33.333` é arredondado para `33.33`.

### RN-011 — Processamento de Estornos (Valores Negativos)
**Regra:** Lançamentos com valor negativo (ex: `-45.00`) representam estornos ou cancelamentos. Eles são aprovados como valores de crédito e seu montante abate/reduz o total acumulado consumido no dia para aquela categoria, recompondo a margem disponível.
**Origem:** Tratamento de estornos e ajustes financeiros.
**Aceite:** Um estorno de R$ -45,00 em transporte reduz em R$ 45,00 o acumulado do dia em transporte.

### RN-012 — Elegibilidade de Despesas em Fins de Semana e Feriados
**Regra:** Despesas ocorridas em fins de semana (sábado ou domingo) ou feriados são válidas para reembolso, desde que respeitem as demais regras de limite, nota fiscal e categoria.
**Origem:** Análise prática do item `d-012` do arquivo de entrada de exemplo.
**Aceite:** Despesa de alimentação no sábado (`2026-07-18`) com nota fiscal é aprovada normalmente.

### RN-013 — Validação de Período Limite (Datas Futuras ou Fora do Intervalo)
**Regra:** Despesas com data posterior à data final da competência analisada (`periodo.fim`) ou no futuro são 100% recusadas por incoerência temporal.
**Origem:** Integridade de controle temporal de lançamentos.
**Aceite:** Despesa com data `2026-08-05` em relatório de competência `2026-07` (`fim: 2026-07-31`) é RECUSADA.

### RN-014 — Validação de Consistência dos Dados da Despesa
**Regra:** Despesas com valor monetário igual a zero (`valor == 0.00`) ou com campos obrigatórios nulos/em branco são 100% recusadas por inconsistência de dados.
**Origem:** Qualidade e consistência dos dados de entrada.
**Aceite:** Despesa com `valor: 0.00` é RECUSADA.

---

## 6. Ambiguidades identificadas e decisões

### AMB-001 — Aplicação do limite por dia vs por despesa
**Texto original do RH:** "1. Alimentação tem limite de R$ 60 por dia. 2. Transporte urbano tem limite de R$ 80 por dia."
**O que não está claro:** Se o limite é por lançamento individual ou pela soma acumulada de todas as despesas daquela categoria na mesma data.
**Decisão:** O limite aplica-se à **soma acumulada do dia** por colaborador e categoria. As despesas são processadas por ordem de ID. Atingido o teto diário, despesas subsequentes na mesma categoria e data são recusadas.
**Justificativa:** A redação expressa "por dia", o que implica controle do gasto diário acumulado e não da nota individual.
**Regra afetada:** RN-001, RN-002, RN-004.

### AMB-002 — Significado de "reembolsadas parcialmente"
**Texto original do RH:** "4. Despesas acima do limite são reembolsadas parcialmente."
**O que não está claro:** Se a despesa que ultrapassa o teto é aprovada até a margem disponível (cortando o excedente) ou se é totalmente rejeitada por ter estourado o limite.
**Decisão:** Reembolsa-se o valor até atingir o teto disponível. O valor excedente é atribuído ao campo `valor_recusado` e a despesa recebe status `APROVADO_PARCIAL`.
**Justificativa:** Garante o direito do colaborador ao teto estipulado em política sem cobrir o luxo/excesso.
**Regra afetada:** RN-004.

### AMB-003 — Inclusividade do limite de R$ 100 para Nota Fiscal
**Texto original do RH:** "5. Nota fiscal é obrigatória acima de R$ 100."
**O que não está claro:** Se uma despesa de exatamente R$ 100,00 precisa de nota fiscal.
**Decisão:** Valores iguais ou superiores a R$ 100,00 (`valor >= 100.00`) exigem nota fiscal. Valores de R$ 0,01 até R$ 99,99 são isentos.
**Justificativa:** Pragmatismo fiscal corporativo: R$ 100,00 é o valor de corte inclusive para exigência de nota fiscal.
**Regra afetada:** RN-005.

### AMB-004 — Identificação e alcance do status "Em Viagem"
**Texto original do RH:** "6. Colaborador em viagem tem limites ampliados em 50%."
**O que não está claro:** Não existe flag `em_viagem` no JSON de entrada. Como inferir se o colaborador está em viagem e quais despesas/dias recebem a ampliação?
**Decisão:** A presença de uma despesa válida da categoria `hospedagem` ativa o status de viagem para os dias abrangidos por aquela hospedagem. Nesses dias, os limites de alimentação (R$ 90/dia), transporte (R$ 120/dia) e hospedagem (R$ 375/diária) são ampliados em 50%.
**Justificativa:** A despesa de hospedagem é o comprovante material do deslocamento a trabalho em sistemas sem diário de bordo.
**Regra afetada:** RN-006.

### AMB-005 — Regra de período de competência e lançamentos retroativos
**Texto original do RH:** "7. Despesas devem ser lançadas dentro do período de competência."
**O que não está claro:** Qual a janela de tolerância para despesas retroativas em relação ao mês de competência informado no relatório?
**Decisão:** Aceitam-se despesas ocorridas em até 3 meses calendários antes da competência do relatório (ex: em relatório de 2026-07, aceitam-se despesas de 2026-04, 2026-05, 2026-06 e 2026-07). Despesas mais antigas são recusadas.
**Justificativa:** Prática contábil comum de fechamento trimestral para acerto de contas de despesas atrasadas.
**Regra afetada:** RN-007.

### AMB-006 — Definição exata de duplicata e regra de desempate
**Texto original do RH:** "8. Duplicatas devem ser tratadas."
**O que não está claro:** Quais campos definem uma duplicata e qual item da duplicata é mantido?
**Decisão:** Consideram-se duplicatas despesas com a mesma **data**, mesma **categoria** e mesmo **valor** para o mesmo colaborador. A despesa com o **menor ID** (primeira a ser processada) é mantida; as posteriores idênticas são recusadas como duplicatas.
**Justificativa:** Ordem determinística de entrada e prevenção contra lançamentos repetidos por erro do usuário.
**Regra afetada:** RN-008.

### AMB-007 — Categorias válidas, tratamento de Coworking e case-sensitivity
**Texto original do RH:** "9. Categorias fora da política não são reembolsáveis."
**O que não está claro:** Quais categorias são aceitas? Como tratar caixa alta/baixa e categorias sem teto explícito como Coworking?
**Decisão:** Categorias válidas: `alimentacao`, `transporte_urbano` (ou `transporte`), `hospedagem` e `coworking`. A comparação é insensível a maiúsculas/minúsculas. Coworking é categoria válida, não possui teto diário fixado em política (aprovado 100% desde que respeitada a regra de nota fiscal). Categorias desconhecidas são recusadas.
**Justificativa:** Garantir resiliência na entrada de dados e suporte às categorias operacionais observadas nos exemplos reais.
**Regra afetada:** RN-009.

### AMB-008 — Tratamento de arredondamento e precisão decimal
**Texto original do RH:** Não mencionado na política.
**O que não está claro:** Como formatar e calcular despesas com mais de 2 casas decimais (ex: R$ 33.333 em `d-011`)?
**Decisão:** Todos os valores numéricos são arredondados para 2 casas decimais usando arredondamento padrão bancário/matemático (half-up).
**Justificativa:** Garantir precisão e conformidade com o padrão da moeda Real (BRL).
**Regra afetada:** RN-010.

### AMB-009 — Lançamentos de valor negativo (estornos)
**Texto original do RH:** Não mencionado na política.
**O que não está claro:** Como processar uma despesa com valor negativo (ex: `d-009` de R$ -45,00)?
**Decisão:** O estorno é aprovado como crédito, reduzindo o valor acumulado no dia da respectiva categoria, o que pode restaurar saldo de limite diário.
**Justificativa:** Representação contábil correta de devoluções de corridas/serviços cancelados.
**Regra afetada:** RN-011.

### AMB-010 — Múltiplas diárias em uma única nota de hospedagem
**Texto original do RH:** "3. Hospedagem tem limite de R$ 250 por diária."
**O que não está claro:** Como aplicar o teto de R$ 250/diária quando uma nota fiscal consolida 2 ou 3 diárias em um único valor (ex: R$ 480,00 em `d-010` para 2 diárias)?
**Decisão:** Extrai-se o número de diárias a partir da descrição ou campo do lançamento. O limite aplicável à despesa é `quantidade_diarias * limite_diaria_aplicavel`.
**Justificativa:** Hotéis e acomodações (como Airbnb) frequentemente emitem uma única nota fiscal para todo o período de permanência.
**Regra afetada:** RN-003, RN-006.

### AMB-011 — Reembolso de despesas em fins de semana e feriados
**Texto original do RH:** Não mencionado na política.
**O que não está claro:** Gastos ocorridos em sábados, domingos ou feriados (ex: `d-012` em 2026-07-18) são permitidos?
**Decisão:** Despesas em fins de semana e feriados são **válidas e elegíveis**, desde que cumpram os requisitos normais de categoria, limite e nota fiscal.
**Justificativa:** Colaboradores em regime de plantão, viagem ou eventos corporativos necessitam de reembolso nesses dias.
**Regra afetada:** RN-012.

### AMB-012 — Lançamentos com data futura ou posterior ao período
**Texto original do RH:** "7. Despesas devem ser lançadas dentro do período de competência."
**O que não está claro:** O que ocorre se uma despesa tiver data posterior ao `periodo.fim` da competência?
**Decisão:** Despesas com data posterior ao `periodo.fim` são 100% recusadas.
**Justificativa:** Impede a aprovação de gastos futuros não ocorridos na competência.
**Regra afetada:** RN-013.

### AMB-013 — Despesas com valor zerado (`0.00`) ou dados incompletos
**Texto original do RH:** Não mencionado na política.
**O que não está claro:** Como o sistema deve reagir a lançamentos com `valor: 0.00` ou campos obrigatórios vazios?
**Decisão:** Despesas com `valor == 0.00` ou sem descrição/categoria válida são 100% recusadas com a justificativa "Inconsistência de dados ou valor zerado".
**Justificativa:** Manter a integridade contábil e evitar processamento de registros corrompidos.
**Regra afetada:** RN-014.

---

## 7. Casos de borda

| Caso | Entrada | Comportamento esperado | Regra |
|---|---|---|---|
| Múltiplas despesas no mesmo dia ultrapassando o teto | `d-001` (R$ 72.50) e `d-002` (R$ 38.00) no dia 2026-07-03 para `alimentacao` | `d-001` aprova R$ 60.00 e recusa R$ 12.50 (status APROVADO_PARCIAL). `d-002` aprova R$ 0.00 e recusa R$ 38.00 (status RECUSADO por teto esgotado). | RN-001, RN-004 |
| Exatamente R$ 100,00 sem nota fiscal | `d-003` (R$ 100.00, `tem_nota_fiscal: false`) | Status RECUSADO. Valor recusado: R$ 100.00. Motivo: Ausência de Nota Fiscal obrigatória para valores >= R$ 100,00. | RN-005 |
| R$ 99,99 sem nota fiscal | `valor: 99.99`, `tem_nota_fiscal: false` | Status APROVADO (se dentro do teto). Isento de Nota Fiscal. | RN-005 |
| Duplicata idêntica no mesmo dia | `d-006` (R$ 54.90) e `d-007` (R$ 54.90) em 2026-07-09 | `d-006` aprovado. `d-007` status RECUSADO com justificativa "Despesa duplicada". | RN-008 |
| Despesa com 3 casas decimais | `d-011` (R$ 33.333) | `valor_solicitado` e `valor_aprovado` formatados/arredondados para `33.33`. | RN-010 |
| Despesa retroativa de 3 meses | Data da despesa `2026-04-15` em relatório de competência `2026-07` | Aprovada (dentro da janela de 3 meses). | RN-007 |
| Hospedagem sem nota fiscal acima de R$ 100 | `d-013` (R$ 690.00, `hospedagem`, `tem_nota_fiscal: false`) | Status RECUSADO por ausência de Nota Fiscal (R$ 690.00 >= R$ 100.00). | RN-005 |
| Categoria em maiúsculo | `d-014` (`categoria: "ALIMENTACAO"`) | Processada normalmente como `alimentacao`. | RN-009 |
| Estorno de corrida cancelada | `d-009` (R$ -45.00, `transporte_urbano`) | Status APROVADO. Abate R$ 45.00 da soma acumulada do dia de transporte. | RN-011 |
| Plantão de Fim de Semana | `d-012` em um sábado (`2026-07-18`, R$ 47.20) | Status APROVADO. Despesas de fim de semana são válidas. | RN-012 |
| Data futura/após competência | Data `2026-08-01` em competência `2026-07` | Status RECUSADO por data fora do período de competência. | RN-013 |
| Despesa zerada | `valor: 0.00` | Status RECUSADO por inconsistência de dados. | RN-014 |

---

## 8. Ordem de aplicação das regras

Para cada despesa no arquivo de entrada, as regras de avaliação devem ser executadas exatamente na seguinte ordem sequencial de precedência:

1. **Consistência de Dados e Valor (RN-014):** Se `valor == 0.00` ou dados forem truncados/inválidos, recusa 100%.
2. **Validação de Categoria (RN-009):** Se a categoria for inválida/desconhecida, recusa 100% a despesa.
3. **Validação de Prazo de Competência e Data Limite (RN-007, RN-013):** Se a data for anterior ao limite de 3 meses ou posterior ao `periodo.fim`, recusa 100% a despesa.
4. **Detecção de Duplicata (RN-008):** Se for identificada como duplicata de uma despesa já processada com menor ID, recusa 100% a despesa.
5. **Validação de Comprovante Fiscal (RN-005):** Se o valor for >= R$ 100,00 e `tem_nota_fiscal` for `false`, recusa 100% a despesa.
6. **Cálculo do Teto Elegível e Estado de Viagem (RN-003, RN-006, RN-012):** Identifica se a data está sob efeito de viagem (+50% nos limites) e determina o limite máximo aplicável à categoria no dia (incluindo fins de semana).
7. **Aplicação do Limite Acumulado Diário e Reembolso Parcial (RN-001, RN-002, RN-004, RN-010, RN-011):** Atualiza o acumulado do dia (considerando estornos). Aprova integralmente se couber no saldo do teto, aprova parcialmente se exceder o saldo restante do teto, ou recusa 100% se o teto do dia já estiver esgotado.

---

## 9. Critérios de aceite

O motor de reembolso estará aceito e homologado quando:

- [ ] Processar o arquivo de entrada de exemplo `exemplos/despesas-exemplo.json` gerando uma saída JSON válida no formato especificado.
- [ ] Tratar corretamente todas as 14 despesas de exemplo em conformidade com as regras RN-001 até RN-014.
- [ ] Exibir no relatório de resumo os totais consolidados de valores solicitados, aprovados e recusados batendo com a soma dos itens.
- [ ] Conter justificativas claras e compreensíveis em cada item que for recusado ou aprovado parcialmente.
- [ ] Passar em 100% dos testes de unidade e integração automatizados cobrindo todos os casos de borda e regras de negócio.

---

## 10. O que fica em aberto

- **Identificação da quantidade de diárias de hospedagem quando não explícita:** Quando a descrição da hospedagem não trouxer o número de diárias (ex: "Hotel Executivo"), adota-se por padrão a contagem de 1 diária, a menos que a descrição explicite a quantidade (ex: "2 diárias", "3 noites").
