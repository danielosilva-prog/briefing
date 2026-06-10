# BRIEFING-MUNICIPIO

Relatorio de briefing gerado a partir de arquivo local, sem BigQuery, com uma linha por municipio.

## Uso

```bash
uv run schoolreport generate BRIEFING-MUNICIPIO cod_ibge=2927408 input_file=reports/BRIEFING-MUNICIPIO/data/exemplo_briefing_municipios.csv --output output/briefing-2927408.pdf
```

O arquivo de entrada deve ter uma coluna `cod_ibge` com o codigo IBGE do municipio.
Tambem e recomendado manter as colunas `uf`, `municipio`, `territorio` e `titulo`.

## Estrutura

- `data/exemplo_briefing_municipios.csv`: exemplo de entrada.
- `template/assets/data/sections.json`: contrato que mapeia colunas do arquivo para secoes e linhas do PDF.
- `template/assets/header.png`: imagem usada no cabecalho do PDF, quando existir.
- `template/assets/footer.png`: imagem usada no rodape do PDF, quando existir.
- `executor.py`: le CSV/XLSX, filtra o municipio, monta o JSON esperado pelo template e compila o PDF.

## Comparacao com o estado

Campos podem trazer, na mesma celula, o valor do municipio e o valor do estado separados por `|`.
Quando isso acontecer, o segundo trecho sera renderizado em verde com o rotulo `ESTADO`.

Exemplo de valor no CSV:

```text
12,3% em 2025 | Estado: 18,7% em 2025
```

Resultado esperado no PDF:

```text
12,3% em 2025 - ESTADO: 18,7% em 2025
```

Para quebrar o valor do estado em uma nova linha, use no `sections.json`:

```json
{
  "type": "field",
  "label": "",
  "column": "nome_da_coluna",
  "value_bold": true,
  "estado_newline": true,
  "estado_separator": "",
  "indent": true
}
```

Para incluir novos campos no PDF:

1. Adicione a coluna no CSV/XLSX.
2. Adicione uma entrada em `template/assets/data/sections.json` apontando para essa coluna.
3. Rode novamente o comando de geracao.
