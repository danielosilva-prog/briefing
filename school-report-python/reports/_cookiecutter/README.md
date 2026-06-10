# SEGAPE School Reports - Cookiecutter Template

Template cookiecutter para criar novos relatórios padronizados no sistema `school-report-python`.

## Visão Geral

Este cookiecutter cria uma estrutura completa e padronizada para novos relatórios, incluindo:

- ✅ **Componentes compartilhados** - Header, Footer, Capa, Sumário, Cards, Totalizers
- ✅ **Template Typst** - Entry point configurado com imports de componentes
- ✅ **Executor Python** - Lógica de geração com suporte a gráficos
- ✅ **Geradores de gráficos** - Bar, Line, Gauge (se habilitado)
- ✅ **Schema de validação** - JSON Schema para entrada de dados
- ✅ **Hooks** - Validação e setup automático pós-geração
- ✅ **Documentação** - README completo gerado automaticamente

## Pré-requisitos

```bash
pip install cookiecutter
```

## Uso Básico

### 1. Criar novo relatório

No diretório `school-report-python/reports/`:

```bash
cookiecutter _cookiecutter/
```

### 2. Responder às perguntas

O cookiecutter irá perguntar:

```
report_id [ATS-XX]: ATS-03
report_name [Nome do Relatório]: Relatório de Infraestrutura
report_description [Descrição do relatório]: Dados de infraestrutura das instituições
report_version [1.0.0]: 1.0.0
maintainer [SEGAPE]: SEGAPE
Select has_queries:
1 - yes
2 - no
Choose from 1, 2 [1]: 1
Select has_charts:
1 - yes
2 - no
Choose from 1, 2 [1]: 1
Select cache_enabled:
1 - no
2 - yes
Choose from 1, 2 [1]: 2
cache_ttl_days [30]: 30
```

### 3. Estrutura criada

```
reports/ATS-03/
├── README.md                 # Documentação completa
├── report.yaml               # Configuração
├── executor.py               # Lógica Python
├── charts/                   # Geradores de gráficos
│   ├── __init__.py
│   ├── bar_chart.py
│   ├── line_chart.py
│   └── gauge.py
├── data/
│   ├── schema.json           # Validação
│   └── test_data.json        # Dados de teste
├── queries/                  # Queries SQL (se has_queries=yes)
│   └── main_query.sql
└── template/
    ├── main.typ              # Entry point
    ├── pages/
    │   └── page01.typ        # Exemplo de página
    ├── components/           # (vazio - usa _shared)
    └── assets/               # Assets específicos
```

## Componentes Compartilhados

### Disponíveis em `reports/_shared/components/`

| Componente | Descrição | Uso |
|------------|-----------|-----|
| `style.typ` | Cores, fontes, helpers | `#import "../../_shared/components/style.typ": *` |
| `header.typ` | Cabeçalho padrão | `#import "../../_shared/components/header.typ": Header` |
| `footer.typ` | Rodapé com numeração | `#import "../../_shared/components/footer.typ": Footer` |
| `capa.typ` | Capa institucional | `#import "../../_shared/components/capa.typ": Capa` |
| `sumario.typ` | Sumário/índice | `#import "../../_shared/components/sumario.typ": Sumario` |
| `cards.typ` | Cards e containers | `#import "../../_shared/components/cards.typ": Card, CardBoxed` |
| `totalizers.typ` | Totalizadores | `#import "../../_shared/components/totalizers.typ": Totalizer, TotalizerBig` |
| `page-setup.typ` | Config de páginas | `#import "../../_shared/components/page-setup.typ": *` |

### Exemplo de uso no template

```typst
// Importar componentes compartilhados
#import "../../_shared/components/style.typ": *
#import "../../_shared/components/header.typ": Header
#import "../../_shared/components/footer.typ": Footer
#import "../../_shared/components/capa.typ": Capa
#import "../../_shared/components/totalizers.typ": Totalizer, TotalizerGrid

// Usar componentes
#Capa(
  universidade: metadata.universidade,
  sigla: metadata.sigla,
  titulo-relatorio: "Meu Relatório",
  ano: "2024"
)

#TotalizerGrid(
  columns: 3,
  totalizers: (
    Totalizer(value: "1.234", description: "Total de Alunos"),
    Totalizer(value: "45", description: "Cursos"),
    Totalizer(value: "567", description: "Docentes"),
  )
)
```

## Customização

