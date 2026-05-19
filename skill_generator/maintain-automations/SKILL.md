---
name: maintain-automations
description: Criar, revisar ou melhorar automacoes parametrizadas em C:\codes\skills. Use quando uma atividade se repete mudando apenas parametros, quando um fluxo manual ficar longo, sensivel a erro ou reutilizavel, ou quando Codex precisar transformar pratica recorrente em script, template ou asset dentro da skill dona da atividade.
---

# Manter Automacoes

## Objetivo

Transformar atividades repetitivas em automacoes simples, parametrizadas e mantidas dentro da skill dona da responsabilidade.

## Uso

1. Usar quando a diferenca entre execucoes for principalmente parametros.
2. Usar quando uma tarefa exigir passos mecanicos repetidos.
3. Usar quando uma skill estiver acumulando texto que deveria virar script, template ou asset.
4. Usar em conjunto com `maintain-skills` quando a automacao envolver criar ou revisar skills.

## Limites

1. Nao criar automacao sem ganho real de repeticao, confiabilidade ou economia de contexto.
2. Nao criar regra global dentro desta skill; regras globais ficam no `root`.
3. Nao criar scripts fora da skill dona da atividade.
4. Nao substituir julgamento do Codex por script quando a tarefa exigir decisao contextual.
5. Nao criar dependencias externas sem necessidade clara.
6. Nao criar automacao em outro contexto sem pedido no `plan` do contexto dono.
7. Nao mover automacao para tool global sem plano aprovado no contexto tools.

## Decisao

1. Se a tarefa muda apenas valores de entrada, criar script parametrizado.
2. Se a tarefa copia uma estrutura com pequenas variacoes, criar template ou asset.
3. Se a tarefa exige conhecimento longo mas raramente lido, criar referencia.
4. Se a tarefa exige interpretacao ampla, manter instrucao curta no `SKILL.md`.
5. Se a tarefa pertence a uma area existente, melhorar a skill existente em vez de criar nova skill.
6. Se a tarefa nao tem dona clara e e recorrente, propor skill nova com proposito e limite explicitos.
7. Se o recurso for compartilhado entre contextos, planejar artefato em `C:\codes\tools` e registrar pedido no contexto dono.

## Padrao de script

1. Usar parametros obrigatorios para entradas que mudam por execucao.
2. Usar valores padrao somente para caminhos e opcoes estaveis do workspace.
3. Definir `$ErrorActionPreference = "Stop"` em PowerShell.
4. Validar entradas antes de escrever arquivos.
5. Retornar objeto simples com caminhos, identificadores e status.
6. Testar com caminho temporario quando o script cria arquivos.
7. Documentar o script no `SKILL.md` da skill dona.

## Fluxo

1. Identificar a skill dona da atividade.
2. Verificar se ja existe script, template, asset ou referencia que resolva o caso.
3. Criar ou melhorar o recurso dentro da skill dona.
4. Atualizar o `SKILL.md` da skill dona com uso, limites e script relacionado.
5. Validar a skill alterada com `quick_validate.py` ou `maintain-skills/scripts/validate-skills.ps1`.
6. Registrar no plano aplicavel somente se o padrao for reutilizavel.

## Scripts

1. `scripts/criar-script-parametrizado.ps1`: cria um esqueleto de script PowerShell ou Python dentro da skill dona.


## Correlacao Obrigatoria de Skills

1. Antes de qualquer mudanca persistente, executar `route-skills-by-context`.
2. Registrar na sessao ativa:
- skill executora
- skills de apoio
- motivo da escolha
- validacao da escolha
3. Sem esse registro, manter atividade como `bloqueado`.
