# School Report Definitions

This directory contains declarative report definitions for the School Report system.

## Structure

Each report is defined in its own directory with the following structure:

```
reports/
├── atsbr/                      # Report ID (must be unique)
│   ├── report.yaml             # Report definition (required)
│   ├── queries/                # SQL query files (required)
│   │   ├── query1.sql
│   │   ├── query2.sql
│   │   └── ...
│   └── template/               # Typst template (required)
│       ├── main.typ            # Template entry point
│       ├── components/         # Reusable Typst components
│       ├── assets/             # Images, backgrounds, etc.
│       └── fonts/              # Custom fonts (optional)
│
├── ats/                        # Another report
│   └── ...
│
└── atm/                        # Another report
    └── ...
```

## Available Reports

### ATSBR - Aqui Tem Superior - Brasil ✅

**Status**: Migrated from R

**Description**: National report on Brazilian higher education, aggregating data from all federal universities.

**Parameters**: None (national report)

**Queries**: 8 BigQuery queries
- INEP education census data
- Faculty information
- Administrative staff data
- Graduate programs
- CAPES scholarships

**Complexity**: Low (no parameters)

**Usage**:
```bash
schoolreport generate ATSBR --output atsbr-brasil.pdf
```

---

### ATS - Aqui Tem Superior ⏳

**Status**: Pending migration

**Description**: Higher education report for individual institutions.

**Parameters**:
- `cod_ies` (required): Institution code

**Queries**: 7 BigQuery queries

**Complexity**: Medium

**Usage**:
```bash
schoolreport generate ATS --params '{"cod_ies": "123"}' --output ats-123.pdf
```

---

### ATM - Aqui Tem MEC 2 ⏳

**Status**: Pending migration

**Description**: Municipal report on educational programs from MEC.

**Parameters**:
- `cod_ibge` (required): Municipal IBGE code
- `ano` (optional): Reference year (default: 2024)

**Queries**: 20+ BigQuery queries

**Complexity**: High (most complex report)

**Usage**:
```bash
schoolreport generate ATM --params '{"cod_ibge": "3550308", "ano": 2024}' --output atm-3550308.pdf
```

---

## Creating a New Report

See [MIGRATION_GUIDE.md](../MIGRATION_GUIDE.md) for detailed instructions.

### Quick Start

1. **Create directory structure**:
   ```bash
   mkdir -p reports/NEW_REPORT/{queries,template/assets}
   ```

2. **Create report.yaml**:
   ```yaml
   id: NEW_REPORT
   name: Report Name
   parameters: [...]
   queries: [...]
   template:
     entry: template/main.typ
   ```

3. **Add SQL queries**:
   ```bash
   cat > reports/NEW_REPORT/queries/query1.sql << 'EOF'
   SELECT * FROM table WHERE param = @param
   EOF
   ```

4. **Create Typst template**:
   ```bash
   cp reports/atsbr/template/main.typ reports/NEW_REPORT/template/main.typ
   # Customize as needed
   ```

5. **(Optional) Add custom charts** — `charts.py`:
   ```python
   from schoolreport.charts import chart, ChartContext
   import matplotlib.pyplot as plt

   @chart("my_chart", data="my_query", size=(900, 320))
   def my_chart(df, ctx: ChartContext):
       fig, ax = plt.subplots(figsize=ctx.figsize)
       ax.bar(df["label"], df["value"])
       return fig
   ```

