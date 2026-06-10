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
#let params = data.at("params", default: (:))
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

#let green = rgb("#1E90FF")
#let contexto = first-row(queries.at("briefing_contexto", default: ()))
#let sections = queries.at("briefing_sections", default: ())
#let briefing-sections = if type(sections) == array {
  sections.sorted(key: item => item.at("ordem", default: 999))
} else {
  ()
}

#let title = template-params.at(
  "title",
  default: metadata.at(
    "title",
    default: contexto.at("titulo", default: "BRIEFING - Visita Ministerial"),
  ),
)

#let render-value(value, bold: false, fill: black) = {
  if type(value) == dictionary {
    if "segments" in value {
      for segment in value.at("segments", default: ()) [
        #text(
          fill: fill,
          weight: if segment.at("bold", default: false) { "bold" } else { "regular" },
        )[#segment.at("text", default: "")]
      ]
    } else {
      text(fill: fill, weight: "bold")[#value.at("prefix", default: "")]
      if value.at("rest", default: "") != "" [
        #text(fill: fill)[ #value.at("rest", default: "")]
      ]
    }
  } else if bold {
    text(fill: fill, weight: "bold")[#value]
  } else {
    text(fill: fill)[#value]
  }
}

#let table-blue = rgb("BFE3EF")

#let render_side_by_side_table(value-lines, estado-lines) = {
  let max-len = if value-lines.len() > estado-lines.len() {
    value-lines.len()
  } else {
    estado-lines.len()
  }
  let cells = range(0, max-len).map(index => (
    table.cell[
      #if index < value-lines.len() {
        render-value(value-lines.at(index))
      }
    ],
    table.cell[
      #if index < estado-lines.len() {
        render-value(estado-lines.at(index), fill: green)
      }
    ],
  )).flatten()

  block(width: 100%)[
    #table(
      columns: (1fr, 1fr),
      stroke: 0.45pt + black,
      inset: 3pt,
      align: (left, left),
      table.header(
        table.cell(fill: table-blue)[#text(weight: "bold")[Município]],
        table.cell(fill: table-blue)[#text(fill: green, weight: "bold")[ESTADO]],
      ),
      ..cells,
    )
  ]
}

