# Relatório — Desafio SDD

**Aluno:** Desenvolvedor SDD · **Repositório:** sdd-desafio · **Data:** 2026-08-14

> Isto não é redação. São **evidências**. Toda afirmação vem acompanhada de arquivo, hash de commit ou trecho de sessão exportada.

---

## Delegação

*O que você fez, o que o assistente IA fez, e por que dividiu assim.*

**A divisão:**

| Atividade | Quem | Por quê |
|---|---|---|
| Identificar ambiguidades | Humano + IA | O humano trouxe a lista de regras/dúvidas do RH e a IA analisou `despesas-exemplo.json` e os arquivos do envelope para encontrar casos ocultos (`AMB-011` a `AMB-019`). |
| Decidir as ambiguidades | Humano | Decisão de negócio e política corporativa cabe ao humano; a IA apoia com alternativas. |
| Escrever a spec | IA (sob revisão humana) | A IA garante formatação e ausência de vazamento técnico; o humano aprova cada seção (`spec.md` v1.0, v1.1 e v2.0). |
| Desenhar a arquitetura | IA + Humano | O humano exigiu a estratégia de centavos (`int`); a IA desenhou a pipeline modular em `plan.md`. |
| Implementar | IA (guiada pelas tasks) | A IA gera o código limpo orientado às fatias `T-001` a `T-017`. |
| Escrever testes | IA + Humano | A IA escreveu os arquivos de teste; o humano revisou e corrigiu asserções incorretas. |
| Absorver o envelope | Humano + IA | A IA mapeou os impactos da Política v4 e implementou as novas regras dinâmicas sob orientação do humano. |

**Onde deleguei e me arrependi:**
Deleguei a escrita inicial do teste de integração (`test_t010_integration.py`) sem especificar os valores esperados calculados na mão. A IA reutilizou um valor estático de exemplo (`2046.93`) que estava no template da `spec.md`, fazendo o teste falhar no primeiro `pytest`.

**Onde não deleguei e deveria ter delegado:**
A formatação dos cenários de teste da tabela de casos de borda poderia ter sido gerada automaticamente via IA antes, acelerando a escrita dos testes unitários da Fase 1.

**Usei subagentes / skills / MCP / hooks?**
Sim. Utilizei as diretrizes do workflow SDD e a inspeção silenciosa de logs para refinar o código e executar a suíte `pytest` a cada commit.

---

## Descrição

*Como você transformou requisito ambíguo em requisito verificável.*

**Requisito ambíguo escolhido:** Item 3 da Política ("Hospedagem tem limite de R$ 250 por diária") cruzado com a despesa `d-010` de `despesas-exemplo.json`.

**Versão 1 (primeira escrita / texto do RH):**
> *"3. Hospedagem tem limite de R$ 250 por diária."*

**Versão final na `spec.md` (`RN-003` e `AMB-010`):**
> *"Despesas na categoria hospedagem possuem teto padrão de R$ 250,00 por diária (ou R$ 375,00 se em viagem). Para estadias cobrindo múltiplas diárias em um único lançamento (ex: R$ 480,00 por 2 diárias), o limite aplicável é `quantidade_diarias * limite_diaria`. A quantidade de diárias é extraída da descrição do lançamento."*

**O que estava ambíguo:**
A despesa `d-010` possui valor bruto de R$ 480,00 em um único lançamento na data `2026-07-14`. Se o sistema aplicasse o limite simples de 1 diária (R$ 250,00 ou R$ 375,00), cortaria o valor indevidamente. Como a descrição informa "2 diárias", o teto do lançamento é 2 × R$ 375,00 = R$ 750,00, tornando a despesa de R$ 480,00 totalmente aprovada.

