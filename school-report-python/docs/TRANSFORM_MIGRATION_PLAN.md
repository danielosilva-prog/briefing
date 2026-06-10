# Plano de Migração: `transform.py`

> Gancho leve entre queries e render — eliminando a necessidade de `executor.py` para a maioria dos relatórios.

## Contexto

### O problema atual

O pipeline declarativo do `school-report-python` é **tudo ou nada**:

| Cenário | O que o dev escreve | Linhas |
|---------|---------------------|--------|
| Relatório simples (só queries + template) | `report.yaml` | 0 Python |
| Precisa de UM cálculo extra | `executor.py` completo | 160–700 linhas |

Não existe meio-termo. Quando o relatório precisa de uma coisa a mais — computar uma métrica, formatar um valor, agregar dados — o desenvolvedor é forçado a criar um `executor.py` que reimplementa toda a orquestração: validação, client BigQuery, chart generation, Typst rendering.

### O que já fizemos (Priority 1)

Extraímos primitivas reutilizáveis em `schoolreport.core`:

- `core.formatting` — `fmt_brl()`, `fmt_pct()`
- `core.chart_assets` — `write_charts_to_assets()`, `ensure_placeholder_charts()`
- `core.bigquery` — `BigQueryClient.execute_query_as_dicts()`, `ArrayQueryParameter`
- `core.typst` — `TypstClient.render_to_bytes()`

Isso reduziu executores existentes em ~50%, mas o problema estrutural permanece: qualquer customização ainda requer um executor completo.

### A solução: `transform.py`

Um arquivo Python opcional por relatório com uma única função `transform()` que se injeta no pipeline declarativo:

```
Queries (BigQuery) ─→ transform() ─→ Charts (charts.py) ─→ Render (Typst) ─→ PDF
                       ↑ NOVO
```

---

## Design

### Contrato da função

```python
# reports/MEU-REPORT/transform.py

from schoolreport.transforms import TransformContext

async def transform(ctx: TransformContext) -> None:
    """Transforma dados entre queries e render.

    Modifica ctx.queries e ctx.template_params in-place.
    """
    df = ctx.queries["metricas"]
    total = df["valor"].sum()
    ctx.template_params["totalOrcamento"] = ctx.fmt_brl(total)
```

### `TransformContext`

```python
@dataclass
class TransformContext:
    # ── Mutáveis (modifique in-place) ──────────────────
    queries: Dict[str, pd.DataFrame]      # resultados das queries BQ
    template_params: Dict[str, str]        # params extras para o template Typst

    # ── Somente leitura ────────────────────────────────
    params: Dict[str, Any]                 # parâmetros do relatório (cod_ibge, etc.)
    report_id: str                         # ID do relatório
    report_dir: Path                       # diretório do relatório

    # ── Utilitários ────────────────────────────────────
    fmt_brl: Callable[[float], str]        # formatação BRL (R$ X,XX mi/bi)
    fmt_pct: Callable[[float], str]        # formatação percentual (X,XX%)
```

**Princípios de design:**

1. **In-place mutation** — sem retorno obrigatório. Mais natural que transformações puras.
2. **Utilitários embutidos** — o dev não precisa importar `fmt_brl`/`fmt_pct` manualmente.
3. **Async** — permite consultas adicionais ou I/O dentro do transform, se necessário.
4. **Sem dependência do pipeline** — o transform não sabe sobre Typst, charts, ou BQ. Só vê dados.

### Hierarquia de descoberta

Quando o CLI gera um relatório, a ordem de prioridade é:

```
1. executor.py existe?  → Usa executor customizado (comportamento atual, inalterado)
2. transform.py existe? → Usa pipeline declarativo + transform hook
3. Nenhum?              → Usa pipeline declarativo puro (comportamento atual, inalterado)
```

O `executor.py` sempre tem precedência. Isso garante backwards compatibility total.

---

## Ponto de injeção no pipeline

### `LocalExecutor.execute()` (CLI)

```python
# Antes:
data, charts = await self._execute_pipeline(report, params, progress)
output_path = await self._render_pdf(report, data, charts, output)

# Depois:
data, charts = await self._execute_pipeline(report, params, progress)
data, template_params = await self._apply_transform(report, data, params)
output_path = await self._render_pdf(report, data, charts, output, template_params)
```

### `LocalExecutor.execute_with_data()` (JSON input)

```python
# Antes:
charts = await self._generate_charts(report, query_results, params)
output_path = await self._render_pdf(report, query_results, charts, output)

# Depois:
query_results, template_params = await self._apply_transform(report, query_results, params)
charts = await self._generate_charts(report, query_results, params)
output_path = await self._render_pdf(report, query_results, charts, output, template_params)
```

**Nota importante:** o transform roda ANTES dos charts. Isso permite que o transform modifique DataFrames que os charts vão consumir (e.g. adicionar coluna derivada, filtrar linhas).

