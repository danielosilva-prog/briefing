// ============================================================================
// {{ cookiecutter.report_name }}
// ============================================================================
// ID: {{ cookiecutter.report_id }}
// Versão: {{ cookiecutter.report_version }}
// Mantido por: {{ cookiecutter.maintainer }}
// ============================================================================

// Importar componentes compartilhados
#import "../../_shared/components/style.typ": *
#import "../../_shared/components/header.typ": Header
#import "../../_shared/components/footer.typ": Footer
#import "../../_shared/components/capa.typ": Capa
#import "../../_shared/components/sumario.typ": Sumario
#import "../../_shared/components/cards.typ": Card, CardBoxed, CardGrid
#import "../../_shared/components/totalizers.typ": Totalizer, TotalizerBig, TotalizerGrid
#import "../../_shared/components/page-setup.typ": *

// Importar páginas do relatório
#import "pages/page01.typ": Page01

// ============================================================================
// CARREGAR DADOS
// ============================================================================

// Ler dados JSON passados via sys.inputs
#let raw-data = sys.inputs.at("data", default: "{}")
#let data = json(raw-data)

// Extrair seções dos dados
#let metadata = data.at("metadata", default: (:))
#let params = data.at("params", default: (:))
#let queries = data.at("queries", default: (:))
#let charts = data.at("charts", default: (:))

// ============================================================================
// FUNÇÕES AUXILIARES
// ============================================================================

/// Decodifica gráfico base64 para imagem
#let decode-chart(name) = {
  let chart-data = charts.at(name, default: none)
  if chart-data != none {
    // Decodificar base64 e criar imagem
    image.decode(chart-data, format: "png")
  } else {
    // Placeholder se gráfico não existir
    box(
      width: 100%,
      height: 200pt,
      fill: bgCinzaClaro,
      stroke: (paint: borderCinza, thickness: 1pt),
    )[
      #align(center + horizon)[
        #text("Gráfico não disponível", fill: txCinza)
      ]
    ]
  }
}

/// Acessa valor seguro dos dados
#let get-value(dict, key, default: "-") = {
  dict.at(key, default: default)
}

// ============================================================================
// CONFIGURAÇÃO DO DOCUMENTO
// ============================================================================

#set document(
  title: "{{ cookiecutter.report_name }} - " + metadata.at("instituicao", default: ""),
  author: "MEC - SEGAPE",
  date: datetime.today(),
)

#set page(
  paper: "a4",
  margin: (
    left: 2cm,
    right: 2cm,
    top: 3cm,
    bottom: 2.5cm,
  ),
)

#set text(
  font: "Rawline",
  size: 10pt,
  lang: "pt",
)

#set par(
  justify: true,
  leading: 0.65em,
)

// ============================================================================
// CAPA
// ============================================================================

#Capa(
  universidade: metadata.at("instituicao", default: ""),
  sigla: metadata.at("sigla", default: ""),
  titulo-relatorio: "{{ cookiecutter.report_name }}",
  ano: str(params.at("ano_base", default: datetime.today().year())),
)

#pagebreak()

// ============================================================================
// SUMÁRIO
// ============================================================================

#Sumario(
  titulo: "Sumário",
  depth: 2,
)

#pagebreak()

// ============================================================================
// CONFIGURAR PÁGINAS COM HEADER/FOOTER
// ============================================================================

#set page(
  header: [
    #Header(
      universidade: metadata.at("instituicao", default: ""),
      sigla: metadata.at("sigla", default: ""),
    )
    #v(10pt)
  ],
  footer: [
    #v(10pt)
    #Footer()
  ],
)

// Reiniciar numeração de páginas
#counter(page).update(1)

// ============================================================================
// CONTEÚDO DO RELATÓRIO
// ============================================================================

= Introdução

Este é um template boilerplate para o relatório {{ cookiecutter.report_name }}.

Personalize este arquivo adicionando suas próprias páginas e conteúdo.

#pagebreak()

= Seção de Exemplo

== Exemplo de Totalizadores

#TotalizerGrid(
  columns: 3,
  totalizers: (
    Totalizer(
      value: get-value(queries, "total_alunos", default: "1.234"),
      description: "Total de Alunos"
    ),
    Totalizer(
      value: get-value(queries, "total_cursos", default: "45"),
      description: "Cursos Oferecidos"
    ),
    Totalizer(
      value: get-value(queries, "total_docentes", default: "567"),
      description: "Docentes"
    ),
  )
)

#pagebreak()

== Exemplo de Card com Gráfico

#Card(
  title: "Evolução de Matrículas"
)[
  #figure(
    decode-chart("grafico_exemplo"),
    caption: [Gráfico de exemplo]
  )
]

// ============================================================================
// PÁGINAS CUSTOMIZADAS
// ============================================================================

// Adicione suas páginas aqui
// #Page01(data: queries, charts: charts)

// ============================================================================
// FIM DO DOCUMENTO
// ============================================================================