**Como percebi:**
Ao inspecionar o arquivo [`exemplos/despesas-exemplo.json`](file:///c:/Users/sirll/OneDrive/%C3%81rea%20de%20Trabalho/IA%20NTT/desafio/sdd-desafio/exemplos/despesas-exemplo.json#L95-L102) na linha 98 (`"Hotel Rio - 2 diarias"`), notou-se a contradição entre um lançamento único de R$ 480,00 e o limite unitário de R$ 250,00.

**Commits da mudança:** [`a0f47fe`](file:///c:/Users/sirll/OneDrive/%C3%81rea%20de%20Trabalho/IA%20NTT/desafio/sdd-desafio) (spec v1.0) e [`96b7090`](file:///c:/Users/sirll/OneDrive/%C3%81rea%20de%20Trabalho/IA%20NTT/desafio/sdd-desafio) (spec v1.1).

---

## Discernimento

*Onde a IA errou e você pegou.*

### Caso 1 — Alucinação de Totais no Teste de Integração Ponta a Ponta

**O que ele propôs:**
No arquivo [`tests/test_t010_integration.py`](file:///c:/Users/sirll/OneDrive/%C3%81rea%20de%20Trabalho/IA%20NTT/desafio/sdd-desafio/tests/test_t010_integration.py), a IA gerou a seguinte asserção para o total solicitado:
```python
assert resumo["total_solicitado"] == 2046.93
```

**Por que estava errado:**
O valor `2046.93` não era a soma das despesas do arquivo `despesas-exemplo.json`. A IA alucinou reutilizando o valor ilustrativo que estava presente no exemplo do template da `spec.md`. A soma matemática real dos 14 lançamentos do JSON de entrada é **R$ 1.816,84**.

**Como eu detectei:**
Executei o comando `python -m pytest tests/test_t010_integration.py` e o teste falhou com o erro:
`AssertionError: assert 1816.84 == 2046.93`.

**O que eu fiz:**
Analisei o diff do teste, efetuei o somatório manual e corrigi as asserções no arquivo [`tests/test_t010_integration.py`](file:///c:/Users/sirll/OneDrive/%C3%81rea%20de%20Trabalho/IA%20NTT/desafio/sdd-desafio/tests/test_t010_integration.py) para validar os totais reais exatos (`total_solicitado: 1816.84`, `total_aprovado: 820.43`, `total_recusado: 996.41`, `aprovadas: 9`, `recusadas: 5`).

**Onde está a evidência:**
Documentado em [`docs/sessions/03-implementacao-tdd-fase-base.md`](file:///c:/Users/sirll/OneDrive/%C3%81rea%20de%20Trabalho/IA%20NTT/desafio/sdd-desafio/docs/sessions/03-implementacao-tdd-fase-base.md) (Seção T-010) e no commit `ac0769a`.

### Caso 2 — Padrão Observado

**Padrão que notei:**
A IA tende a copiar valores fictícios de mocks anteriores em testes de integração em vez de calcular dinamicamente a soma dos inputs. Sempre que houver asserção numérica de resumo, a validação empírica via log do `pytest` é indispensável.

---

## Diligência

*O que você verificou antes de aceitar.*

**Meu procedimento de verificação:**
1. Para cada task, li o arquivo de teste gerado antes da implementação da feature.
2. Rodei `python -m pytest tests/test_tXXX.py` e verifiquei o status de aprovação.
3. Inspecionei o `git diff` antes de efetuar o `git commit`.
4. Executei a CLI com o comando final e inspecionei visualmente o JSON gerado em [`resultado.json`](file:///c:/Users/sirll/OneDrive/%C3%81rea%20de%20Trabalho/IA%20NTT/desafio/sdd-desafio/resultado.json).

**Li o diff inteiro em que porcentagem das entregas?**
100% das entregas de código e spec foram lidas na íntegra.

**O que aceitei sem verificar direito, e o que me custou:**
No primeiro rascunho de `T-010`, não conferi os totais antes de rodar o teste, o que custou 1 falha de suíte que precisou de ajuste manual na asserção.

**Testes: quem escreveu, e como você sabe que eles testam a coisa certa?**
Os testes foram escritos em TDD com base na Seção 7 da `spec.md` (Casos de Borda). Sei que testam a coisa certa porque cobrem tanto os caminhos felizes quanto a negação dos requisitos.

---

## O envelope

*A mudança de requisito do Dia 2.*

**Quantos arquivos toquei na mão:** `4` arquivos de código (`models.py`, `parser.py`, `engine.py`, `cli.py`) e `4` arquivos de documentação (`spec.md`, `DECISIONS.md`, `plan.md`, `tasks.md`).
**Quanto tempo levou:** Aproximadamente 45 minutos.
**Diff de absorção:** `9` arquivos commitados no envelope (`+566/-340` linhas).

**Absorveu de graça:**
A arquitetura em pipeline funcional e a representação monetária em inteiros centavos (`int`) absorveram a conversão PTAX sem alterar a lógica de comparadores ou o calculador de acumulado diário.

**Resistiu:**
Os limites estáticos rígidos no código (`LIMITES_PADRAO_CENTAVOS`) precisaram ser encapsulados dentro da nova classe `GerenciadorPolitica` para suportar leitura dinâmica por Centro de Custo sem quebrar a retrocompatibilidade com a v1.1.

**Ordem em que fiz:**
1. Leitura do comunicado e atualização da `spec.md` v2.0 (`AMB-014` a `AMB-019`).
2. Registro da decisão `D-003` em `DECISIONS.md`.
3. Planejamento das novas tarefas `T-013` a `T-017` em `tasks.md`.
4. Commit da especificação antes de alterar qualquer código.
5. Execução TDD incremental de `T-013` a `T-017` com commits separados.

**Se eu tivesse escrito a spec original sabendo desta mudança:**
Teria definido desde a v1.0 que a tabela de limites seria um dicionário injetável por centro de custo, em vez de definir constantes globais de categorias na raiz do módulo.

**O que a spec me poupou, em concreto:**
Poupou retrabalho ao definir previamente a regra de fallback PTAX para fins de semana (`AMB-016`) e a recusa imediata de moedas não suportadas (`AMB-017`), evitando que testes falhassem silenciosamente por erro de conversão.

---

## Fechamento

**Para qual tamanho de projeto isto valeu a pena?**
Para projetos com regras de negócio compostas e sujeitas a auditoria/compliance, onde ambiguidades não documentadas geram bugs caros em produção.

**Para qual não valeria?**
Scripts descartáveis de uso único (*one-off scripts*) ou protótipos de interface sem lógica de backend.

**O que eu faria diferente:**
Teria criado uma fixture de teste com os dados calculados de `despesas-exemplo.json` logo na `T-001` para servir de referência constante.

**A coisa mais desconfortável que aprendi sobre como eu trabalho com IA:**
Que é tentador aceitar um teste que passou sem ler o que ele estava testando; a disciplina de exigir que o teste falhe primeiro ou conferir o valor esperado é o que realmente garante a qualidade no SDD.
