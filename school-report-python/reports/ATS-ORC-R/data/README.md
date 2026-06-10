# ATS-02 - Dados de Teste

Este diretório contém dados de teste para desenvolvimento e testes locais do relatório ATS-02, **sem necessidade de conexão com BigQuery**.

## Arquivos Disponíveis

### 1. `test_data.json` (Básico)

Dados mínimos para testar a estrutura básica do relatório.

**Conteúdo**:
- Metadados da instituição (UFAL)
- Parâmetros básicos
- Dados de orçamento para P1 (Visão Geral)
- Dados de execução para P6 (Despesas Liquidadas)

**Uso**: Testes rápidos, validação de estrutura

### 2. `test_data_complete.json` (Completo) ⭐ RECOMENDADO

Conjunto completo de dados realistas cobrindo **todas as seções do relatório**.

**Conteúdo**:
- ✅ Metadados completos
- ✅ Resumo executivo
- ✅ Orçamento aprovado (LOA, Dotação)
- ✅ Despesas obrigatórias
- ✅ Despesas discricionárias
- ✅ Emendas parlamentares
- ✅ Execução orçamentária
- ✅ Ações específicas (4002, 4572, 20KG, 20RK, 4086, 8282)
- ✅ Novo PAC
- ✅ Restos a pagar
- ✅ Indicadores gerais
- ✅ Comparativo nacional

**Dados simulados para**: UFAL (Universidade Federal de Alagoas) - Ano base 2024

### 3. `schema.json`

Schema de validação JSON para estrutura de dados de entrada.

**Uso**: Validação automática de dados no executor

## Estrutura dos Dados

### Metadados

```json
{
  "metadata": {
    "sigla": "UFAL",
    "universidade": "Universidade Federal de Alagoas",
    "generated_at": "2026-02-04T10:30:00Z",
    "system_version": "1.0.0",
    "relatorio": "Relatório Orçamentário - Aqui Tem Superior",
    "ano_base": 2024
  }
}
```

### Parâmetros

```json
{
  "params": {
    "sigla": "UFAL",
    "instituicao_id": "UFAL",
    "ano_base": 2024
  }
}
```

### Dados Orçamentários

```json
{
  "orcamento_aprovado": {
    "visao_geral": {
      "anos": ["2020", "2021", "2022", "2023", "2024"],
      "loa_valores": [850.5, 920.3, 985.7, 1020.4, 1105.2],
      "dotacao_valores": [845.2, 915.8, 980.1, 1015.3, 1098.6]
    }
  }
}
```

**Valores**: Em milhões de reais (R$ milhões)

### Execução Orçamentária

```json
{
  "execucao_orcamentaria": {
    "geral": {
      "dotacao": "1.098,6",
      "empenhado": "983,4",
      "liquidado": "879,8",
      "pago": "856,2",
      "pct_empenhado": 89.5,
      "pct_liquidado": 80.1,
      "pct_pago": 77.9
    }
  }
}
```

## Como Usar

### Método 1: Script de Teste (Recomendado)

Use o script `test_generate.py` na raiz do relatório:

```bash
cd school-report-python/reports/ATS-02/

# Gerar com dados completos (padrão)
python test_generate.py

# Usar dados básicos
python test_generate.py --data data/test_data.json

# Especificar saída customizada
python test_generate.py --output meu_relatorio.pdf
```

**Saída padrão**: `output/relatorio_ats02_teste.pdf`

### Método 2: Python Direto

```python
import asyncio
import json
from pathlib import Path

async def test_report():
    # Importar executor
    from ATS_02.executor import ATS02Executor

    # Carregar dados
    with open('data/test_data_complete.json') as f:
        data = json.load(f)

    # Gerar relatório
    reports_dir = Path(__file__).parent.parent
    executor = ATS02Executor(reports_dir)
    pdf_bytes = await executor.execute(data)

    # Salvar
    with open('output/relatorio.pdf', 'wb') as f:
        f.write(pdf_bytes)

    print("✅ Relatório gerado!")

asyncio.run(test_report())
```

### Método 3: Via CLI (Futuro)

```bash
schoolreport generate ATS-02 \
    --from-file data/test_data_complete.json \
    --output relatorio.pdf
```

## Customizar Dados de Teste

### Para Outra Instituição

1. Copie `test_data_complete.json`
2. Altere os metadados:

```json
{
  "metadata": {
    "sigla": "UFPE",
    "universidade": "Universidade Federal de Pernambuco",
    "ano_base": 2024
  },
  "params": {
    "sigla": "UFPE",
    "instituicao_id": "UFPE",
    "ano_base": 2024
  }
}
```

