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

#let metadata = data.at("metadata", default: (:))
#let queries = data.at("queries", default: (:))
#let template-params = data.at("template_params", default: (:))

#let first-row(rows) = {
  if type(rows) == array and rows.len() > 0 {
    rows.at(0)
  } else if type(rows) == dictionary {
    rows
  } else {
    (:)
  }
}

#let contexto = first-row(queries.at("flyer_contexto", default: ()))
#let resumo = queries.at("resumo_novopac", default: ())
#let programas = queries.at("programas_mec", default: ())
#let obras = queries.at("obras", default: ())

#let title = template-params.at(
  "title",
  default: metadata.at("title", default: contexto.at("titulo", default: "Novo PAC e Programas do MEC")),
)

#let blue = rgb("BFE3EF")
#let dark-blue = rgb("1F4E79")

#let render-resumo-table(rows) = {
  let cells = rows.map(row => {
    let fill = if row.at("total", default: false) {
      dark-blue
    } else if row.at("subtotal", default: false) {
      blue
    } else {
      none
    }
    let text-fill = if row.at("total", default: false) { white } else { black }
    let weight = if row.at("subtotal", default: false) or row.at("total", default: false) {
      "bold"
    } else {
      "regular"
    }
    (
      table.cell(fill: fill)[#text(fill: text-fill, weight: weight)[#row.at("label", default: "")]],
      table.cell(fill: fill)[#text(fill: text-fill, weight: weight)[#row.at("value", default: "")]],
      if row.at("skip_quantity", default: false) {
        ()
      } else {
        (
          table.cell(
            fill: fill,
            rowspan: row.at("quantity_rowspan", default: 1),
          )[#text(fill: text-fill, weight: weight)[#row.at("quantity", default: "")]],
        )
      },
    )
  }).flatten()

  table(
    columns: (1fr, 4.2cm, 3.2cm),
    stroke: 0.45pt + black,
    inset: 3.5pt,
    align: (left, right, center),
    table.header(
      table.cell(fill: blue)[#text(weight: "bold")[Resumo Geral]],
      table.cell(fill: blue)[#text(weight: "bold")[Valor]],
      table.cell(fill: blue)[#text(weight: "bold")[Quantidade]],
    ),
    ..cells,
  )
}

#let render-programas(rows) = {
  for row in rows [
    #text(weight: "bold")[#row.at("label", default: ""): ]
    #row.at("value", default: "")
    #linebreak()
  ]
}

#let render-obras-table(rows) = {
  if rows.len() > 0 [
    #text(size: 13pt, weight: "bold")[Novo Pac - Lista de Obras]
    #v(0.1cm)
    #let cells = rows.map(row => (
      table.cell[#row.at("acao", default: "")],
      table.cell[#row.at("tipo_sigla", default: "")],
      table.cell[#row.at("municipio", default: "")],
      table.cell[#row.at("obra", default: "")],
    )).flatten()
    #table(
      columns: (2.7cm, 2.6cm, 3.0cm, 1fr),
      stroke: 0.35pt + black,
      inset: 3pt,
      table.header(
        table.cell(fill: blue)[#text(weight: "bold")[Ação]],
        table.cell(fill: blue)[#text(weight: "bold")[Tipo/Sigla (\*)]],
        table.cell(fill: blue)[#text(weight: "bold")[Município]],
        table.cell(fill: blue)[#text(weight: "bold")[Obra]],
      ),
      ..cells,
    )
  ]
}

#set document(title: title)
#set page(
  paper: "a4",
  margin: (top: 1.4cm, right: 1.4cm, bottom: 1.4cm, left: 1.4cm),
)
#set text(font: "Calibri", size: 10.5pt, lang: "pt")
#set par(leading: 0.45em, spacing: 0.2em, justify: false)

#align(center)[
  #text(size: 18pt, weight: "bold")[#title]
]

#v(0.35cm)

#render-resumo-table(resumo)

#v(0.45cm)

#text(size: 13pt, weight: "bold")[Programas do MEC]
#v(0.1cm)
#render-programas(programas)

#if obras.len() > 0 [
  #v(0.45cm)
  #render-obras-table(obras)
]
