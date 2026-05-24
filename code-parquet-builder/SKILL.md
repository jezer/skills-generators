---
name: code-parquet-builder
description: Extrai blocos AST (imports topo + cada def/class top-level) de arquivos Python listados em um JSON de configuracao e gera parquet+csv ordenado para carga em tabela Delta. Use quando precisar transformar um conjunto de arquivos .py em um artefato versionado de blocos de codigo executavel via exec() no Databricks, com filtragem automatica de imports relativos e absolutos do proprio framework.
---

# code-parquet-builder

## Objetivo

Converter fontes Python (arquivos `.py`) em parquet/csv de blocos ordenados, prontos para serem persistidos em tabela Delta e executados via `exec(..., globals())` em ambiente Databricks. Substitui scripts ad-hoc duplicados por uma chamada generica parametrizada via JSON.

## Uso

1. Criar um arquivo `config.json` (modelo em `templates/config.example.json`) com:
   - `versao`: rotulo de versao (ex.: `v3.0`).
   - `base_python`: caminho absoluto da pasta-raiz dos fontes.
   - `output_dir`: pasta onde salvar os artefatos.
   - `fontes`: lista ordenada `[{ "arquivo", "modulo", "ordem_base" }]`.
   - `init_blocos` (opcional): blocos finais com codigo literal a anexar.
   - `filtros` (opcional): pacotes cujos imports absolutos devem ser removidos (ex.: `["lib_createobj"]`).
2. Executar `scripts/build_code_parquet.py --config caminho.json [--versao vX.Y]`.
3. Saida: `output_dir/tb_<nome>_<versao>.parquet` e `.csv`.

## Limites

1. Nao implanta o parquet no Databricks; apenas gera o artefato local.
2. Nao versiona o `output_dir` (consumidor define a politica de git ignore).
3. Nao executa codigo dos fontes; apenas faz `ast.parse` + extracao textual.
4. Nao decide ordem entre modulos — confia em `ordem_base` informado.
5. Nao concatena fontes; gera um bloco por def/class top-level.

## Fluxo

1. Le `config.json`.
2. Para cada fonte, le o arquivo, faz `ast.parse`, separa bloco de topo (imports/globals) e cada `def`/`class` de nivel top.
3. Filtra de cada bloco: `from .x import y`, `from . import y`, `from {pacote_filtrado}...` e `import {pacote_filtrado}...` para cada item em `filtros`.
4. Atribui `ordem = ordem_base * 10` ao topo e `ordem_base * 10 + i + 1` para cada definicao subsequente.
5. Anexa `init_blocos` literais com a `ordem` informada.
6. Ordena, monta `DataFrame` com colunas `[versao, ordem, modulo, tipo, nome, codigo, descricao, ativo]`.
7. Grava parquet e csv no `output_dir`.

## Scripts

1. `scripts/build_code_parquet.py`: motor de extracao parametrizado.
2. `scripts/build-code-parquet.ps1`: wrapper PowerShell (`-Config caminho.json -Versao vX.Y`).
3. `templates/config.example.json`: exemplo de configuracao.

## Consumidores conhecidos

1. `semaforo-cabecalho` (`C:\codes\skills\domains\products\semaforo-cabecalho`).
2. Espelhos `cnu/11autorizacaodiario.v1.a1/x.semaforo_cabecalho` e `cnu/11autorizacaodiario_v2.v1.a1/x.semaforo_cabecalho` (delegam para esta skill).

## Dependencias

1. Python >= 3.10 com `pandas` e `pyarrow` (`pip install pandas pyarrow`).
2. `maintain-skills` para qualquer alteracao desta skill.
