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

#let green = rgb("00B050")
#let contexto = first-row(queries.at("briefing_contexto", default: ()))
#let beau = first-row(queries.at("beau_data", default: ()))
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

#let navy = rgb("142B4A")
#let cyan = rgb("00A6D6")
#let sky = rgb("DDF4FB")
#let green-brand = rgb("00A66A")
#let yellow = rgb("FFD447")
#let ink = rgb("17212B")
#let muted = rgb("607080")
#let pale = rgb("F3F7FA")
#let mock-blue = rgb("1C6EB7")
#let mock-teal = rgb("009DA3")
#let mock-orange = rgb("F18C0E")
#let mock-red = rgb("B0302B")
#let mock-light-teal = rgb("C7EEEF")
#let mock-gray = rgb("6D6E71")

#let pair-value(key, side: "local") = {
  let pair = beau.at(key, default: (local: "—", brasil: "—"))
  pair.at(side, default: "—")
}

#let school-value(key) = {
  let values = beau.at("escolas", default: (:))
  values.at(key, default: "—")
}

#let comparison-row(label, local, brasil, label-fill: pale, label-text: muted) = grid(
  columns: (1fr, 4.65cm),
  gutter: 0cm,
  block(fill: label-fill, radius: (left: 4pt), inset: 11pt, width: 100%)[
    #grid(
      columns: (1fr, auto),
      gutter: 0.2cm,
      align: (left + horizon, right + horizon),
      text(size: 13pt, weight: "regular", fill: label-text)[#label],
      text(size: 14pt, weight: "bold", fill: mock-blue)[#local],
    )
  ],
  block(fill: mock-teal, radius: (right: 4pt), inset: 11pt, width: 100%)[
    #align(right)[#text(size: 14pt, weight: "bold", fill: white)[#brasil]]
  ],
)

#let cnca-row(label, local, brasil, color) = grid(
  columns: (1fr, 2.2cm, 4.65cm),
  gutter: 0cm,
  block(fill: color, radius: (left: 4pt), inset: 7.5pt, width: 100%)[
    #text(size: 16pt, weight: "bold", fill: white)[#label]
  ],
  block(fill: white, inset: 7.5pt, width: 100%)[
    #align(right)[#text(size: 16pt, weight: "bold", fill: muted)[#local]]
  ],
  block(fill: mock-teal, radius: (right: 4pt), inset: 7.5pt, width: 100%)[
    #align(right)[#text(size: 16pt, weight: "bold", fill: white)[#brasil]]
  ],
)

#let year-row(local, brasil) = {
  let parts = local.split(":")
  let year = parts.at(0, default: "—")
  let local-value = if parts.len() > 1 { parts.slice(1).join(":").trim() } else { local }
  let brasil-parts = brasil.split(":")
  let brasil-value = if brasil-parts.len() > 1 { brasil-parts.slice(1).join(":").trim() } else { brasil }
  grid(
    columns: (2.25cm, 1fr, 4.65cm),
    gutter: 0cm,
    block(fill: mock-blue, radius: (left: 4pt), inset: 8pt, width: 100%)[
      #align(center)[#text(size: 13pt, weight: "bold", fill: white)[#year]]
    ],
    block(fill: white, inset: 8pt, width: 100%)[
      #align(right)[#text(size: 12pt, weight: "bold", fill: muted)[#local-value]]
    ],
    block(fill: mock-teal, radius: (right: 4pt), inset: 8pt, width: 100%)[
      #align(right)[#text(size: 12pt, weight: "bold", fill: white)[#brasil-value]]
    ],
  )
}

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

