@echo off
setlocal enabledelayedexpansion

set ufs=AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO

for %%u in (%ufs%) do (
    echo Gerando relatorio para: %%u...
    uv run schoolreport generate BRIEFING-LOCAL-2 uf=%%u input_file=reports/BRIEFING-LOCAL-2/data/revisado-geral.csv --output output/novo/briefing-%%u.pdf
)

echo Todos os relatorios foram gerados.
pause