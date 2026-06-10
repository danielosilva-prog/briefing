# ATM-EQ Report Batch

Fluxo para planejamento e execucao em lote do relatorio `ATM-EQ` (PDF por municipio).

## Script

- `reports/ATM-EQ/scripts/report_batch/run_atm_eq_batch.py`

## Saida padrao

As saidas deste fluxo ficam em:

- `reports/ATM-EQ/scripts/report_batch/output/atm_eq_batch_regioes/`
- `reports/ATM-EQ/scripts/report_batch/output/atm_eq_batch_regioes/_logs/`

Os PDFs sao gerados sem timestamp no nome do arquivo. Com `SKIP_EXISTING=True`, uma nova rodada pula PDFs que ja existem no destino.

## Divisao do export

O lote esta configurado para dividir a geracao entre 3 pessoas por perfil:

- `pessoa_1`: Norte, Sul e Centro-Oeste
- `pessoa_2`: Sudeste
- `pessoa_3`: Nordeste

Antes de executar, cada pessoa deve alterar somente `EXPORT_SPLIT_PROFILE` no topo de `run_atm_eq_batch.py`.

Exemplo:

```python
EXPORT_SPLIT_PROFILE = "pessoa_2"
```

Como `FOLDER_GROUPING="regiao"`, os arquivos ficam separados por pasta de regiao dentro de `atm_eq_batch_regioes`.

## Uso

Edite a configuracao no topo de `run_atm_eq_batch.py`:

- `EXECUTE` (`False` = dry-run, `True` = gera PDF)
- `PARALLEL` / `WORKERS`
- `EXPORT_SPLIT_PROFILE`
- filtros (`FILTER_UFS`, `FILTER_REGIOES`, `FILTER_COD_IBGE`, `MAX_MUNICIPIOS`)
- `SKIP_EXISTING`
- `FOLDER_GROUPING`

Execucao:

```powershell
cd .\school-report-python
uv run python .\reports\ATM-EQ\scripts\report_batch\run_atm_eq_batch.py
```

## Exemplos de configuracao

### Gerar todo o Brasil separado por regiao

```python
EXECUTE = True
FOLDER_GROUPING = "regiao"
FILTER_UFS = None
FILTER_REGIOES = None
FILTER_COD_IBGE = None
MAX_MUNICIPIOS = None
```

### Gerar municipios especificos por codigo IBGE

```python
EXECUTE = True
FILTER_UFS = None
FILTER_REGIOES = None
FILTER_COD_IBGE = ["5300108", "3550308", "3304557"]
MAX_MUNICIPIOS = None
```

### Gerar uma unica UF

```python
EXECUTE = True
FILTER_UFS = ["DF"]
FILTER_REGIOES = None
FILTER_COD_IBGE = None
MAX_MUNICIPIOS = None
```

### Gerar varias UFs

```python
EXECUTE = True
FILTER_UFS = ["DF", "GO", "TO"]
FILTER_REGIOES = None
FILTER_COD_IBGE = None
MAX_MUNICIPIOS = None
```

### Gerar uma regiao

```python
EXECUTE = True
FILTER_UFS = None
FILTER_REGIOES = ["Centro-Oeste"]
FILTER_COD_IBGE = None
MAX_MUNICIPIOS = None
```

### Gerar varias regioes

```python
EXECUTE = True
FILTER_UFS = None
FILTER_REGIOES = ["Norte", "Sul", "Centro-Oeste"]
FILTER_COD_IBGE = None
MAX_MUNICIPIOS = None
```

### Fazer dry-run sem gerar PDFs

```python
EXECUTE = False
FILTER_UFS = None
FILTER_REGIOES = None
FILTER_COD_IBGE = None
MAX_MUNICIPIOS = None
```

### Testar com poucos municipios

```python
EXECUTE = True
FILTER_UFS = None
FILTER_REGIOES = None
FILTER_COD_IBGE = None
MAX_MUNICIPIOS = 10
```

### Separar saida por UF

```python
EXECUTE = True
FOLDER_GROUPING = "uf"
FILTER_UFS = None
FILTER_REGIOES = None
FILTER_COD_IBGE = None
MAX_MUNICIPIOS = None
```

### Colocar tudo em uma unica pasta Brasil

```python
EXECUTE = True
FOLDER_GROUPING = "brasil"
FILTER_UFS = None
FILTER_REGIOES = None
FILTER_COD_IBGE = None
MAX_MUNICIPIOS = None
```

Os filtros sao combinados. Por exemplo, se `FILTER_UFS = ["DF"]` e
`FILTER_COD_IBGE = ["3550308"]`, nenhum municipio sera selecionado, porque Sao
Paulo nao pertence ao DF. Para usar apenas um tipo de filtro, deixe os demais
como `None`.

## Logs e metricas

O runner gera:

- CSV por municipio
- JSON com resumo da execucao

No final imprime:

- tempo total (wall-clock)
- soma das duracoes individuais
- throughput aproximado
- paralelismo efetivo e eficiencia vs `WORKERS`
