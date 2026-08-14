# GEMINI.md

> Este arquivo é lido pelo Gemini / Antigravity AI no início de toda sessão. 
> Ele define as regras de engenharia, convenções de commits e a automação do fluxo SDD.

## O projeto

Motor de cálculo de reembolso de despesas corporativas. CLI que lê um JSON de
despesas e emite um JSON com o valor reembolsável e a justificativa de cada item.

## Fonte da verdade

- `specs/001-motor-reembolso/spec.md` define **o que** o sistema faz.
- `specs/001-motor-reembolso/plan.md` define **como**.
- `specs/001-motor-reembolso/tasks.md` define **em que ordem**.
- `specs/001-motor-reembolso/DECISIONS.md` registra **mudanças de rumo e ambiguidades**.

Quando o código e a spec discordarem, a spec está certa e o código é o bug —
a menos que a spec esteja errada, e nesse caso corrigimos a spec primeiro,
registramos em `DECISIONS.md` e atualizamos o código em seguida.

⚠️ **Antes de implementar qualquer coisa, leia a task correspondente em `tasks.md`.**
Se o que o usuário pedir não estiver coberto por nenhuma task, avise-o em vez de implementar.

## Regras de trabalho e Rastreabilidade

1. **Bug de Spec (Penalidade −5):** Toda regra de negócio vive na spec, não no chat e não em comentário de código. Se o usuário explicar uma regra de negócio que não está na spec, **pare e avise-o imediatamente** para atualizar a spec primeiro.
2. **Commits Obrigatórios:** Todo commit deve referenciar uma task ou documento:
   - Funcionalidade/Código: `feat(T-00X): <descrição>`
   - Testes: `test(T-00X): <descrição>`
   - Documentação: `docs(spec):`, `docs(plan):`, `docs(tasks):`, `docs(decisions):`
3. **Testes Obrigatórios:** Nenhuma regra de negócio entra no sistema sem teste automatizado cobrindo os caminhos felizes e casos de borda.

## Salvamento Automático de Sessões (`docs/sessions/`)

Ao final de cada etapa ou sessão de trabalho, o assistente deve auxiliar na geração e salvamento do log da conversa em `docs/sessions/` usando a seguinte nomenclatura:
- `docs/sessions/01-especificacao-spec.md`
- `docs/sessions/02-planejamento-tasks.md`
- `docs/sessions/03-implementacao-core.md`
- `docs/sessions/04-envelope-dia2.md`
- `docs/sessions/05-relatorio-final.md`

Cada log em markdown deve incluir: Data, Resumo do que foi feito, Prompts/Respostas principais, Arquivos modificados e Lista de commits gerados.

## Stack e Comandos

- Linguagem: Python 3.12 (ou Node.js/TypeScript)
- Rodar CLI: `python -m src.cli calcular --input <caminho_input> --output <caminho_output>`
- Rodar Testes: `pytest`
- Lint/Format: `flake8` / `black`

## Convenções de Código e Precisão Monetária

- **Valores Monetários:** Representados internamente como **inteiros em centavos** (ex: R$ 60,00 ➔ `6000`) para evitar bugs de arredondamento de float (`0.1 + 0.2`).
- **Nomenclatura:** Funções e variáveis em snake_case. Classes em PascalCase.
- **Tratamento de Erros:** Erros de validação de JSON de entrada devem gerar mensagens claras no terminal sem crashar com traceback não tratado.

## Fora de Escopo

- Interface gráfica (GUI) ou aplicação web.
- Leitura de imagens/comprovantes de nota fiscal via OCR.
- Integração com sistemas de pagamentos bancários ou envio de e-mails.