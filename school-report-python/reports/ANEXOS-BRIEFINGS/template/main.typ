#let empty-data = (
  metadata: (:),
  params: (:),
  queries: (:),
  charts: (:),
  template_params: (:),
)

#let input-file = if "data_file" in sys.inputs {
  sys.inputs.at("data_file")
} else {
  sys.inputs.at("data", default: none)
}

#let data = if input-file != none {
  json(input-file)
} else {
  empty-data
}

#let queries = data.at("queries", default: (:))

#let first-row(rows) = {
  if type(rows) == array and rows.len() > 0 {
    rows.at(0)
  } else if type(rows) == dictionary {
    rows
  } else {
    (:)
  }
}

#let contexto = first-row(queries.at("contexto", default: ()))
#let obras = queries.at("obras", default: ())

#let blue = rgb("BFE3EF")
#let dark-blue = rgb("1F4E79")
#let light-gray = rgb("F2F2F2")

#let secretaria = contexto.at("secretaria", default: "")
#let uf = contexto.at("uf", default: "")
#let title = contexto.at("titulo", default: "Anexo de Obras")
#let subtitle = contexto.at("subtitulo", default: "")

#let render-obras-table(rows) = {
  let cells = rows.map(row => (
    table.cell[#row.at("instituicao", default: "")],
    table.cell[#row.at("descricao", default: "")],
    table.cell[#row.at("municipio", default: "")],
    table.cell[#row.at("valor_previsto", default: "")],
  )).flatten()

  table(
    columns: (2.7cm, 1fr, 3.1cm, 3.1cm),
    stroke: 0.45pt + black,
    inset: 3.5pt,
    align: (left, left, left, right),
    table.header(
      table.cell(fill: blue)[#text(weight: "bold")[Instituição]],
      table.cell(fill: blue)[#text(weight: "bold")[Descrição do empreendimento]],
      table.cell(fill: blue)[#text(weight: "bold")[Município]],
      table.cell(fill: blue)[#text(weight: "bold")[Valor previsto]],
    ),
    ..cells,
  )
}

#set document(title: title)
#set page(
  paper: "a4",
  flipped: true,
  margin: (top: 1.3cm, right: 1.2cm, bottom: 1.2cm, left: 1.2cm),
  footer: align(right)[
    #text(size: 8pt, fill: rgb("666666"))[
      #secretaria - #uf | #context counter(page).display()
    ]
  ],
)
#set text(font: "Calibri", size: 9.2pt, lang: "pt")
#set par(leading: 0.45em, spacing: 0.2em, justify: false)

#align(center)[
  #text(size: 18pt, weight: "bold")[#title]
  #linebreak()
  #text(size: 12pt, weight: "bold", fill: dark-blue)[#subtitle]
]

#v(0.35cm)

#if obras.len() > 0 [
  #render-obras-table(obras)
] else [
  #text(weight: "bold")[Nenhuma obra encontrada para os parâmetros informados.]
]
