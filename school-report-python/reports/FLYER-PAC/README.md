# FLYER-PAC

Relatorio local para gerar a pagina de apoio ao flyer da ACS, com resumo do Novo PAC e programas do MEC por UF.

## Uso

```powershell
$env:PYTHONUTF8='1'
uv run schoolreport generate FLYER-PAC uf=RJ input_file=reports/FLYER-PAC/data/flyer_estados.csv --output output/flyer-pac-rj.pdf
```

## Entrada

O arquivo de entrada deve ter uma linha por UF e uma coluna `uf`.

O CSV completo de exemplo esta em:

```text
reports/FLYER-PAC/data/flyer_estados_completo.csv
```

Para manter compatibilidade, o CSV inicial tambem permanece em `data/flyer_estados.csv`.

A lista de obras deve estar preferencialmente na coluna:

- `obras_expansao_lista`

O executor tambem aceita os nomes antigos abaixo:

- `obras_lista`
- `lista_obras`
- `obras`

Formato esperado da lista completa:

```text
acao§tipo_sigla§municipio§obra-x-acao§tipo_sigla§municipio§obra
```

Primeiro o texto e separado por `-x-` para obter cada obra. Depois cada obra e separada por `§` para obter os campos da tabela.