#let render-field(line) = {
  let label = line.at("label", default: "")
  let value = line.at("value", default: "")
  let brasil = line.at("brasil", default: none)
  let value-parts = line.at("value_parts", default: none)
  let brasil-parts = line.at("brasil_parts", default: none)
  let value-lines = line.at("value_lines", default: none)
  let brasil-lines = line.at("brasil_lines", default: none)
  let note = line.at("note", default: none)
  let label-bold = line.at("label_bold", default: true)
  let value-bold = line.at("value_bold", default: false)
  let value-newline = line.at("value_newline", default: false)
  let brasil-newline = line.at("brasil_newline", default: false)
  let brasil-separator = line.at("brasil_separator", default: " - ")

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

  if value-lines != none {
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

  if brasil != none and brasil != "" {
    if brasil-lines != none {
      linebreak()
      text(fill: green, weight: "bold")[BRASIL:]
      linebreak()
      for item in brasil-lines [
        #render-value(item, bold: true, fill: green)
        #linebreak()
      ]
    } else if brasil-newline {
      linebreak()
      if brasil-parts != none {
        render-value(brasil-parts, fill: green)
      } else {
        text(fill: green, weight: "bold")[#brasil]
      }
    } else {
      if brasil-parts != none {
        [#brasil-separator#render-value(brasil-parts, fill: green)]
      } else {
        [#brasil-separator#text(fill: green, weight: "bold")[#brasil]]
      }
    }
  }
  if note != none and note != "" {
    linebreak()
    text(fill: black, weight: if value-bold { "bold" } else { "regular" })[#note]
  }
}

#let table-blue = rgb("BFE3EF")

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
  margin: 0cm,
  background: image("assets/page-1-background.pdf", width: 100%, height: 100%),
)
#set text(font: "Calibri", size: 12pt, lang: "pt", fill: mock-gray)
#set par(leading: 0.45em, spacing: 0.15em, justify: false)

#let at(x, y, width, body) = place(
  top + left,
  dx: x,
  dy: y,
  block(width: width)[#body],
)

#let value-panel(value, width: 4.65cm, height: auto, size: 13pt) = block(
  width: width,
  height: height,
  fill: mock-teal,
  radius: (right: 4pt),
  inset: (x: 7pt, y: 6pt),
)[
  #align(right + horizon)[#text(size: size, weight: "bold", fill: white)[#value]]
]

#let series-parts(value) = {
  let parts = value.split(":")
  (
    year: parts.at(0, default: "—"),
    value: if parts.len() > 1 { parts.slice(1).join(":").trim() } else { value },
  )
}

#let metric-parts(value) = {
  let parts = value.split(" (")
  (
    main: parts.at(0, default: value).trim(),
    detail: if parts.len() > 1 {
      ("(" + parts.slice(1).join(" (").trim()).replace(" matrículas", "")
    } else {
      ""
    },
  )
}

#let highlighted-percent-text(value, base-fill: mock-gray, percent-fill: mock-blue) = {
  for word in value.split(" ") {
    if word.contains("%") {
      text(size: 16pt, weight: "bold", fill: percent-fill)[#word]
    } else {
      text(size: 16pt, weight: "regular", fill: base-fill)[#word]
    }
    h(0.1cm)
  }
}

#let cnca-overlay-row(y, label, local, brasil, fill) = {
  at(1.28cm, y, 7.35cm)[
    #block(width: 100%, fill: fill, radius: (left: 4pt), inset: (x: 7pt, y: 5pt))[
      #text(size: 16pt, weight: "bold", fill: white)[#label]
    ]
  ]
  at(13.23cm, y, 1.42cm)[
    #align(right + horizon)[#text(size: 16pt, weight: "bold", fill: mock-gray)[#local]]
  ]
  at(14.68cm, y, 5.05cm)[#value-panel(brasil, width: 4.95cm, size: 16pt)]
}

#let cnca-number-row(y, label, local, brasil, height: 0.72cm) = {
  at(5.88cm, y, 6.62cm)[
    #block(
      width: 6.62cm,
      height: height,
      fill: mock-blue,
      radius: (left: 4pt),
      inset: (x: 6pt, y: 3pt),
    )[
      #align(left + horizon)[#text(size: 16pt, weight: "bold", fill: white)[#label]]
    ]
  ]
  at(12.5cm, y, 2.18cm)[
    #block(
      width: 100%,
      height: height,
      fill: white,
      inset: (x: 5pt, y: 3pt),
    )[
      #block(width: 100%, height: 100%)[
        #align(center + horizon)[
          #text(size: 16pt, weight: "bold", fill: mock-gray)[#local]
        ]
      ]
    ]
  ]
  at(14.68cm, y, 5.05cm)[
    #block(
      width: 5.5cm,
      height: height,
      fill: mock-teal,
      radius: (right: 4pt),
      inset: (x: 7pt, y: 3pt),
    )[
      #align(right + horizon)[#text(size: 16pt, weight: "bold", fill: white)[#brasil]]
    ]
  ]
}

