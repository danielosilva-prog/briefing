# ANEXOS-BRIEFINGS

Relatório local para gerar os anexos de obras da SETEC e da SESU por UF, a partir de CSV.

## Arquivo de entrada

Coloque o arquivo com os dados em:

```text
reports/ANEXOS-BRIEFINGS/data/Anexos-briefing.csv
```

Colunas esperadas:

- `secretaria`
- `sigla_uf`
- `instituicao`
- `descricao_empreendimento`
- `municipio`
- `valor_previsto`

## Gerar os dois anexos por UF

No PowerShell, a partir da raiz do projeto:

```powershell
.\reports\ANEXOS-BRIEFINGS\gera_anexos_briefing.bat RJ
```

O comando gera:

```text
output/anexo-setec-rj.pdf
output/anexo-sesu-rj.pdf
```

## Gerar apenas um anexo pelo CLI

```powershell
$env:PYTHONUTF8='1'
uv run schoolreport generate ANEXOS-BRIEFINGS uf=RJ secretaria=SETEC input_file=reports/ANEXOS-BRIEFINGS/data/Anexos-briefing.csv --output output/anexo-setec-rj.pdf
uv run schoolreport generate ANEXOS-BRIEFINGS uf=RJ secretaria=SESU input_file=reports/ANEXOS-BRIEFINGS/data/Anexos-briefing.csv --output output/anexo-sesu-rj.pdf
```

Troque `RJ` pela UF desejada.
