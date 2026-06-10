#!/usr/bin/env python
"""
Post-generation hook for cookiecutter template.

Performs cleanup and post-generation setup.
"""

import os
import shutil
from pathlib import Path


def remove_files_for_no_queries():
    """Remove query files if has_queries == no."""
    has_queries = '{{ cookiecutter.has_queries }}'

    if has_queries == 'no':
        print("Removing query files (has_queries=no)...")
        queries_dir = Path('queries')
        if queries_dir.exists():
            shutil.rmtree(queries_dir)
            print("  ✓ Removed queries/ directory")


def remove_files_for_no_charts():
    """Remove chart files if has_charts == no."""
    has_charts = '{{ cookiecutter.has_charts }}'

    if has_charts == 'no':
        print("Removing chart files (has_charts=no)...")
        charts_dir = Path('charts')
        if charts_dir.exists():
            # Keep __init__.py but remove chart generators
            for file in charts_dir.glob('*.py'):
                if file.name != '__init__.py':
                    file.unlink()
                    print(f"  ✓ Removed {file.name}")


def create_readme():
    """Create a README.md file for the report."""
    report_id = '{{ cookiecutter.report_id }}'
    report_name = '{{ cookiecutter.report_name }}'
    report_description = '{{ cookiecutter.report_description }}'
    has_queries = '{{ cookiecutter.has_queries }}'
    has_charts = '{{ cookiecutter.has_charts }}'

    readme_content = f"""# {report_name} ({report_id})

{report_description}

## Características

- **ID**: `{report_id}`
- **Versão**: `{{ cookiecutter.report_version }}`
- **Mantido por**: {{ cookiecutter.maintainer }}
- **Queries BigQuery**: {'Sim' if has_queries == 'yes' else 'Não'}
- **Gráficos Dinâmicos**: {'Sim' if has_charts == 'yes' else 'Não'}
- **Cache**: {'Habilitado' if '{{ cookiecutter.cache_enabled }}' == 'yes' else 'Desabilitado'}

## Estrutura

```
{report_id}/
├── report.yaml           # Configuração do relatório
├── executor.py           # Executor Python
"""

    if has_queries == 'yes':
        readme_content += """├── queries/              # Queries BigQuery (.sql)
"""

    if has_charts == 'yes':
        readme_content += """├── charts/               # Geradores de gráficos
│   ├── __init__.py
│   ├── bar_chart.py      # Gráficos de barras
│   ├── line_chart.py     # Gráficos de linha
│   └── gauge.py          # Gauges semicirculares
"""

    readme_content += """├── data/
│   ├── schema.json       # Schema de validação JSON
│   └── test_data.json    # Dados de teste
└── template/
    ├── main.typ          # Template principal Typst
    ├── components/       # (vazio - usa componentes compartilhados)
    ├── pages/            # Páginas do relatório
    │   └── page01.typ
    └── assets/           # Assets específicos do relatório
```

## Uso

### Via Python

```python
from pathlib import Path
from school_report_python.reports.{report_id}.executor import {report_id.replace('-', '').replace('_', '')}Executor

# Inicializar executor
reports_dir = Path("school-report-python/reports")
executor = {report_id.replace('-', '').replace('_', '')}Executor(reports_dir)

# Preparar dados
data = {{
    "metadata": {{
        "instituicao": "Universidade Federal de Exemplo",
        "sigla": "UFEX",
        "generated_at": "2026-02-04T10:00:00Z",
        "system_version": "1.0.0"
    }},
    "params": {{
        "instituicao_id": "UFEX",
        "ano_base": 2024
    }},
    "queries": {{}},
    "charts": {{}}
}}

# Gerar relatório
pdf_bytes = await executor.execute(data)
```

### Via CLI

```bash
schoolreport generate {report_id} \\
    --instituicao-id UFEX \\
    --ano-base 2024 \\
    --output report.pdf
```

## Desenvolvimento

### Adicionar novas páginas

1. Criar arquivo em `template/pages/pageXX.typ`
2. Importar no `main.typ`
3. Adicionar conteúdo

### Adicionar novos gráficos

1. Criar gerador em `charts/novo_grafico.py`
2. Exportar no `charts/__init__.py`
3. Chamar no `executor.py`
4. Referenciar no template

### Testar localmente

```bash
# Com dados de teste
python -m pytest tests/test_{report_id.lower().replace('-', '_')}.py

# Geração manual
python scripts/test_generate_{report_id.lower().replace('-', '_')}.py
```

## Próximos Passos

- [ ] Implementar páginas customizadas
- [ ] Adicionar queries BigQuery (se aplicável)
- [ ] Implementar geradores de gráficos (se aplicável)
- [ ] Criar dados de teste realistas
- [ ] Adicionar testes unitários
- [ ] Documentar parâmetros específicos

## Componentes Compartilhados

Este relatório usa componentes compartilhados em `reports/_shared/components/`:

- `style.typ` - Estilos e cores padrão
- `header.typ` - Cabeçalho padrão
- `footer.typ` - Rodapé com numeração
- `capa.typ` - Capa padrão
- `sumario.typ` - Sumário/índice
- `cards.typ` - Cards e containers
- `totalizers.typ` - Totalizadores
- `page-setup.typ` - Configuração de páginas

Para personalizar, basta sobrescrever os imports ou criar versões locais.

---

*Gerado por cookiecutter em {{ '%Y-%m-%d' | strftime }}*
"""

    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print("✓ Created README.md")


def create_test_data():
    """Create a test_data.json file."""
    test_data = """{
  "metadata": {
    "instituicao": "Universidade Federal de Exemplo",
    "sigla": "UFEX",
    "generated_at": "2026-02-04T10:00:00Z",
    "system_version": "1.0.0"
  },
  "params": {
    "instituicao_id": "UFEX",
    "ano_base": 2024
  },
  "queries": {},
  "charts": {}
}
"""

    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)

    with open(data_dir / 'test_data.json', 'w', encoding='utf-8') as f:
        f.write(test_data)

    print("✓ Created data/test_data.json")


def print_next_steps():
    """Print next steps for the user."""
    report_id = '{{ cookiecutter.report_id }}'
    has_queries = '{{ cookiecutter.has_queries }}'
    has_charts = '{{ cookiecutter.has_charts }}'

    print()
    print("=" * 60)
    print(f"Report {report_id} created successfully!")
    print("=" * 60)
    print()
    print("Next steps:")
    print()
    print("1. Review the generated files:")
    print(f"   cd {report_id}/")
    print("   ls -la")
    print()
    print("2. Customize the template:")
    print("   - Edit template/main.typ")
    print("   - Add pages in template/pages/")
    print("   - Update data/schema.json")
    print()

    if has_queries == 'yes':
        print("3. Add BigQuery queries:")
        print("   - Create .sql files in queries/")
        print("   - Update report.yaml")
        print()

    if has_charts == 'yes':
        print("4. Implement chart generators:")
        print("   - Customize charts/*.py")
        print("   - Update executor.py to call them")
        print()

    print(f"{3 if has_queries == 'no' and has_charts == 'no' else 5}. Test the report:")
    print("   - Update data/test_data.json")
    print("   - Run executor locally")
    print()
    print("6. Read README.md for detailed documentation")
    print()
    print("Happy coding! 🚀")
    print()


def main():
    """Run post-generation tasks."""
    print()
    print("Running post-generation tasks...")
    print()

    remove_files_for_no_queries()
    remove_files_for_no_charts()
    create_readme()
    create_test_data()

    print_next_steps()


if __name__ == "__main__":
    main()