### `_render_pdf()` — propagação de `template_params`

O `_render_pdf()` precisa ser atualizado para incorporar `template_params` no `template_data` enviado ao Typst:

```python
template_data = {
    "queries": { ... },
    "charts": charts,
    "params": params,
    "template_params": template_params,  # NOVO
}
```

---

## Arquivos a criar/modificar

### Novos

| Arquivo | Descrição |
|---------|-----------|
| `src/schoolreport/transforms.py` | `TransformContext`, `discover_transform()`, `apply_transform()` |
| `reports/_cookiecutter/{{cookiecutter.report_id}}/transform.py` | Template com exemplo comentado |

### Modificados

| Arquivo | Mudança |
|---------|---------|
| `src/schoolreport/cli/executor.py` | Adicionar `_apply_transform()`, chamar em `execute()` e `execute_with_data()` |
| `src/schoolreport/cli/commands/generate.py` | Quando transform.py existe sem executor.py, usar pipeline declarativo (não precisa de executor customizado) |

### Testes

| Arquivo | Descrição |
|---------|-----------|
| `tests/test_core/test_transforms.py` | Testes unitários para TransformContext e discover |
| `tests/test_cli/test_executor_transform.py` | Testes de integração do transform no pipeline |

---

## Impacto em relatórios existentes

### ATM-EQ — Candidato a migração

O `ATM-EQ/executor.py` (166 linhas) faz essencialmente:
1. Converter queries para DataFrames → **já feito pelo pipeline declarativo**
2. Gerar charts via `ChartLoader` + `generate_many()` → **já feito por `charts.py`**
3. Compilar Typst → **já feito pelo pipeline**

Com `transform.py`, o ATM-EQ provavelmente não precisa de nenhum código Python customizado. O `charts.py` + `report.yaml` já cobrem tudo.

**Migração:** deletar `executor.py`, verificar que `charts.py` + pipeline declarativo gera o mesmo PDF.

### ATS-02 / ATS-ORC-R — Mantêm executor

Esses relatórios têm lógica complexa que vai além do transform:
- Resolução de institution filter (sigla → id_uo via BQ)
- Queries dinâmicas com parâmetros derivados
- Shared Y-axis limits entre pares de charts
- BigQuery paralelo com semáforo e cache

O `transform.py` não elimina esses executores, mas reduz o incentivo de criar novos para casos similares.

### Relatórios futuros

Um relatório novo que precisar de:

| Necessidade | Solução |
|-------------|---------|
| Queries + template | `report.yaml` (0 Python) |
| Charts custom | + `charts.py` |
| Métricas computadas | + `transform.py` (~15-30 linhas) |
| Shared ylims, formatação | + `transform.py` (~30-50 linhas) |
| BQ paralelo customizado, institution filter | `executor.py` (usar primitivas de `core`) |

---

## Cronograma sugerido

### Fase 1: Core (estimativa: 1 sessão)
1. Criar `src/schoolreport/transforms.py` com TransformContext e discover
2. Integrar no `LocalExecutor` (execute + execute_with_data)
3. Atualizar `generate.py` para hierarquia executor > transform > declarativo
4. Testes unitários e de integração

### Fase 2: Template e docs (estimativa: 1 sessão)
1. Criar template cookiecutter para transform.py
2. Atualizar documentação (DEVELOPER_GUIDE, reports/README)
3. Exemplo funcional com relatório sample

### Fase 3: Migração ATM-EQ (estimativa: 1 sessão)
1. Verificar que ATM-EQ funciona sem executor.py (só charts.py)
2. Se precisar de transform, criar transform.py minimal
3. Deletar executor.py
4. Testes de regressão (comparar PDF gerado)

---

## Riscos e mitigações

| Risco | Mitigação |
|-------|-----------|
| Transform modifica dados que charts.py espera em formato original | Transform roda antes de charts — documentar que charts veem dados transformados |
| Transform async pode fazer I/O inesperado (queries extras, HTTP) | Documentar que transform é para transformação de dados, não orchestração |
| Confusão sobre quando usar transform vs executor | Tabela clara de decisão na documentação |
| `_execute_pipeline` entrelaça queries e charts em paralelo | Transform injeta DEPOIS das queries, ANTES do render. Charts que dependem de dados transformados precisam rodar sequencialmente após o transform |

---

## Decisões de design pendentes

1. **Transform síncrono vs async?**
   - Proposta: async (mais flexível, permite I/O futuro)
   - Alternativa: sync (mais simples, força transform puro)

2. **Múltiplos hooks vs função única?**
   - Proposta: função única `transform()` (KISS)
   - Alternativa: `pre_charts()` + `post_charts()` + `pre_render()`

3. **Template params como dict separado vs merge em queries?**
   - Proposta: `ctx.template_params` separado (clareza sobre o que vai para o template)
   - Alternativa: tudo em `ctx.queries` (simples mas perde semântica)
