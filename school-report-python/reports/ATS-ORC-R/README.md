# ATS-02: Relatório Orçamentário - Aqui Tem Superior

## Visão Geral

O **ATS-02** é um relatório de execução orçamentária de Instituições de Ensino Superior (IES) federais, com foco em dados financeiros como:

- Orçamento Aprovado (LOA, Dotação, Despesas)
- Execução Orçamentária (Empenho, Liquidação)
- Restos a Pagar
- Ações específicas (4002, 4572, 20KG, 20RK, 4086, 8282)
- Novo PAC

## Características Técnicas

| Aspecto | Valor |
|---------|-------|
| **Fonte de dados** | JSON (via API/CLI) |
| **Queries BigQuery** | 0 (futuro) |
| **Parâmetros** | sigla (obrigatório) |
| **Páginas** | 32 páginas Typst |
| **Componentes** | 6 componentes |
| **Tipos de gráficos** | 5 tipos (gauge, horizontal_bar, stacked_bar, grouped_bar, area_line) |
| **Cache** | Desabilitado (dados dinâmicos) |

## Estrutura do Diretório

```
ATS-02/
├── README.md              # Este arquivo
├── report.yaml            # Configuração do relatório
├── executor.py            # Executor Python customizado
├── charts/                # Módulos de geração de gráficos
│   ├── __init__.py
│   ├── gauge.py           # Gauge semicircular (SVG)
│   ├── horizontal_bar.py  # Barras horizontais (matplotlib)
│   ├── stacked_bar.py     # Barras empilhadas (matplotlib)
│   └── grouped_bar.py     # Barras agrupadas (matplotlib)
├── data/
│   ├── schema.json        # Schema de validação JSON
│   └── test_data.json     # Dados de teste
└── template/
    ├── main.typ           # Entry point Typst
    ├── components/        # Componentes reutilizáveis
    │   ├── card.typ
    │   ├── footer.typ
    │   ├── header.typ
    │   ├── style.typ
    │   ├── totalizer.typ
    │   └── totalizerWithImage.typ
    ├── pages/             # 32 páginas do relatório
    │   ├── P01-OrcamentoAprovado-VisaoGeral.typ
    │   ├── P02-OrcamentoAprovado-DespesasObrigatorias.typ
    │   └── ... (P03-P32)
    └── assets/            # Assets estáticos
        ├── background/    # SVGs de fundo
        ├── icons/         # Ícones
        ├── logos/         # Logos das universidades
        └── data/          # Dados JSON estáticos
```

## Tipos de Gráficos

### 1. Gauge (Semicircular)

Indica porcentagens de execução orçamentária.

**Módulo**: `charts/gauge.py`

**Uso**:
```python
from charts.gauge import generate_gauge

svg_base64 = generate_gauge(
    value=58.1,      # Valor atual
    max_value=100,   # Valor máximo
    color="#0095DA", # Cor do arco
)
```

**Exemplos**: P6-G1, P7-G1, P8-G1, P8-G2, P10-G2

### 2. Horizontal Bar (Barras Horizontais)

Compara LOA vs Dotação Atualizada por ano.

**Módulo**: `charts/horizontal_bar.py`

**Uso**:
```python
from charts.horizontal_bar import generate_horizontal_bar

png_base64 = generate_horizontal_bar(
    labels=["2020", "2021", "2022"],
    values1=[100, 110, 120],  # LOA
    values2=[95, 105, 118],   # Dotação
)
```

**Exemplos**: P1-G1, P9-G1, P12-G1

### 3. Stacked Bar (Barras Empilhadas)

Mostra composição por tipo de orçamento.

**Módulo**: `charts/stacked_bar.py`

**Uso**:
```python
from charts.stacked_bar import generate_stacked_bar

png_base64 = generate_stacked_bar(
    labels=["2020", "2021", "2022"],
    series={
        "Obrigatório": [60, 65, 70],
        "Discricionário": [25, 28, 30],
        "Emendas": [10, 12, 15],
    }
)
```

**Exemplos**: P1-G2, P9-G2, P12-G2

### 4. Grouped Bar (Barras Agrupadas)

Comparação lado a lado (ex: Empenhado vs Liquidado).

**Módulo**: `charts/grouped_bar.py`

**Uso**:
```python
from charts.grouped_bar import generate_grouped_bar

png_base64 = generate_grouped_bar(
    labels=["Custeio", "Capital", "Pessoal"],
    series={
        "Empenhado": [50, 30, 80],
        "Liquidado": [45, 25, 78],
    }
)
```

**Exemplos**: P1-G3, P9-G3, P12-G3

### 5. Area + Line (Área + Linha)

Série temporal com área (orçamento total) e linha (despesa empenhada).

**Módulo**: `charts/area_line.py`

