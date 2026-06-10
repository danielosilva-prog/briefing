# BRIEFING-LOCAL-2

Relatorio de briefing local por UF, sem BigQuery, baseado no modelo Word `20260512 Briefing-MG.docx`.

## Uso

```bash
$env:PYTHONUTF8='1'
uv run schoolreport generate BRIEFING-LOCAL-2 uf=MG input_file=reports/BRIEFING-LOCAL-2/data/MG.csv --output output/briefing-local-2-mg.pdf
```

## Estrutura

- `data/MG.csv`: exemplo de entrada no novo formato.
- `template/assets/data/sections.json`: contrato das secoes, linhas, textos nacionais e colunas do CSV.
- `template/assets/header.png`: cabecalho extraido do Word.
- `template/assets/footer.png`: rodape extraido do Word.
- `executor.py`: le CSV/XLSX, filtra a UF e monta o JSON consumido pelo Typst.

Para incluir novas UFs, mantenha uma linha por UF e preserve a coluna `uf`.
