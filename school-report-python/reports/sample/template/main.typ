#let data = json(sys.inputs.at("data", default: "data.json"))
#let queries = data.at("queries", default: (:))
#let charts = data.at("charts", default: (:))

#set page(paper: "a4", margin: 2cm)
#set text(size: 11pt, lang: "pt")

#align(center)[
  #text(size: 20pt, weight: "bold")[Sample Report]
  #v(0.5cm)
  #text(size: 12pt)[Instituições de Ensino Superior por Região]
]

#v(1cm)

// Display the chart (SVG file path)
#let chart_path = charts.at("instituicoes_bar", default: none)
#if chart_path != none [
  #align(center)[
    #image(chart_path, width: 80%)
  ]
] else [
  _Chart not available._
]

#v(1cm)

// Data table
#let inst_data = queries.at("instituicoes_por_regiao", default: none)
#if inst_data != none and type(inst_data) == "array" [
  #table(
    columns: (1fr, auto),
    align: (left, right),
    stroke: 0.5pt + gray,
    fill: (_, row) => if row == 0 { rgb("#2E4172").lighten(80%) },
    [*Região*], [*Total*],
    ..inst_data.map(r => ([#r.at("regiao")], [#r.at("total")])).flatten()
  )
]