#let cnca-value-row(y, label, local, brasil, height: 1.0cm) = {
  at(1.28cm, y, 9.4cm)[
    #block(
      width: 100%,
      height: height,
      fill: mock-orange,
      radius: (left: 4pt),
      inset: (x: 10pt, y: 5pt),
    )[
      #align(left + horizon)[#text(size: 16pt, weight: "bold", fill: white)[#label]]
    ]
  ]
  at(10.68cm, y, 4.0cm)[
    #block(
      width: 100%,
      height: height,
      fill: white,
      inset: (x: 5pt, y: 4pt),
    )[
      #block(width: 100%, height: 100%)[
        #align(center + horizon)[
          #text(size: 16pt, weight: "bold", fill: mock-gray)[#local]
        ]
      ]
    ]
  ]
  at(14.68cm, y, 5.05cm)[
    #block(
      width: 5.5cm,
      height: height,
      fill: mock-teal,
      radius: (right: 4pt),
      inset: (x: 7pt, y: 4pt),
    )[
      #align(right + horizon)[
        #text(size: 16pt, weight: "bold", fill: white)[#brasil]
      ]
    ]
  ]
}

#at(1.28cm, 0.38cm, 6.6cm)[
  #text(size: 15pt, weight: "bold", fill: white)[BRIEFING - Visita Ministerial]
]

#at(8.7cm, 0.22cm, 9.15cm)[
  #block(
    width: 100%,
    height: 0.82cm,
    fill: white,
    radius: 5pt,
    inset: (left: 0.5cm),
  )[
    #align(left + horizon)[
      #text(size: 16pt, weight: "bold", fill: mock-blue)[
        #contexto.at("territorio", default: contexto.at("uf", default: "UF"))
      ]
    ]
  ]
]
#at(17.8cm, 0.09cm, 1.52cm)[
  #image("assets/flag.png", width: 100%)
]
#at(16.0cm, 1.66cm, 5.7cm)[
  #align(center)[
    #grid(
      columns: (auto, auto),
      gutter: 0.1cm,
      align: (center + horizon, center + horizon),
      image("assets/brasil-education.png", width: 0.48cm),
      text(size: 16pt, weight: "bold", fill: mock-teal)[BRASIL],
    )
  ]
]

#let schools-panel-height = 2.05cm

#at(6.15cm, 2.2cm, 8.5cm)[
  #block(width: 100%, height: schools-panel-height, fill: pale, radius: (left: 4pt), inset: 8pt)[
    #grid(
      columns: (1fr, auto),
      align: (left + horizon, right + horizon),
      text(size: 16pt)[ESCOLAS#linebreak()CONECTADAS#linebreak()#text(size: 11.5pt)[(NÍVEL 4 E 5)]],
      align(right)[
        #text(size: 16pt, weight: "bold", fill: mock-blue)[#school-value("local_pct")]
        #linebreak()
        #text(size: 16pt)[#school-value("local_count")]
      ],
    )
  ]
]
#at(14.68cm, 2.2cm, 8.5cm)[
  #value-panel(
    [
      #school-value("brasil_pct")
      #linebreak()
      #text(size: 16pt, weight: "regular")[(#school-value("brasil_count"))]
    ],
    width: 5.50cm,
    height: schools-panel-height,
    size: 16pt,
  )
]

#let eti-summary-height = 1.45cm

