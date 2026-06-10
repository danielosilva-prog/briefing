// ===================================
// {{ cookiecutter.report_id }} Report Template - Main Entry Point
// {{ cookiecutter.report_name }}
// ===================================

// Read data from JSON input
// The Python renderer passes the data file path via sys.inputs.data
#let data = json(sys.inputs.at("data", default: "data.json"))

// Extract data sections
#let queries = data.at("queries", default: (:))
#let charts = data.at("charts", default: (:))
#let metadata = data.at("metadata", default: (:))

// Document settings
#set document(
  title: "{{ cookiecutter.report_name }}",
  author: "Ministério da Educação - SEGAPE",
  date: datetime.today(),
)

// Page setup
#set page(
  paper: "a4",
  margin: (
    top: 2cm,
    bottom: 2cm,
    left: 2cm,
    right: 2cm,
  ),
  numbering: "1",
)

// Text settings
#set text(
  font: "Latin Modern Roman",
  size: 11pt,
  lang: "pt",
)

// Heading settings
#show heading.where(level: 1): it => {
  set text(size: 18pt, weight: "bold")
  block(
    below: 1em,
    above: 1.5em,
    it
  )
}

#show heading.where(level: 2): it => {
  set text(size: 14pt, weight: "bold")
  block(
    below: 0.8em,
    above: 1.2em,
    it
  )
}

// ===================================
// COVER PAGE
// ===================================

#align(center)[
  #v(4cm)

  #text(size: 24pt, weight: "bold")[
    {{ cookiecutter.report_name | upper }}
  ]

  #v(1cm)

  #text(size: 14pt)[
    {{ cookiecutter.description }}
  ]

  #v(2cm)

  // Add your logo here
  // #image("assets/logo.svg", width: 6cm)

  #v(fill: 1fr)

  #text(size: 12pt)[
    Ministério da Educação
  ]

  #text(size: 10pt)[
    Secretaria Executiva do MEC (SEGAPE)
  ]

  #v(1cm)

  #text(size: 10pt)[
    #metadata.at("generated_at", default: datetime.today().display())
  ]
]

#pagebreak()

// ===================================
// TABLE OF CONTENTS
// ===================================

#outline(
  title: "Sumário",
  indent: auto,
)

#pagebreak()

// ===================================
// MAIN CONTENT
// ===================================

= Introdução

Este relatório apresenta os dados de {{ cookiecutter.report_name | lower }}.

== Dados Principais

// Access query results
#let example_data = queries.at("example_data", default: none)

#if example_data != none [
  #if type(example_data) == "array" and example_data.len() > 0 [
    // Display data in a table
    #table(
      columns: (auto, auto, auto),
      align: (left, right, left),
      stroke: 0.5pt + gray,
      fill: (col, row) => if row == 0 { rgb("#2E4172").lighten(80%) } else { none },

      [*Categoria*], [*Valor*], [*Descrição*],

      ..example_data.map(row => (
        [#row.at("category", default: "-")],
        [#row.at("value", default: "-")],
        [#row.at("description", default: "-")],
      )).flatten()
    )
  ] else [
    _Nenhum dado retornado pela query._
  ]
] else [
  _Dados não disponíveis._
]

#pagebreak()

// ===================================
// TECHNICAL SHEET
// ===================================

= Ficha Técnica

*Título:* {{ cookiecutter.report_name }}

*Instituição:* Ministério da Educação (MEC)

*Secretaria:* Secretaria Executiva do MEC (SEGAPE)

*Fontes de Dados:*
- BigQuery - br-mec-segape

{% if cookiecutter.has_parameters == 'yes' -%}
*Parâmetros:*
- {{ cookiecutter.parameter_name }}: #metadata.at("{{ cookiecutter.parameter_name }}", default: "-")
{% endif %}
*Data de Geração:* #metadata.at("generated_at", default: datetime.today().display())

*Versão do Sistema:* #metadata.at("system_version", default: "1.0.0")

#v(2cm)

#align(center)[
  _Este relatório foi gerado automaticamente pelo sistema de relatórios do MEC._
]
