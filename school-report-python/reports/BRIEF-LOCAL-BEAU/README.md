# BRIEF-LOCAL-BEAU

Versao visual do briefing local por UF, baseada no mockup de 10/06/2026.

O relatorio continua lendo o mesmo formato de CSV do `BRIEFING-LOCAL-2`.
Campos vazios sao exibidos com o placeholder `—`.

## Executar

```powershell
uv run schoolreport generate BRIEF-LOCAL-BEAU uf=MG input_file=reports/BRIEF-LOCAL-BEAU/data/revisado-geral.csv --output output/brief-local-beau-mg.pdf
```

Troque `MG` pela UF desejada.