### Cores personalizadas

Adicione cores específicas do relatório em `template/main.typ`:

```typst
// Cores personalizadas do relatório
#let myCustomBlue = rgb("0066CC")
#let myCustomRed = rgb("CC0000")

// Sobrescrever cor padrão
#let mecAzul = myCustomBlue
```

### Componentes customizados

Se precisar de um componente específico:

1. Crie em `template/components/my_component.typ`
2. Importe no `main.typ`
3. Use normalmente

```typst
#import "components/my_component.typ": MyComponent
#MyComponent(data: ...)
```

### Páginas customizadas

Adicione páginas em `template/pages/`:

```typst
// template/pages/page_custom.typ
#import "../../../_shared/components/style.typ": *

#let PageCustom(data) = [
  = Minha Página Customizada

  // Conteúdo aqui
]
```

E importe no `main.typ`:

```typst
#import "pages/page_custom.typ": PageCustom
// ...
#PageCustom(data: queries)
```

## Gráficos

### Geradores incluídos (se has_charts=yes)

| Tipo | Arquivo | Descrição |
|------|---------|-----------|
| Barras | `charts/bar_chart.py` | Gráficos de barras verticais |
| Linhas | `charts/line_chart.py` | Gráficos de linha/série temporal |
| Gauge | `charts/gauge.py` | Gauges semicirculares (% de progresso) |

### Adicionar novo tipo de gráfico

1. Criar `charts/novo_grafico.py`:

```python
import base64
import io
import matplotlib.pyplot as plt

def generate_novo_grafico(data: dict) -> str:
    """Gera novo tipo de gráfico."""
    # Implementação
    fig, ax = plt.subplots()
    # ...
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150)
    plt.close()
    return base64.b64encode(buffer.getvalue()).decode()
```

2. Exportar em `charts/__init__.py`:

```python
from .novo_grafico import generate_novo_grafico

__all__ = [
    # ...
    "generate_novo_grafico",
]
```

3. Usar em `executor.py`:

```python
from .charts import generate_novo_grafico

# ...
charts["meu_grafico"] = generate_novo_grafico(data)
```

4. Referenciar no template:

```typst
#figure(
  decode-chart("meu_grafico"),
  caption: [Meu gráfico customizado]
)
```

## Queries BigQuery

### Se has_queries=yes

1. Adicione arquivos `.sql` em `queries/`:

```sql
-- queries/alunos_por_curso.sql
SELECT
  curso,
  COUNT(*) as total_alunos
FROM `projeto.dataset.tabela`
WHERE ano = @ano_base
  AND instituicao_id = @instituicao_id
GROUP BY curso
ORDER BY total_alunos DESC
```

2. Registre em `report.yaml`:

```yaml
queries:
  - name: alunos_por_curso
    description: "Contagem de alunos por curso"
    file: queries/alunos_por_curso.sql
    required: true
```

3. Use no template:

```typst
#let alunos = queries.at("alunos_por_curso", default: ())
```

## Validação de Entrada

### Schema JSON (`data/schema.json`)

Defina estrutura esperada dos dados:

```json
{
  "properties": {
    "metadata": {
      "required": ["instituicao", "sigla"]
    },
    "params": {
      "required": ["instituicao_id", "ano_base"]
    }
  }
}
```

A validação acontece automaticamente no `executor.py`.

## Testes

### Dados de teste

Edite `data/test_data.json` com dados realistas:

```json
{
  "metadata": {
    "instituicao": "UFAL",
    "sigla": "UFAL"
  },
  "params": {
    "instituicao_id": "UFAL",
    "ano_base": 2024
  },
  "queries": {
    "alunos_por_curso": [
      {"curso": "Engenharia", "total": 1234},
      {"curso": "Medicina", "total": 987}
    ]
  }
}
```

### Teste local

```python
import asyncio
import json
from pathlib import Path

async def test():
    from reports.ATS_03.executor import ATS03Executor

    reports_dir = Path("school-report-python/reports")
    executor = ATS03Executor(reports_dir)

    with open("reports/ATS-03/data/test_data.json") as f:
        data = json.load(f)

    pdf = await executor.execute(data)

    with open("test_output.pdf", "wb") as f:
        f.write(pdf)

    print("✓ PDF gerado: test_output.pdf")

asyncio.run(test())
```

## Hooks do Cookiecutter

### Pre-generation (`hooks/pre_gen_project.py`)