#at(6.15cm, 4.98cm, 8.5cm)[
  #block(width: 100%, height: eti-summary-height, fill: pale, radius: (left: 4pt), inset: 8pt)[
    #grid(
      columns: (1fr, auto),
      align: (left + horizon, right + horizon),
      text(size: 16pt)[MATRÍCULAS#linebreak()FOMENTADAS],
      align(right + horizon)[
        #text(size: 16.0pt, weight: "bold", fill: mock-blue)[#pair-value("eti_matriculas")]
        #linebreak()
        #text(size: 16.0pt, weight: "regular", fill: mock-gray)[2023-2025]
      ],
    )
  ]
]
#at(14.68cm, 4.98cm, 5.05cm)[
  #value-panel(
    [
      #text(size: 16.0pt, weight: "bold")[#pair-value("eti_matriculas", side: "brasil")]
      #linebreak()
      #text(size: 16.0pt, weight: "regular")[2023-2025]
    ],
    width: 5.5cm,
    height: eti-summary-height,
  )
]
#at(6.15cm, 6.72cm, 8.5cm)[
  #block(width: 100%, height: eti-summary-height, fill: pale, radius: (left: 4pt), inset: 8pt)[
    #grid(
      columns: (1fr, auto),
      align: (left + horizon, right + horizon),
      text(size: 16pt)[VALOR#linebreak()FOMENTADO],
      align(right + horizon)[
        #text(size: 16pt, weight: "bold", fill: mock-blue)[#pair-value("eti_valor")]
        #linebreak()
        #text(size: 16pt, weight: "regular", fill: mock-gray)[2023-2025]
      ],
    )
  ]
]
#at(14.68cm, 6.72cm, 5.05cm)[
  #value-panel(
    [
      #text(size: 16.0pt, weight: "bold")[#pair-value("eti_valor", side: "brasil")]
      #linebreak()
      #text(size: 16pt, weight: "regular")[2023-2025]
    ],
    width: 5.5cm,
    height: eti-summary-height,
  )
]

#at(1.28cm, 8.5cm, 4.25cm)[
  #text(size: 16pt)[\*2026 com dado mais recente de 2025; 2026 ainda não publicado.]
]
#at(6.15cm, 8.45cm, 4cm)[#text(size: 16pt)[MATRÍCULAS]]
#let local-series = beau.at("eti_serie", default: (local: ("—",))).at("local", default: ("—",))
#let brasil-series = beau.at("eti_serie", default: (brasil: ("—",))).at("brasil", default: ("—",))
#let series-row-height = 0.82cm
#for index in range(0, local-series.len()) {
  let local = series-parts(local-series.at(index))
  let brasil = series-parts(brasil-series.at(index, default: "—"))
  let local-metric = metric-parts(local.value)
  let brasil-metric = metric-parts(brasil.value)
  let y = 9.0cm + index * 1.22cm
  at(6.15cm, y, 2.25cm)[
    #block(width: 100%, height: series-row-height, fill: mock-blue, radius: (left: 4pt), inset: (x: 6pt, y: 5pt))[
      #align(center)[#text(size: 16pt, weight: "bold", fill: white)[#local.year]]
    ]
  ]
  at(8.4cm, y, 6.28cm)[
    #block(
      width: 100%,
      height: series-row-height,
      fill: white,
      stroke: 0.25pt + rgb("E4E4E4"),
      inset: (x: 7pt, y: 5pt),
    )[
      #align(right + horizon)[
        #text(size: 16pt, weight: "bold", fill: mock-gray)[#local-metric.main]
        #if local-metric.detail != "" {
          h(0.12cm)
          text(size: 16pt, weight: "regular", fill: mock-gray)[#local-metric.detail]
        }
      ]
    ]
  ]
  at(14.68cm, y, 5.05cm)[
    #block(
      width: 5.5cm,
      height: series-row-height,
      fill: mock-teal,
      radius: (right: 4pt),
      inset: (x: 7pt, y: 5pt),
    )[
      #align(right + horizon)[
        #text(size: 16pt, weight: "bold", fill: white)[#brasil-metric.main]
        #if brasil-metric.detail != "" {
          h(0.12cm)
          text(size: 16pt, weight: "regular", fill: white)[#brasil-metric.detail]
        }
      ]
    ]
  ]
}

#at(5.88cm, 14.05cm, 3cm)[#text(size: 16pt)[NÚMEROS]]
#cnca-number-row(14.6cm, "Cantinhos de Leitura", pair-value("cnca_cantinhos"), pair-value("cnca_cantinhos", side: "brasil"))
#cnca-number-row(15.45cm, "Escolas Apoiadas", pair-value("cnca_escolas"), pair-value("cnca_escolas", side: "brasil"))
#cnca-number-row(16.30cm, "Articuladores RENALFA\n(2025)", pair-value("cnca_articuladores"), pair-value("cnca_articuladores", side: "brasil"), height: 1.18cm)