3. Ajuste os valores orçamentários conforme necessário

### Para Outro Ano

```json
{
  "params": {
    "ano_base": 2025
  },
  "orcamento_aprovado": {
    "visao_geral": {
      "anos": ["2021", "2022", "2023", "2024", "2025"],
      "loa_valores": [920.3, 985.7, 1020.4, 1105.2, 1187.8]
    }
  }
}
```

## Formato de Valores

### Valores Monetários

- **Strings formatadas**: `"1.105,2"` (para exibição)
- **Números raw**: `1105200000` (para cálculos)

```json
{
  "orcamento_total_2024": "1.105,2",       // Display
  "orcamento_total_2024_raw": 1105200000   // Valor real em reais
}
```

### Percentuais

- **Números**: `89.5` (formato decimal, representa 89,5%)

```json
{
  "pct_liquidado": 89.5  // 89.5%
}
```

### Arrays Temporais

```json
{
  "anos": ["2020", "2021", "2022", "2023", "2024"],
  "valores": [850.5, 920.3, 985.7, 1020.4, 1105.2]
}
```

## Validação dos Dados

### Validação Automática

O executor valida automaticamente contra `schema.json`:

```python
# Validação é feita automaticamente
pdf = await executor.execute(data)  # Valida internamente
```

### Validação Manual

```python
import json
import jsonschema

# Carregar schema
with open('data/schema.json') as f:
    schema = json.load(f)

# Carregar dados
with open('data/test_data_complete.json') as f:
    data = json.load(f)

# Validar
try:
    jsonschema.validate(data, schema)
    print("✓ Dados válidos!")
except jsonschema.ValidationError as e:
    print(f"✗ Erro de validação: {e.message}")
```

## Dicas

### Performance

- Use `test_data.json` para testes rápidos de estrutura
- Use `test_data_complete.json` para validação completa

### Debugging

1. Adicione `print()` statements no executor
2. Use dados simplificados primeiro
3. Incremente complexidade gradualmente

### Gráficos

Os gráficos são gerados automaticamente pelo executor a partir dos dados:

```json
{
  "orcamento_aprovado": {
    "visao_geral": {
      "anos": [...],
      "loa_valores": [...]  // → Gera gráfico P1-G1
    }
  }
}
```

Não é necessário fornecer gráficos pré-gerados!

## Troubleshooting

### Erro: "Required field missing"

Verifique se todos os campos obrigatórios estão presentes:

```json
{
  "metadata": {
    "sigla": "...",        // OBRIGATÓRIO
    "universidade": "..."  // OBRIGATÓRIO
  },
  "params": {
    "instituicao_id": "...",  // OBRIGATÓRIO
    "ano_base": 2024          // OBRIGATÓRIO
  }
}
```

### Erro: "Invalid JSON"

Valide o JSON:

```bash
python -m json.tool data/test_data_complete.json
```

### Gráficos não aparecem

Verifique se os dados da seção correspondente estão presentes:

- P1-G1 requer `orcamento_aprovado.visao_geral`
- P6-G1 requer `execucao_orcamentaria.por_tipo`

## Exemplos de Dados Reais

Os valores em `test_data_complete.json` são baseados em:

- **Orçamentos médios** de universidades federais brasileiras
- **Padrões de execução** típicos do setor público
- **Proporções realistas** entre categorias orçamentárias

**Nota**: Dados são simulados para fins de teste, não representam dados reais da UFAL.

## Integração com BigQuery (Produção)

Em produção, estes dados virão do BigQuery:

```python
# Produção: dados do BigQuery
data = await bigquery_client.execute_queries(report_id, params)

# Desenvolvimento: dados de teste
with open('data/test_data_complete.json') as f:
    data = json.load(f)

# Mesmo executor funciona para ambos!
pdf = await executor.execute(data)
```

## Contribuindo

### Adicionar Novos Dados de Teste

1. Criar arquivo `test_data_[nome].json`
2. Seguir estrutura do schema
3. Documentar neste README
4. Testar geração do relatório

### Melhorar Dados Existentes

1. Editar `test_data_complete.json`
2. Garantir consistência (somas, percentuais)
3. Validar contra schema
4. Testar geração

## Recursos

- [JSON Schema Validator](https://www.jsonschemavalidator.net/)
- [Schema ATS-02](./schema.json)
- [Executor ATS-02](../executor.py)
- [README Principal](../README.md)

---

*Última atualização: 2026-02-04*