#let render-field(line) = {
  let label = line.at("label", default: "")
  let value = line.at("value", default: "")
  let estado = line.at("estado", default: none)
  let value-parts = line.at("value_parts", default: none)
  let estado-parts = line.at("estado_parts", default: none)
  let value-lines = line.at("value_lines", default: none)
  let estado-lines = line.at("estado_lines", default: none)
  let note = line.at("note", default: none)
  let label-bold = line.at("label_bold", default: true)
  let value-bold = line.at("value_bold", default: false)
  let value-newline = line.at("value_newline", default: false)
  let estado-newline = line.at("estado_newline", default: false)
  let estado-separator = line.at("estado_separator", default: " - ")
  let side-by-side = line.at("side_by_side", default: false)

  if label != "" {
    if label-bold {
      strong[#label]
    } else {
      label
    }
    [: ]
    if value-newline {
      linebreak()
    }
  }

  if side-by-side and value-lines != none and estado-lines != none {
    linebreak()
    render_side_by_side_table(value-lines, estado-lines)
  } else if value-lines != none {
    linebreak()
    for item in value-lines [
      #render-value(item, bold: value-bold)
      #linebreak()
    ]
  } else {
    if value-parts != none {
      render-value(value-parts)
    } else {
      render-value(value, bold: value-bold)
    }
  }

  if not side-by-side and estado != none and estado != "" {
    if estado-lines != none {
      if value-lines == none {
        linebreak()
      }
      text(fill: green, weight: "bold")[ESTADO:]
      linebreak()
      for item in estado-lines [
        #render-value(item, bold: true, fill: green)
        #linebreak()
      ]
    } else if estado-newline {
      linebreak()
      if estado-parts != none {
        render-value(estado-parts, fill: green)
      } else {
        text(fill: green, weight: "bold")[#estado]
      }
    } else {
      if estado-parts != none {
        [#estado-separator#render-value(estado-parts, fill: green)]
      } else {
        [#estado-separator#text(fill: green, weight: "bold")[#estado]]
      }
    }
  }
  if note != none and note != "" {
    linebreak()
    text(fill: black, weight: if value-bold { "bold" } else { "regular" })[#note]
  }
}

#let render-campi-table(title, rows) = {
  let cells = rows.map(row => {
    let fill = if row.at("total", default: false) { table-blue } else { none }
    let weight = if row.at("bold", default: false) { "bold" } else { "regular" }
    (
      table.cell(fill: fill)[
        #if row.at("indent", default: false) { h(0.35cm) }
        #text(weight: weight)[#row.at("label", default: "")]
      ],
      table.cell(fill: fill)[
        #text(weight: weight)[#row.at("value", default: "")]
      ],
    )
  }).flatten()

  if rows.len() > 0 [
    #text(weight: "bold")[#title]
    #linebreak()
    #block(width: 9.6cm)[
      #table(
        columns: (1fr, 3.2cm),
        stroke: 0.45pt + black,
        inset: 3pt,
        align: (left, right),
        table.header(
          table.cell(fill: table-blue)[#text(weight: "bold")[Período]],
          table.cell(fill: table-blue)[#text(weight: "bold")[Qtd. Campus]],
        ),
        ..cells,
      )
    ]
  ]
}

#let render-campi-tables(line) = {
  render-campi-table(
    line.at("overview_title", default: "Visão Geral (inclusive Expansão Novo PAC)"),
    line.at("overview_rows", default: ()),
  )
  v(0.42cm)
  render-campi-table(
    line.at("expansion_title", default: "Somente Expansão Novo PAC"),
    line.at("expansion_rows", default: ()),
  )
  linebreak()
}

#let render-if-table(title, rows) = {
  let cells = rows.map(row => {
    let fill = if row.at("total", default: false) { table-blue } else { none }
    let weight = if row.at("bold", default: true) { "bold" } else { "regular" }
    let style = if row.at("italic", default: false) { "italic" } else { "normal" }
    (
      table.cell(fill: fill)[
        #if row.at("indent", default: false) { h(0.45cm) }
        #text(weight: weight, style: style)[#row.at("periodo", default: "")]
      ],
      table.cell(fill: fill)[#text(weight: weight, style: style)[#row.at("funcionando", default: "")]],
      table.cell(fill: fill)[#text(weight: weight, style: style)[#row.at("nao_funcionando", default: "")]],
      table.cell(fill: fill)[#text(weight: weight, style: style)[#row.at("total_if", default: "")]],
    )
  }).flatten()

  if rows.len() > 0 [
    #text(weight: "bold")[#title]
    #linebreak()
    #block(width: 14.2cm)[
      #table(
        columns: (1fr, 3.2cm, 3.9cm, 2.5cm),
        stroke: 0.45pt + black,
        inset: 3pt,
        align: (left, right, right, right),
        table.header(
          table.cell(fill: table-blue)[#text(weight: "bold")[Período]],
          table.cell(fill: table-blue)[#text(weight: "bold")[IF Funcionando]],
          table.cell(fill: table-blue)[#text(weight: "bold")[IF#linebreak()Não funcionando]],
          table.cell(fill: table-blue)[#text(weight: "bold")[Total IF]],
        ),
        ..cells,
      )
    ]
  ]
}

#let render-if-tables(line) = {
  for table-data in line.at("tables", default: ()) [
    #render-if-table(table-data.at("title", default: ""), table-data.at("rows", default: ()))
    #v(0.42cm)
  ]
  linebreak()
}

#let render-line(line) = {
  let kind = line.at("type", default: "field")
  let indent = if line.at("indent", default: false) { 0.6cm } else { 0cm }

  let indented(content) = {
    pad(left: indent)[#content]
  }

  if kind == "spacer" {
    v(if line.at("size", default: "small") == "large" { 0.34cm } else { 0.18cm })
  } else if kind == "campi_table" {
    indented[
      #render-campi-tables(line)
    ]
  } else if kind == "if_table" {
    indented[
      #render-if-tables(line)
    ]
  } else if kind == "text" {
    let content = line.at("text", default: "")
    let color = if line.at("color", default: "black") == "green" { green } else { black }

    indented[
      #text(
        fill: color,
        weight: if line.at("bold", default: false) { "bold" } else { "regular" },
      )[#content]
      #linebreak()
    ]
  } else if kind == "list" {
    for item in line.at("items", default: ()) [
      #indented[
        #item
        #linebreak()
      ]
    ]
  } else {
    indented[
      #render-field(line)
      #linebreak()
    ]
  }
}

#set document(title: title)
#set page(
  paper: "a4",
  margin: (top: 2.4cm, right: 2.0cm, bottom: 4.0cm, left: 3.0cm),
  header: pad(left: -3.0cm, right: -2.0cm, image("assets/header.png", width: 100%)),
  footer: pad(left: -2cm, right: -2cm, image("assets/footer.png", width: 100%)),
)
#set text(font: "Calibri", size: 14pt, lang: "pt")
#set par(leading: 0.65em, spacing: 0.3em, justify: false)

#align(center)[
  #text(size: 16pt, weight: "bold")[#title]
]

#v(0.4cm)

#for section in briefing-sections [
  #let keep-together = section.at("keep_together", default: false)
  #block(below: 0.68cm, breakable: not keep-together)[
    #text(weight: "bold")[#section.at("numero", default: "") #section.at("titulo", default: "")]

    #v(0.24cm)

    #for line in section.at("lines", default: ()) [
      #render-line(line)
    ]
  ]
]

#if briefing-sections.len() == 0 [
  #text(style: "italic")[Nenhum indicador encontrado para o municipio #params.at("cod_ibge", default: "").]
]
