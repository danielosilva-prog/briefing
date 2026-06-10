# Shared Components - SEGAPE School Reports

Componentes compartilhados entre todos os relatórios do sistema `school-report-python`.

## Objetivo

Centralizar elementos visuais e funcionais comuns a múltiplos relatórios:

- ✅ **Consistência visual** - Mesmo look & feel em todos os relatórios
- ✅ **Manutenção centralizada** - Mudanças propagam para todos os relatórios
- ✅ **Redução de código** - DRY (Don't Repeat Yourself)
- ✅ **Onboarding rápido** - Novos desenvolvedores entendem a estrutura facilmente

## Estrutura

```
_shared/
├── README.md                 # Este arquivo
├── components/               # Componentes Typst reutilizáveis
│   ├── style.typ            # Cores, fontes, helpers
│   ├── header.typ           # Cabeçalho padrão
│   ├── footer.typ           # Rodapé com numeração
│   ├── capa.typ             # Capa institucional
│   ├── sumario.typ          # Sumário/índice
│   ├── cards.typ            # Cards e containers
│   ├── totalizers.typ       # Totalizadores
│   └── page-setup.typ       # Configuração de páginas
└── assets/                   # Assets compartilhados (futuro)
    ├── logos/               # Logos MEC, Governo, etc
    ├── backgrounds/         # Fundos padrão
    └── icons/               # Ícones comuns
```

## Componentes Disponíveis

### 1. `style.typ` - Estilos e Cores

**O que é**: Define paleta de cores, tamanhos de fonte e funções auxiliares.

**Importar**:
```typst
#import "../../_shared/components/style.typ": *
```

**Cores disponíveis**:

| Tipo | Variável | Valor | Uso |
|------|----------|-------|-----|
| **Brand** | `mecAzul` | #0095DA | Azul principal MEC |
| | `mecVerdeEscuro` | #008F00 | Verde MEC |
| | `mecAmarelo` | #FFD000 | Amarelo destaque |
| **Background** | `bgBranco` | #FFFFFF | Fundo branco |
| | `bgCinzaClaro` | #F5F5F5 | Fundo cinza claro |
| | `bgAzulClaro` | #24B0DB | Fundo azul claro |
| **Text** | `txBranco` | #FFFFFF | Texto branco |
| | `txCinza` | #646464 | Texto cinza |
| | `corTitulosTextosGeral` | #3C3C3C | Títulos padrão |

**Tamanhos de fonte**:

| Variável | Valor | Uso |
|----------|-------|-----|
| `sizeBody` | 11pt | Corpo de texto |
| `sizeSubtitle` | 13pt | Subtítulos |
| `sizeTitle` | 15pt | Títulos |
| `sizeCaption` | 7pt | Legendas/notas |
| `sizeTotalizerSmall` | 15pt | Totalizadores pequenos |
| `sizeTotalizerBig` | 24pt | Totalizadores grandes |

**Funções auxiliares**:

```typst
// Formatar moeda brasileira
#format-currency(1234.56) // → "R$ 1.234,56"

// Formatar percentual
#format-percent(0.8531) // → "85,31%"
```

### 2. `header.typ` - Cabeçalho Padrão

**O que é**: Cabeçalho com nome da instituição e logo.

**Importar**:
```typst
#import "../../_shared/components/header.typ": Header
```

**Uso básico**:
```typst
#Header(
  universidade: "Universidade Federal de Alagoas",
  sigla: "UFAL",
)
```

**Parâmetros**:

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `universidade` | string | `""` | Nome completo da instituição |
| `sigla` | string | `""` | Sigla (para buscar logo) |
| `titulo` | string | `""` | Título customizado (sobrescreve universidade) |
| `subtitulo` | string | `""` | Subtítulo opcional |
| `bgColor` | color | `mecAzul` | Cor de fundo |
| `txColor` | color | `txBranco` | Cor do texto |
| `mostrarLogo` | bool | `true` | Se deve mostrar logo |

**Exemplo customizado**:
```typst
#Header(
  universidade: "UFAL",
  sigla: "UFAL",
  titulo: "Relatório de Infraestrutura",
  subtitulo: "Ano Base 2024",
  bgColor: mecVerdeEscuro,
)
```

### 3. `footer.typ` - Rodapé com Numeração

**O que é**: Rodapé com logos e número da página.

**Importar**:
```typst
#import "../../_shared/components/footer.typ": Footer, FooterSimple
```

**Uso básico**:
```typst
#Footer()
```

**Parâmetros**:

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `show-page-number` | bool | `true` | Exibir número da página |
| `logo-left` | string | `"../assets/logos/aquiTemMEC..."` | Logo esquerdo |
| `logo-right` | string | `"../assets/logos/MEC-GOV-povo.png"` | Logo direito |
| `logo-left-height` | length | `50%` | Altura do logo esquerdo |
| `logo-right-height` | length | `70%` | Altura do logo direito |

**Rodapé simples (só número)**:
```typst
#FooterSimple()
```

### 4. `capa.typ` - Capa Institucional

**O que é**: Capa padrão com logos institucionais.

**Importar**:
```typst
#import "../../_shared/components/capa.typ": Capa, CapaSimples
```

**Uso básico**:
```typst
#Capa(
  universidade: "Universidade Federal de Alagoas",
  sigla: "UFAL",
  titulo-relatorio: "Relatório Orçamentário",
  ano: "2024",
)
```

**Parâmetros**:

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `universidade` | string | `""` | Nome completo |
| `sigla` | string | `""` | Sigla da instituição |
| `titulo-relatorio` | string | `"Relatório"` | Título do relatório |
| `subtitulo-relatorio` | string | `none` | Subtítulo opcional |
| `ano` | string | `""` | Ano de referência |
| `background-image` | string | `none` | Imagem de fundo |
| `logo-programa` | string | Path padrão | Logo do programa |
| `show-bandeira` | bool | `true` | Mostrar bandeira Brasil |

**Capa simples**:
```typst
#CapaSimples(
  titulo: "Meu Relatório",
  instituicao: "UFAL",
  ano: "2024",
)
```

### 5. `sumario.typ` - Sumário/Índice

**O que é**: Gerador automático de sumário.

**Importar**:
```typst
#import "../../_shared/components/sumario.typ": Sumario, SumarioSimples
```

**Uso básico**:
```typst
#Sumario(
  titulo: "Sumário",
  depth: 2,
)
```

**Parâmetros**:

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `titulo` | string | `"Sumário"` | Título do sumário |
| `depth` | int | `2` | Profundidade (níveis de heading) |
| `show-page-numbers` | bool | `true` | Mostrar números de página |
| `background-image` | string | `none` | Imagem de fundo |

### 6. `cards.typ` - Cards e Containers

**O que é**: Componentes de card para organização visual.

**Importar**:
```typst
#import "../../_shared/components/cards.typ": Card, CardBoxed, CardWithIcon, CardGrid
```

**Card simples**:
```typst
#Card(title: "Título do Card")[
  Conteúdo aqui...
]
```

**Card com borda e fundo**:
```typst
#CardBoxed(
  title: "Indicadores",
  bg-color: bgCinzaClaro,
  border-color: mecAzul,
)[
  Conteúdo...
]
```

**Card com ícone**:
```typst
#CardWithIcon(
  icon: "../assets/icons/clock.svg",
  title: "Total de Horas",
  value: "1.234",
  subtitle: "Horas acumuladas",
)
```

**Grid de cards**:
```typst
#CardGrid(
  columns: 2,
  cards: (
    Card(title: "Card 1")[...],
    Card(title: "Card 2")[...],
  )
)
```

### 7. `totalizers.typ` - Totalizadores

**O que é**: Componentes para exibir métricas chave.

**Importar**:
```typst
#import "../../_shared/components/totalizers.typ": Totalizer, TotalizerBig, TotalizerGrid, TotalizerWithImage
```

**Totalizador simples**:
```typst
#Totalizer(
  value: "1.234",
  description: "Total de Alunos",
)
```

**Totalizador grande**:
```typst
#TotalizerBig(
  value: "45",
  description: "Cursos Oferecidos",
)
```

**Grid de totalizadores**:
```typst
#TotalizerGrid(
  columns: 3,
  totalizers: (
    Totalizer(value: "1.234", description: "Alunos"),
    Totalizer(value: "45", description: "Cursos"),
    Totalizer(value: "567", description: "Docentes"),
  )
)
```

**Com imagem**:
```typst
#TotalizerWithImage(
  image: "../assets/icons/docente.svg",
  value: "567",
  description: "Docentes Ativos",
)
```

### 8. `page-setup.typ` - Configuração de Páginas

**O que é**: Funções para configurar páginas, headers, footers e numeração.

**Importar**:
```typst
#import "../../_shared/components/page-setup.typ": *
```

**Configuração de documento**:
```typst
#document-setup(
  paper: "a4",
  font: "Rawline",
  font-size: 10pt,
)
```

**Página com header e footer**:
```typst
#page-with-header-footer(
  universidade: "UFAL",
  sigla: "UFAL",
  header-title: "Relatório Orçamentário",
)
```

**Resetar numeração**:
```typst
#reset-page-counter()
```

## Uso em Relatórios

### Estrutura de imports recomendada

```typst
// main.typ de um relatório

// 1. Importar estilos e helpers
#import "../../_shared/components/style.typ": *

// 2. Importar componentes estruturais
#import "../../_shared/components/header.typ": Header
#import "../../_shared/components/footer.typ": Footer
#import "../../_shared/components/capa.typ": Capa
#import "../../_shared/components/sumario.typ": Sumario

// 3. Importar componentes de conteúdo
#import "../../_shared/components/cards.typ": Card, CardGrid
#import "../../_shared/components/totalizers.typ": Totalizer, TotalizerGrid

// 4. Importar utilitários
#import "../../_shared/components/page-setup.typ": *
```

### Exemplo completo de relatório

```typst
// Imports (ver acima)

// Carregar dados
#let data = json(sys.inputs.at("data"))
#let metadata = data.at("metadata")

// Configurar documento
#document-setup()

// CAPA
#Capa(
  universidade: metadata.at("universidade"),
  sigla: metadata.at("sigla"),
  titulo-relatorio: "Meu Relatório",
  ano: str(data.at("params").at("ano_base")),
)
#pagebreak()

// SUMÁRIO
#Sumario()
#pagebreak()

// CONFIGURAR PÁGINAS COM HEADER/FOOTER
#page-with-header-footer(
  universidade: metadata.at("universidade"),
  sigla: metadata.at("sigla"),
)
#reset-page-counter()

// CONTEÚDO
= Introdução

#TotalizerGrid(
  columns: 3,
  totalizers: (
    Totalizer(value: "1.234", description: "Total"),
    Totalizer(value: "567", description: "Parcial"),
    Totalizer(value: "89%", description: "Percentual"),
  )
)

#Card(title: "Análise")[
  Conteúdo da análise...
]
```

## Customização

### Sobrescrever cores

```typst
#import "../../_shared/components/style.typ": *

// Sobrescrever cor padrão
#let mecAzul = rgb("0066CC")  // Azul customizado
```

### Criar variação de componente

```typst
#import "../../_shared/components/totalizers.typ": Totalizer

// Totalizer customizado
#let MyTotalizer(value, desc) = Totalizer(
  value: value,
  description: desc,
  value-color: rgb("FF0000"),  // Vermelho
  value-size: 20pt,
)
```

### Componente completamente novo

Se um componente compartilhado não atende, crie localmente:

```typst
// template/components/my_custom.typ
#import "../../../_shared/components/style.typ": *

#let MyCustomComponent(data) = [
  // Implementação customizada
]
```

## Contribuindo

### Adicionar novo componente compartilhado

1. Criar arquivo em `_shared/components/nome.typ`
2. Seguir padrão dos existentes (cabeçalho, parâmetros, exemplos)
3. Adicionar seção neste README
4. Testar em múltiplos relatórios
5. Commitar

### Modificar componente existente

⚠️ **Atenção**: Mudanças aqui afetam TODOS os relatórios!

1. Testar em pelo menos 2 relatórios diferentes
2. Manter retrocompatibilidade quando possível
3. Documentar breaking changes
4. Atualizar README

## Melhores Práticas

### ✅ DO

- Sempre importar `style.typ` primeiro
- Usar variáveis de cor ao invés de hardcode
- Documentar parâmetros customizados
- Testar componentes em múltiplos relatórios

### ❌ DON'T

- Não duplicar código de componentes compartilhados
- Não fazer breaking changes sem avisar
- Não adicionar dependências desnecessárias
- Não hardcodar paths absolutos

## Versionamento

### Breaking Changes

Se precisar fazer breaking change:

1. Criar nova versão do componente (`component_v2.typ`)
2. Manter versão antiga por período de transição
3. Documentar migração
4. Deprecar versão antiga gradualmente

## Assets Compartilhados (Futuro)

Planejado para centralizar:

- Logos MEC, Governo, Bandeira Brasil
- Backgrounds padrão
- Ícones comuns (clock, bank, user, etc)
- Fontes customizadas

```
_shared/assets/
├── logos/
│   ├── MEC-GOV-povo.png
│   ├── bandeiraBrasil.svg
│   └── aquiTemMECEnsinoSuperior.svg
├── backgrounds/
│   ├── capa-default.svg
│   └── sumario-default.svg
└── icons/
    ├── clock.svg
    ├── bank.svg
    └── ...
```

## Troubleshooting

### Erro: "file not found"

- Verifique paths relativos (`../../_shared/...`)
- Confirme que está no nível correto (`reports/REPORT_ID/template/main.typ`)

### Componente não aparece

- Verifique se import está correto
- Confirme que todos os parâmetros obrigatórios foram passados
- Teste componente isoladamente

### Cores não aplicam

- Importe `style.typ` ANTES de outros componentes
- Use `*` no import: `#import "...": *`

## Referências

- [Typst Documentation](https://typst.app/docs/)
- [Cookiecutter Template](./_cookiecutter/README.md)
- [Exemplo Completo](../ATS-02/)

---

*Mantido por SEGAPE - 2026*
