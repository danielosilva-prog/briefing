# School Report - Python

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Sistema de geração de relatórios educacionais para o SEGAPE/MEC. Arquitetura moderna baseada em Python com processamento assíncrono, templates Typst e integração com Google Cloud.

## Índice

- [Funcionalidades](#funcionalidades)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Início Rápido](#início-rápido)
- [Configuração](#configuração)
- [Referência CLI](#referência-cli)
- [API REST](#api-rest)
- [Criando Novos Relatórios](#criando-novos-relatórios)
- [Desenvolvimento](#desenvolvimento)
- [Testes](#testes)
- [Deploy com Docker](#deploy-com-docker)
- [Arquitetura](#arquitetura)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

## Funcionalidades

- **Relatórios declarativos**: Definições em YAML para configuração de relatórios
- **Processamento assíncrono**: Arquitetura baseada em filas com Redis + arq
- **Múltiplas fontes de dados**: BigQuery, PostgreSQL
- **CLI & API**: Interfaces de linha de comando e REST API
- **Templates Typst**: Geração de PDFs de alta qualidade com tipografia profissional
- **Cache inteligente**: Sistema de cache com TTL configurável
- **Auto-scaling**: Escalabilidade horizontal com Kubernetes

## Pré-requisitos

Antes de começar, certifique-se de ter instalado:

| Requisito | Versão | Descrição |
|-----------|--------|-----------|
| Python | 3.12+ | Linguagem de programação |
| uv | latest | Gerenciador de pacotes Python |
| Typst | latest | Compilador de documentos para PDFs |
| GCP Credentials | - | Credenciais de serviço do Google Cloud |

### Instalando uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Instalando Typst

```bash
# macOS (Homebrew)
brew install typst

# Linux (cargo)
cargo install --git https://github.com/typst/typst --locked typst-cli

# Ou baixe direto: https://github.com/typst/typst/releases
```

## Instalação

```bash
# Clone o repositório
git clone https://github.com/mec-gov-br/school-report.git
cd school-report/school-report-python

# Instale as dependências
uv sync

# Ative o ambiente virtual
source .venv/bin/activate

# Verifique a instalação
schoolreport --help
```

## Início Rápido

### 1. Configure as credenciais GCP

```bash
# Opção 1: Variável de ambiente
export GOOGLE_APPLICATION_CREDENTIALS=/caminho/para/credentials.json

# Opção 2: Arquivo na raiz do projeto
cp /caminho/para/credentials.json .gcp-credentials.json

# Opção 3: Login via gcloud (desenvolvimento local)
gcloud auth application-default login
```

### 2. Gere seu primeiro relatório

```bash
# Listar relatórios disponíveis
schoolreport reports list

# Gerar um relatório (sem parâmetros)
schoolreport generate ATSBR

# Gerar relatório com parâmetros
schoolreport generate ATM cod_ibge=2304400 ano=2024

# Abrir o PDF automaticamente após geração
schoolreport generate ATSBR --open
```

## Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto ou exporte as variáveis:

```bash
# Obrigatório para acesso a dados
GOOGLE_APPLICATION_CREDENTIALS=/caminho/para/credentials.json
GCP_PROJECT_ID=br-mec-segape

# Opcional: Upload para GCS
GCS_BUCKET_NAME=segape-reports

# Opcional: Banco de dados (para API/worker)
DATABASE_URL=postgresql://user:pass@localhost:5432/schoolreport
REDIS_URL=redis://localhost:6379/0

# Opcional: Configurações de ambiente
ENVIRONMENT=development
DEBUG=true
```

### Credenciais GCP

O sistema busca credenciais na seguinte ordem:

1. Variável `GOOGLE_APPLICATION_CREDENTIALS`
2. Arquivo `.gcp-credentials.json` na raiz do projeto
3. Application Default Credentials (ADC) - `gcloud auth application-default login`

**Permissões necessárias:**
- BigQuery Data Viewer
- BigQuery Job User
- Storage Object Admin (para upload GCS)

## Referência CLI

### Comandos Principais

| Comando | Descrição |
|---------|-----------|
| `schoolreport generate <ID>` | Gera um relatório |
| `schoolreport reports list` | Lista relatórios disponíveis |
| `schoolreport reports show <ID>` | Mostra detalhes de um relatório |
| `schoolreport reports validate [ID]` | Valida definição de relatório |
| `schoolreport auth whoami` | Mostra identidade autenticada |
| `schoolreport dev serve` | Inicia servidor de desenvolvimento |
| `schoolreport dev query <ID>` | Executa queries de debug |

### schoolreport generate

Gera um relatório localmente. Suporta **modo lote** passando múltiplos valores separados por vírgula em qualquer parâmetro.

```bash
schoolreport generate <REPORT_ID> [PARAMS...] [OPTIONS]
```

**Argumentos:**
- `REPORT_ID`: ID do relatório (ex: `ATM`, `ATSBR`)
- `PARAMS`: Parâmetros no formato `chave=valor`. Use vírgulas para lote: `chave=v1,v2,v3`

**Opções:**
| Opção | Descrição |
|-------|-----------|
| `-o, --output PATH` | Arquivo de saída (modo simples) ou diretório de saída (modo lote) |
| `--data-only` | Exporta apenas os dados em JSON |
| `--upload` | Faz upload para GCS após geração |
| `--open` | Abre o PDF após geração (ignorado no modo lote) |
| `--no-cache` | Desativa o cache de queries |
| `--keep-chart-files` | Preserva os arquivos temporários `.chart_*.svg` e `.data_*.json` gerados durante a renderização Typst |

**Exemplos — relatório único:**

```bash
# Gerar relatório básico
schoolreport generate ATSBR

# Gerar com parâmetros
schoolreport generate ATM cod_ibge=2304400 ano=2024

# Salvar em local específico
schoolreport generate ATM cod_ibge=2304400 --output relatorio.pdf

# Exportar apenas dados
schoolreport generate ATM cod_ibge=2304400 --data-only --output dados.json

# Gerar PDF e preservar os SVGs temporários dos gráficos
schoolreport generate ATM cod_ibge=2304400 --keep-chart-files

# Gerar e fazer upload para GCS
schoolreport generate ATM cod_ibge=2304400 --upload
```

**Exemplos — modo lote:**

```bash
# Gerar 3 relatórios sequencialmente (um por cod_ibge)
schoolreport generate ATM cod_ibge=2304400,2304459,2304202 ano=2024

# Dois parâmetros com listas do mesmo tamanho são "zipados" (não produto cartesiano)
schoolreport generate ATM cod_ibge=2304400,2304459 ano=2023,2024
# → relatório 1: cod_ibge=2304400 ano=2023
# → relatório 2: cod_ibge=2304459 ano=2024

# Salvar todos em um diretório específico
schoolreport generate ATM cod_ibge=2304400,2304459,2304202 ano=2024 --output ./lote/

# Fazer upload de todos para GCS
schoolreport generate ATM cod_ibge=2304400,2304459,2304202 ano=2024 --upload
```

> **Comportamento do modo lote:**
> - Relatórios executados um a um, sequencialmente
> - Falha em um relatório não interrompe os demais
> - Resumo exibido ao final com sucessos e falhas
> - `--output` aponta para um **diretório** (não um arquivo)
> - Exit code `1` se qualquer relatório falhar

### schoolreport reports

Gerenciamento de relatórios.

```bash
# Listar todos os relatórios
schoolreport reports list

# Listar em formato JSON
schoolreport reports list --format json

# Mostrar detalhes de um relatório
schoolreport reports show ATM

# Validar um relatório específico
schoolreport reports validate ATM

# Validar todos os relatórios
schoolreport reports validate --all
```

### schoolreport dev

Comandos de desenvolvimento.

```bash
# Iniciar servidor de desenvolvimento
schoolreport dev serve

# Servidor com hot-reload
schoolreport dev serve --reload

# Servidor em porta específica
schoolreport dev serve --port 8080

# Executar queries para debug
schoolreport dev query ATM cod_ibge=2304400

# Executar query específica
schoolreport dev query ATM cod_ibge=2304400 --query municipio

# Exportar resultado de queries
schoolreport dev query ATM cod_ibge=2304400 --format json --output dados.json
```

## API REST

O servidor API fornece endpoints para geração de relatórios via HTTP.

### Iniciar o servidor

```bash
# Desenvolvimento
schoolreport dev serve

# Produção (com Docker)
docker-compose -f docker/docker-compose.yml up
```

### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/health` | Health check |
| `GET` | `/reports` | Lista relatórios disponíveis |
| `GET` | `/reports/{id}` | Detalhes de um relatório |
| `POST` | `/reports/{id}/generate` | Solicita geração de relatório |
| `GET` | `/jobs/{id}` | Status de um job |

### Exemplos com curl

```bash
# Health check
curl http://localhost:8000/health

# Listar relatórios
curl http://localhost:8000/reports

# Detalhes de um relatório
curl http://localhost:8000/reports/ATM

# Solicitar geração (retorna job_id)
curl -X POST http://localhost:8000/reports/ATM/generate \
  -H "Content-Type: application/json" \
  -d '{"params": {"cod_ibge": "2304400", "ano": "2024"}}'

# Verificar status do job
curl http://localhost:8000/jobs/{job_id}
```

### Documentação interativa

Acesse a documentação Swagger em: `http://localhost:8000/docs`

## Criando Novos Relatórios

Use o template cookiecutter para criar novos relatórios:

```bash
# Instalar cookiecutter (se necessário)
pip install cookiecutter

# Criar novo relatório interativamente
cookiecutter templates/report

# Criar com valores padrão
cookiecutter templates/report --no-input report_id=MEU_RELATORIO

# Validar o relatório criado
schoolreport reports validate MEU_RELATORIO
```

### Estrutura de um relatório

```
reports/
└── MEU_RELATORIO/
    ├── report.yaml          # Definição do relatório
    ├── queries/             # Queries SQL
    │   └── dados.sql
    └── template/            # Template Typst
        ├── main.typ
        └── assets/
```

### Formato do report.yaml

```yaml
id: MEU_RELATORIO
name: Meu Relatório
description: Descrição do relatório
version: 1.0.0

parameters:
  - name: cod_ibge
    type: string
    required: true
    description: Código IBGE do município

sources:
  bigquery:
    project: br-mec-segape

queries:
  - name: dados_principais
    source: bigquery
    file: queries/dados.sql
    description: Dados principais do relatório

template:
  entry: template/main.typ

cache:
  enabled: true
  ttl_days: 30

output:
  filename_template: "{report_id}-{cod_ibge}.pdf"
  gcs_bucket: segape-reports
```

### Gráficos Customizados

Defina gráficos usando Python em vez de YAML. Crie um arquivo `charts.py` no diretório do relatório:

```python
# reports/MEU_RELATORIO/charts.py
from schoolreport.charts import chart, ChartContext
import matplotlib.pyplot as plt
import pandas as pd

@chart("matriculas_bar", data="dados_principais")
def matriculas_bar(df: pd.DataFrame, ctx: ChartContext) -> plt.Figure:
    """Gráfico de barras com matrículas por etapa."""
    fig, ax = plt.subplots(figsize=ctx.figsize)

    # Controle total do matplotlib
    colors = ctx.get_colors(len(df))
    ax.bar(df["etapa"], df["total"], color=colors)
    ax.set_title("Matrículas por Etapa", fontsize=ctx.title_fontsize)

    # Usar helpers do contexto
    for i, val in enumerate(df["total"]):
        ax.text(i, val + 10, ctx.format_number(val), ha="center")

    plt.tight_layout()
    return fig

# Gráfico com múltiplas fontes de dados
@chart("comparativo", data=["ano_atual", "ano_anterior"])
def comparativo(data: dict[str, pd.DataFrame], ctx: ChartContext) -> plt.Figure:
    fig, ax = plt.subplots()
    ax.plot(data["ano_atual"]["mes"], data["ano_atual"]["valor"], label="2024")
    ax.plot(data["ano_anterior"]["mes"], data["ano_anterior"]["valor"], label="2023")
    ax.legend()
    return fig

# Gráfico opcional (retorna None para pular)
@chart("grafico_opcional", data="dados")
def opcional(df: pd.DataFrame, ctx: ChartContext) -> plt.Figure | None:
    if df.empty:
        return None  # Gráfico não será incluído
    fig, ax = plt.subplots()
    ax.bar(df["x"], df["y"])
    return fig
```

**Sem necessidade de declarar no YAML** - os gráficos são auto-descobertos do `charts.py`.

**ChartContext fornece:**
- `ctx.figsize`, `ctx.dpi` - configurações de renderização
- `ctx.params` - parâmetros do relatório (ex: `ctx.params["ano"]`)
- `ctx.primary_color`, `ctx.color_palette` - cores do tema
- `ctx.format_number(value)` - formatação brasileira (1.234.567)
- `ctx.format_percent(value)` - formatação de percentual (50,5%)
- `ctx.get_colors(n)` - obter n cores da paleta

### Templates Typst

Os templates Typst recebem os dados das queries via `sys.inputs`. O pipeline Python passa automaticamente o caminho do arquivo JSON com os dados.

**Estrutura do template:**

```typst
// Carregar dados do JSON
#let data = json(sys.inputs.at("data", default: "data.json"))

// Extrair seções de dados
#let queries = data.at("queries", default: (:))
#let charts = data.at("charts", default: (:))
#let metadata = data.at("metadata", default: (:))

// Acessar resultados de uma query específica
#let dados = queries.at("dados_principais", default: none)

// Usar os dados no template
#if dados != none [
  #if type(dados) == "array" and dados.len() > 0 [
    #table(
      columns: (auto, auto),
      [*Campo*], [*Valor*],
      ..dados.map(row => (
        [#row.at("campo", default: "-")],
        [#row.at("valor", default: "-")],
      )).flatten()
    )
  ]
]
```

**Estrutura dos dados JSON:**

```json
{
  "queries": {
    "dados_principais": [
      {"campo": "Total", "valor": 100},
      {"campo": "Média", "valor": 50.5}
    ]
  },
  "charts": {},
  "metadata": {
    "generated_at": "2024-01-15T10:30:00",
    "system_version": "1.0.0",
    "cod_ibge": "2304400"
  }
}
```

## Desenvolvimento

### Setup do ambiente

```bash
# Instalar dependências de desenvolvimento
uv sync --dev

# Ativar ambiente virtual
source .venv/bin/activate
```

### Ferramentas de qualidade de código

```bash
# Formatar código
black src/ tests/

# Lint
ruff check src/ tests/

# Lint com correção automática
ruff check src/ tests/ --fix

# Type checking
mypy src/
```

### Estrutura do projeto

```
school-report-python/
├── src/
│   └── schoolreport/
│       ├── api/           # FastAPI endpoints
│       ├── cli/           # Comandos Typer
│       ├── core/          # Lógica de negócio
│       ├── models/        # Modelos Pydantic
│       ├── services/      # Serviços (registry, cache)
│       └── config.py      # Configurações
├── reports/               # Definições de relatórios
├── templates/             # Templates cookiecutter
├── tests/                 # Testes
├── docker/                # Configurações Docker
└── pyproject.toml         # Configuração do projeto
```

## Testes

```bash
# Executar todos os testes
pytest

# Testes com cobertura
pytest --cov

# Testes com relatório de cobertura HTML
pytest --cov --cov-report=html

# Executar testes específicos
pytest tests/test_registry.py

# Executar testes por marcador
pytest -m "not slow"

# Modo verbose
pytest -v
```

## Deploy com Docker

### Desenvolvimento local

```bash
# Iniciar todos os serviços
cd docker
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down
```

### Variáveis de ambiente para Docker

Crie um arquivo `.env` no diretório `docker/`:

```bash
# Banco de dados
POSTGRES_USER=schoolreport
POSTGRES_PASSWORD=sua_senha_segura
POSTGRES_DB=schoolreport

# GCP
GCP_PROJECT_ID=br-mec-segape
GCS_BUCKET=segape-reports
GCP_CREDENTIALS_PATH=./credentials

# Workers
WORKER_REPLICAS=2
WORKER_CONCURRENCY=10
```

### Serviços disponíveis

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| `api` | 8000 | FastAPI application |
| `worker` | - | Background job processor |
| `postgres` | 5432 | Banco de dados |
| `redis` | 6379 | Fila de jobs |

## Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                         SCHOOLREPORT                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────┐    ┌───────────┐    ┌───────────┐              │
│  │    CLI    │    │  FastAPI  │    │  Worker   │              │
│  │  (Typer)  │    │   (API)   │    │   (arq)   │              │
│  └─────┬─────┘    └─────┬─────┘    └─────┬─────┘              │
│        │                │                │                     │
│        └────────────────┼────────────────┘                     │
│                         │                                       │
│              ┌──────────▼──────────┐                           │
│              │   Report Registry   │                           │
│              │   (YAML Parsing)    │                           │
│              └──────────┬──────────┘                           │
│                         │                                       │
│         ┌───────────────┼───────────────┐                      │
│         │               │               │                      │
│  ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐             │
│  │  BigQuery   │ │   Charts    │ │   Typst     │             │
│  │   Client    │ │ (Matplotlib)│ │  Renderer   │             │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘             │
│         │               │               │                      │
│         └───────────────┼───────────────┘                      │
│                         │                                       │
│              ┌──────────▼──────────┐                           │
│              │     PDF Output      │                           │
│              │   (Local / GCS)     │                           │
│              └─────────────────────┘                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     INFRAESTRUTURA                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ BigQuery │  │PostgreSQL│  │  Redis   │  │   GCS    │       │
│  │  (dados) │  │ (estado) │  │ (filas)  │  │ (output) │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Fluxo de geração de relatório

1. **Requisição** → CLI ou API recebe solicitação
2. **Registry** → Carrega definição do relatório (YAML)
3. **Queries** → Executa queries no BigQuery
4. **Charts** → Gera gráficos (se configurado)
5. **Template** → Renderiza template Typst com dados
6. **Output** → Salva PDF localmente ou faz upload para GCS

## Contribuindo

Contribuições são bem-vindas! Por favor, siga estas diretrizes:

### Processo de contribuição

1. Faça fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/minha-feature`)
3. Faça commit das mudanças (`git commit -m 'Adiciona minha feature'`)
4. Faça push para a branch (`git push origin feature/minha-feature`)
5. Abra um Pull Request

### Padrões de código

- Use `black` para formatação
- Use `ruff` para linting
- Adicione type hints em todas as funções
- Escreva testes para novas funcionalidades
- Mantenha a cobertura de testes acima de 80%

### Commits

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` nova funcionalidade
- `fix:` correção de bug
- `docs:` alterações na documentação
- `style:` formatação, ponto e vírgula, etc
- `refactor:` refatoração de código
- `test:` adição/alteração de testes
- `chore:` manutenção, dependências, etc

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

Desenvolvido por [SEGAPE/MEC](https://www.gov.br/mec) 🇧🇷
