# BRIEFING-LOCAL

Relatorio de briefing gerado a partir de arquivo local, sem BigQuery.

## Uso

```bash
uv run schoolreport generate BRIEFING-LOCAL uf=PB input_file=reports/BRIEFING-LOCAL/data/exemplo_briefing_ufs.csv --output output/briefing-pb.pdf
```

O arquivo de entrada deve ter uma linha por UF e uma coluna `uf` com a sigla do estado.

## Estrutura

- `data/exemplo_briefing_ufs.csv`: exemplo de entrada.
- `template/assets/data/sections.json`: contrato que mapeia colunas do arquivo para secoes e indicadores do PDF.
- `template/assets/header.svg`: imagem usada no cabecalho do PDF.
- `template/assets/footer.svg`: imagem usada no rodape do PDF.
- `executor.py`: le CSV/XLSX, filtra a UF, monta o JSON esperado pelo template e compila o PDF.

Para incluir novos campos no PDF:

1. Adicione a coluna no CSV/XLSX.
2. Adicione uma entrada em `template/assets/data/sections.json` apontando para essa coluna.
3. Rode novamente o comando de geracao.

Para trocar as artes do cabecalho e rodape, substitua `template/assets/header.svg`
e `template/assets/footer.svg` mantendo os mesmos nomes de arquivo.