6. **(Optional) Add custom executor** — `executor.py`:

   Only needed for reports that require custom BigQuery orchestration, cross-query metrics, or specialized pipeline logic. Use `schoolreport.core` primitives (`fmt_brl`, `fmt_pct`, `write_charts_to_assets`, `TypstClient.render_to_bytes`, `BigQueryClient.execute_query_as_dicts`) to avoid boilerplate. See [DEVELOPER_GUIDE.md](../DEVELOPER_GUIDE.md#reusable-primitives-for-custom-executors).

7. **Validate and test**:
   ```bash
   schoolreport report validate NEW_REPORT
   schoolreport generate NEW_REPORT --params '{}' --output test.pdf
   ```

### Customization Levels

| Need | Solution | Files |
|------|----------|-------|
| Simple queries + template | Declarative only | `report.yaml` + `queries/` + `template/` |
| Custom matplotlib charts | Add `charts.py` | + `charts.py` with `@chart` decorators |
| Full pipeline control | Add `executor.py` | + `executor.py` with primitives from `schoolreport.core` |

## Report Definition Schema

See [MIGRATION_GUIDE.md](../MIGRATION_GUIDE.md#step-2-migrate-reportyaml) for the complete schema.

### Minimal Example

```yaml
id: EXAMPLE
name: Example Report
description: A simple example report

parameters:
  - name: cod_ibge
    type: string
    required: true

sources:
  bigquery:
    project: br-mec-segape

queries:
  - name: data
    source: bigquery
    file: queries/data.sql

charts: []

template:
  entry: template/main.typ

cache:
  enabled: true
  ttl_days: 30
```

## Testing Reports

### Validate Definition

```bash
# Validate single report
schoolreport report validate ATSBR

# Validate all reports
schoolreport report validate --all
```

### Generate Locally

```bash
# Generate report
schoolreport generate ATSBR --output test.pdf

# With verbose output
schoolreport generate ATSBR --output test.pdf --verbose

# Dry run (validation only)
schoolreport generate ATSBR --dry-run
```

### Compare with R Version

```bash
# Generate with Python
schoolreport generate ATSBR --output python-version.pdf

# Generate with R (from the repository root)
cd school-report-r
R -e "devtools::load_all(); schoolreport::generate_report('ATSBR')"

# Compare outputs
diff python-version.pdf r-version.pdf
```

## Common Tasks

### List Available Reports

```bash
schoolreport report list
```

### Show Report Details

```bash
schoolreport report show ATSBR
```

### Update Report Definition

1. Edit `reports/{REPORT_ID}/report.yaml`
2. Validate changes: `schoolreport report validate {REPORT_ID}`
3. Test generation: `schoolreport generate {REPORT_ID} --output test.pdf`
4. Commit changes

### Add a New Query

1. Create SQL file: `reports/{REPORT_ID}/queries/new_query.sql`
2. Add to `report.yaml`:
   ```yaml
   queries:
     - name: new_query
       source: bigquery
       file: queries/new_query.sql
   ```
3. Update template to use query results
4. Test generation

## Best Practices

### SQL Queries

- Use parameterized queries (no SQL injection)
- Add comments explaining query purpose
- Use CTEs for readability
- Optimize for BigQuery performance
- Test with `bq query` CLI first

### Typst Templates

- Keep templates modular (use components)
- Handle missing data gracefully
- Use consistent styling
- Add comments for complex logic
- Test with sample data

### Report Definitions

- Use semantic versioning for `version` field
- Document all parameters clearly
- Set reasonable cache TTL
- Add maintainer information
- Keep descriptions up-to-date

## Troubleshooting

### Report Not Found

```
ValueError: Report 'EXAMPLE' not found in registry
```

**Solution**: Check that `reports/EXAMPLE/report.yaml` exists and is valid.

### Invalid YAML

```
yaml.scanner.ScannerError: mapping values are not allowed here
```

**Solution**: Check YAML syntax (indentation, colons, quotes).

### Query Fails

```
google.cloud.bigquery.exceptions.BadRequest: Invalid query
```

**Solution**:
- Test query in BigQuery console
- Check parameter names match report.yaml
- Verify table names and permissions

### Template Error

```
typst: error: unknown variable: data
```

**Solution**:
- Check `sys.inputs.at("data")` is used correctly
- Verify data structure matches template expectations
- Test with `--data-only` flag first

## Migration Status

| Report | Status | Queries | Parameters | Complexity | Priority |
|--------|--------|---------|------------|------------|----------|
| ATSBR | ✅ Migrated | 8 | 0 | Low | 1 |
| ATS | ⏳ Pending | 7 | 1 | Medium | 2 |
| ATM | ⏳ Pending | 20+ | 2 | High | 3 |

## Resources

- [Developer Guide](../DEVELOPER_GUIDE.md) - Setup and CLI usage
- [Migration Guide](../MIGRATION_GUIDE.md) - Migrating reports from R
- [Architecture Docs](../../docs/ARCHITECTURE_PYTHON.md) - System architecture
- [Typst Documentation](https://typst.app/docs) - Template language reference

---

**Last Updated**: 2025-01-26
**Maintainers**: João Pedro Oliveira, George Moreno