- Valida formato do `report_id`
- Verifica inputs obrigatórios

### Post-generation (`hooks/post_gen_project.py`)

- Remove arquivos não necessários
- Cria `README.md` customizado
- Cria `test_data.json` inicial
- Exibe próximos passos

## Arquitetura

### Fluxo de dados

```
BigQuery → Queries → [transform] → Charts → Typst Template → PDF
```

### Componentes

1. **Executor** (`executor.py`)
   - Orquestra geração
   - Valida entrada
   - Chama geradores de gráficos
   - Compila Typst
   - **Use primitivas de `schoolreport.core`** para evitar boilerplate (veja abaixo)

2. **Chart Generators** (`charts.py`)
   - Decorador `@chart` para registrar funções
   - matplotlib + `ChartContext` com estilos padrão
   - Auto-descoberta pelo pipeline

3. **Template** (`template/main.typ`)
   - Recebe JSON via `sys.inputs`
   - Decodifica gráficos
   - Renderiza páginas
   - Gera PDF

4. **Componentes Compartilhados** (`_shared/components/`)
   - Reutilizáveis entre relatórios
   - Consistência visual
   - Manutenção centralizada

### Primitivas Reutilizáveis (`schoolreport.core`)

O executor gerado pelo cookiecutter já importa estas primitivas. Use-as para evitar reimplementar lógica comum:

| Módulo | Funções | Uso |
|--------|---------|-----|
| `core.formatting` | `fmt_brl()`, `fmt_pct()` | Formatar moeda BRL e percentuais pt-BR |
| `core.chart_assets` | `write_charts_to_assets()`, `ensure_placeholder_charts()` | Persistir SVGs e criar placeholders |
| `core.bigquery` | `BigQueryClient.execute_query_as_dicts()` | Query BQ retornando `List[Dict]` |
| `core.typst` | `TypstClient.render_to_bytes()` | Render PDF direto para bytes (sem arquivo intermediário) |

Veja [DEVELOPER_GUIDE.md](../../DEVELOPER_GUIDE.md#reusable-primitives-for-custom-executors) para exemplos completos.

## Melhores Práticas

### ✅ DO

- Usar componentes compartilhados sempre que possível
- Seguir padrão de nomenclatura (report_id em UPPER-CASE)
- Documentar parâmetros customizados
- Criar dados de teste realistas
- Validar entrada com JSON Schema

### ❌ DON'T

- Duplicar código de componentes compartilhados
- Hardcodar dados no template
- Ignorar validação de entrada
- Comprometer assets binários desnecessários
- Esquecer de atualizar README.md

## Troubleshooting

### Erro: "Report ID is invalid"

- Use apenas letras maiúsculas, números e hífens
- Exemplo válido: `ATS-03`, `ATM`, `ATSBR`

### Erro: "Module not found: charts"

- Verifique se `has_charts=yes` no cookiecutter
- Ou remova imports de charts em `executor.py`

### Erro na compilação Typst

- Verifique paths dos imports (use `../../_shared/...`)
- Confirme que todos os assets existem

### Gráficos não aparecem

- Verifique se charts estão em `data["charts"]`
- Confirme que `decode-chart()` está sendo chamado
- Teste geradores standalone primeiro

## Contribuindo

### Adicionar novo componente compartilhado

1. Criar em `reports/_shared/components/novo.typ`
2. Documentar parâmetros
3. Adicionar exemplo no README
4. Testar em múltiplos relatórios

### Melhorar template cookiecutter

1. Editar arquivos em `_cookiecutter/{{cookiecutter.report_id}}/`
2. Testar geração com `cookiecutter .`
3. Atualizar hooks se necessário
4. Documentar mudanças

## Exemplos Reais

### Relatórios existentes usando este padrão

- `ATS-02` - Relatório Orçamentário (referência completa)
- Veja `reports/ATS-02/` para exemplo de implementação

## Recursos

- [Documentação Typst](https://typst.app/docs/)
- [Cookiecutter Docs](https://cookiecutter.readthedocs.io/)
- [matplotlib Gallery](https://matplotlib.org/stable/gallery/)
- [JSON Schema](https://json-schema.org/)

## Suporte

Para dúvidas ou problemas:

1. Consultar `reports/ATS-02/` como referência
2. Ler README do relatório gerado
3. Verificar logs do executor
4. Contatar time SEGAPE

---

*Criado por SEGAPE - 2026*