**Uso**:
```python
from charts.area_line import generate_area_line

png_base64 = generate_area_line(
    labels=["2020", "2021", "2022", "2023", "2024"],
    area_values=[100, 120, 130, 140, 150],      # Orçamento Total
    line_values=[90, 108, 121, 129, 143],       # Despesa Empenhada
)
```

**Exemplos**: P5-G1, P10-G1, P13-G1

## Uso

### Via Executor Standalone

```python
import asyncio
import json
from pathlib import Path
from reports.ATS02.executor import generate_ats02_report

# Carregar dados de teste
with open("reports/ATS-02/data/test_data.json") as f:
    data = json.load(f)

# Gerar relatório
pdf_bytes = asyncio.run(generate_ats02_report(data))

# Salvar PDF
with open("ats02_ufal.pdf", "wb") as f:
    f.write(pdf_bytes)
```

### Via CLI (quando integrado)

```bash
# Gerar relatório ATS-02
schoolreport generate ATS-02 sigla=UFAL --data data/test_data.json

# Com output específico
schoolreport generate ATS-02 sigla=UFAL --output ats02_ufal.pdf
```

### Via API (quando integrado)

```bash
curl -X POST http://localhost:8000/reports/ATS-02/generate \
  -H "Content-Type: application/json" \
  -d @reports/ATS-02/data/test_data.json
```

## Estrutura dos Dados de Entrada

### Formato JSON

```json
{
  "metadata": {
    "sigla": "UFAL",
    "universidade": "Universidade Federal de Alagoas",
    "generated_at": "2026-02-04T10:30:00Z",
    "system_version": "1.0.0"
  },
  "params": {
    "sigla": "UFAL",
    "ano_base": 2024
  },
  "queries": {},
  "budget_data": {
    "p1": {
      "anos": ["2020", "2021", "2022", "2023", "2024"],
      "loa": [850.5, 920.3, 985.7, 1020.4, 1105.2],
      "dotacao": [845.2, 915.8, 980.1, 1015.3, 1098.6],
      "tipo_orcamento": {
        "obrigatorio": [620.5, 665.3, 710.2, 735.8, 785.4],
        "discricionario": [180.2, 195.5, 210.8, 220.1, 245.3],
        "emendas": [44.5, 55.0, 59.1, 59.4, 67.9]
      }
    },
    "p6": {
      "percent_geral": 89.5,
      "percent_obrigatorio": 95.2,
      "percent_discricionario": 78.3,
      "percent_emendas": 62.1
    }
  }
}
```

Veja `data/schema.json` para o schema completo.

## Desenvolvimento

### Adicionar Novos Gráficos

1. Adicione dados em `budget_data` no JSON de entrada
2. Implemente geração em `executor.py` no método `_generate_charts()`
3. Adicione a chave do gráfico ao mapeamento (ex: `p7_g1`)
4. Atualize a página Typst para usar `get_chart("p7_g1")`

### Testar Geração de Gráficos

```bash
cd reports/ATS-02/charts

# Testar gauge
python gauge.py

# Testar barras horizontais
python horizontal_bar.py

# Testar barras empilhadas
python stacked_bar.py

# Testar barras agrupadas
python grouped_bar.py
```

Cada módulo gera um arquivo de exemplo (`.svg` ou `.png`) para inspeção visual.

### Validar Dados

```bash
# Validar JSON contra schema
schoolreport reports validate ATS-02 --data data/test_data.json
```

## Integração Futura com BigQuery

Quando os dados estiverem disponíveis no BigQuery:

1. Criar queries SQL em `queries/`
2. Atualizar `report.yaml` com definições de queries
3. Adaptar `executor.py` para processar resultados de queries
4. O módulo de gráficos permanece inalterado

## Roadmap

- [x] Estrutura de diretórios
- [x] Configuração `report.yaml`
- [x] Assets estáticos (backgrounds, icons, logos)
- [x] Componentes Typst
- [x] Páginas Typst (32 arquivos)
- [x] Módulo `gauge.py`
- [x] Módulo `horizontal_bar.py`
- [x] Módulo `stacked_bar.py`
- [x] Módulo `grouped_bar.py`
- [x] Entry point `main.typ`
- [x] Schema de validação
- [x] Executor Python
- [x] Dados de teste
- [ ] Adaptar todas as 32 páginas para gráficos dinâmicos
- [ ] Implementar geração de todos os gráficos (40+ gráficos)
- [ ] Integração com BigQuery
- [ ] Testes unitários para charts
- [ ] Testes de integração end-to-end
- [ ] Deploy em staging
- [ ] Deploy em produção

## Referências

- [Plano de Migração ATS-02](../../../docs/MIGRATION_PLAN_ATS02.md)
- [Typst Documentation](https://typst.app/docs)
- [Matplotlib Documentation](https://matplotlib.org/stable/contents.html)

## Autor

Migrado para Python por Claude Code em 2026-02-04
