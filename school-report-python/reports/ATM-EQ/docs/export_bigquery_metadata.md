# `export_bigquery_metadata.py`

Script: `school-report-python/reports/ATM-EQ/scripts/export_bigquery_metadata.py`

## O que ele faz

Exporta metadados do BigQuery (datasets, tabelas e campos) e gera um snapshot local com:

- visao tabular para busca rapida (`.csv`)
- visao detalhada por tabela (`.json`)
- catalogo completo consolidado (`full_catalog.json`)
- manifesto com contagens e caminhos (`manifest.json`)
- pasta para exemplos de consulta (`query_examples/`)

## Como executar

No diretorio `school-report-python`:

```bash
uv run python reports/ATM-EQ/scripts/export_bigquery_metadata.py
```

Exemplo com filtros:

```bash
uv run python reports/ATM-EQ/scripts/export_bigquery_metadata.py \
  --project-id meu-projeto \
  --datasets ds_alunos,ds_docentes \
  --dataset-regex "^ds_" \
  --include-views
```

## Parametros

- `--project-id`: projeto GCP. Se omitido, usa `GCP_PROJECT_ID` carregado por `get_local_settings()`.
- `--datasets`: lista de datasets separados por virgula. Ex.: `ds1,ds2`.
- `--dataset-regex`: regex para filtrar nome dos datasets.
- `--include-views`: inclui `VIEW` e `MATERIALIZED_VIEW` (por padrao, sao ignoradas).
- `--output-dir`: diretorio base de saida. Padrao: `school-report-python/output/metadata`.
- `--filename-prefix`: prefixo do diretorio do snapshot. Padrao: `metadata_snapshot`.

## Fluxo de execucao

1. Le argumentos da CLI.
2. Resolve `project_id` (CLI ou configuracao local).
3. Cria `bigquery.Client(project=project_id)`.
4. Lista datasets do projeto e aplica filtros (`--datasets` e `--dataset-regex`).
5. Para cada dataset:
   - busca metadados do dataset
   - lista tabelas
   - opcionalmente ignora views
   - busca schema completo de cada tabela
   - achata schema aninhado (`RECORD`) em linhas de colunas com caminho completo
6. Gera snapshot com arquivos CSV/JSON e imprime resumo final.

## Como o schema e achatado

A funcao `_flatten_schema()` percorre recursivamente os campos da tabela e cria uma linha por campo com:

- `column_name`: nome do campo atual
- `column_path`: caminho completo (ex.: `endereco.cidade`)
- `parent_field`: campo pai imediato
- `depth`: profundidade no schema
- `data_type`, `mode`, `is_nullable`, `is_repeated`
- descricoes e `policy_tags` (quando houver)

Isso permite consultar colunas aninhadas sem depender da estrutura JSON original.

## Estrutura de saida

Cada execucao cria uma pasta timestampada:

```text
<output-dir>/<filename-prefix>_YYYYMMDD_HHMMSS/
  manifest.json
  full_catalog.json
  catalog_index.csv
  column_search.csv
  schemas/
    <dataset_id>/
      <table_id>.json
  query_examples/
    README.md
```

## Arquivos gerados

- `catalog_index.csv`:
  - 1 linha por tabela
  - inclui dataset/tabela, tipo, descricao, `column_count`, `num_rows`, `num_bytes`, datas de criacao/modificacao
- `column_search.csv`:
  - 1 linha por campo (inclui campos aninhados)
  - ideal para busca textual de colunas
- `schemas/<dataset>/<table>.json`:
  - detalhes completos da tabela e lista de colunas achatadas
- `manifest.json`:
  - timestamp, projeto, contagem de datasets/tabelas/campos e caminhos principais
- `full_catalog.json`:
  - catalogo completo (`datasets` + metadados do manifesto)
- `query_examples/README.md`:
  - guia inicial para organizar SQLs de exemplo

## Criterios de selecao de datasets

A selecao e feita em duas etapas (na ordem):

1. filtro exato por `--datasets` (se informado)
2. filtro por regex `--dataset-regex` (se informado)

Ou seja, quando ambos sao usados, o resultado final e a intersecao.

## Codigos de saida

- `0`: sucesso
- `1`: nenhum dataset encontrado apos filtros
- `2`: projeto nao definido (`--project-id` ausente e `GCP_PROJECT_ID` nao configurado)

## Dependencias relevantes

- `google-cloud-bigquery`
- configuracao local via `schoolreport.config.get_local_settings`

## Observacoes praticas

- O script le metadados diretamente do BigQuery; a conta usada precisa de permissoes para listar datasets/tabelas e ler schemas.
- Em projetos grandes, a execucao pode ser demorada porque chama `get_table` para cada tabela.
- `query_examples/` e apenas um placeholder para documentacao SQL posterior.