#at(1.28cm, 17.58cm, 3cm)[#text(size: 16pt)[VALORES]]
#cnca-value-row(18.15cm, "Valor Investido em Cantinhos da\nLeitura", pair-value("cnca_valor_cantinhos"), pair-value("cnca_valor_cantinhos", side: "brasil"), height: 1.24cm)
#cnca-value-row(19.6cm, "Repasse para Articuladores\nRENALFA", pair-value("cnca_valor_articuladores"), pair-value("cnca_valor_articuladores", side: "brasil"), height: 1.24cm)
#cnca-value-row(21.05cm, "Valor empenhado para aquisição\nde materiais", pair-value("cnca_materiais"), pair-value("cnca_materiais", side: "brasil"), height: 1.24cm)
#cnca-value-row(22.5cm, "Valor empenhado para formação\nde profissionais da educação", pair-value("cnca_formacao"), pair-value("cnca_formacao", side: "brasil"), height: 1.38cm)
#cnca-value-row(24.1cm, "Total Investido", pair-value("cnca_total"), pair-value("cnca_total", side: "brasil"), height: 0.92cm)

#let ica-panel-height = 1.72cm

#at(1.28cm, 25.55cm, 13.4cm)[
  #block(
    width: 100%,
    height: ica-panel-height,
    fill: pale,
    radius: (left: 4pt),
    inset: 0pt,
  )[]
]
#at(1.62cm, 25.79cm, 1.05cm)[
  #image("assets/graduation-cap.png", width: 100%)
]
#at(2.85cm, 25.72cm, 4.45cm)[
  #block(width: 100%, height: 1.4cm)[
    #align(left + horizon)[
      #text(size: 16pt, fill: mock-gray)[
        INDICADOR DE
        #linebreak()
        ALFABETIZAÇÃO (ICA)
      ]
    ]
  ]
]
#at(7.3cm, 25.62cm, 7.38cm)[
  #block(width: 100%, height: 1.58cm, inset: (x: 6pt, y: 4pt))[
    #align(center + horizon)[
      #highlighted-percent-text(pair-value("ica"))
    ]
  ]
]
#at(14.68cm, 25.55cm, 5.05cm)[
  #block(
    width: 5.5cm,
    height: ica-panel-height,
    fill: mock-teal,
    radius: (right: 4pt),
    inset: (x: 8pt, y: 5pt),
  )[
    #align(center + horizon)[
      #highlighted-percent-text(
        pair-value("ica", side: "brasil"),
        base-fill: white,
        percent-fill: white,
      )
    ]
  ]
]
#at(1.9cm, 27.85cm, 14cm)[#text(size: 16pt)[\*Em 2023, o SAEB era usado como métrica]]

#pagebreak()

#set page(
  paper: "a4",
  margin: (top: 1.4cm, right: 1.5cm, bottom: 1.4cm, left: 1.5cm),
  fill: white,
  background: none,
  header: align(right)[#text(size: 7pt, weight: "bold", fill: navy)[#contexto.at("territorio", default: contexto.at("uf", default: "UF"))]],
  footer: align(right)[#text(size: 7pt, fill: muted)[#context counter(page).display()]],
)
#set text(size: 10.5pt)
#set par(leading: 0.55em, spacing: 0.24em)

#for section in briefing-sections.filter(section => section.at("ordem", default: 0) >= 4) [
  #let keep-together = section.at("keep_together", default: false)
  #block(below: 0.55cm, breakable: not keep-together)[
    #text(size: 11pt, weight: "bold", fill: navy)[#section.at("numero", default: "") #section.at("titulo", default: "")]
    #v(0.16cm)
    #for line in section.at("lines", default: ()) [
      #render-line(line)
    ]
  ]
]

#if briefing-sections.len() == 0 [
  #text(style: "italic")[Nenhum indicador encontrado para esta UF.]
]
