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

#let contexto = first-row(queries.at("briefing_contexto", default: ()))
#let sections = queries.at("briefing_sections", default: ())

#let default-sections = (
  (
    numero: "1.1",
    titulo: "ESCOLAS CONECTADAS",
    indicadores: (
      (rotulo: "Escolas Conectadas (Nível 4 e 5)", valor: "2.934 (78,8%)"),
    ),
  ),
  (
    numero: "1.2",
    titulo: "ESCOLA EM TEMPO INTEGRAL (2023-2025)",
    indicadores: (
      (rotulo: "Matrículas fomentadas", valor: "29.811"),
      (rotulo: "Valor fomentado", valor: "R$ 186,8 milhões"),
    ),
  ),
)

#let briefing-sections = if type(sections) == array and sections.len() > 0 {
  sections.sorted(key: item => item.at("ordem", default: 999))
} else {
  default-sections
}

#let title = template-params.at(
  "title",
  default: metadata.at(
    "title",
    default: contexto.at("titulo", default: "BRIEFING – Visita Ministerial"),
  ),
)

#set document(title: title)
#set page(
  paper: "a4",
  margin: (top: 2.2cm, right: 2.35cm, bottom: 2cm, left: 2.35cm),
)
#set text(font: "Rawline", size: 11pt, lang: "pt")
#set par(leading: 0.72em, spacing: 0.9em, justify: false)

#align(center)[
  #text(size: 13pt, weight: "bold")[#title]
]

#v(0.9cm)

#for section in briefing-sections [
  #block(below: 0.68cm)[
    #text(weight: "bold")[#section.at("numero", default: "") #section.at("titulo", default: "")]

    #v(0.36cm)

    #for indicador in section.at("indicadores", default: ()) [
      #let rotulo = indicador.at("rotulo", default: "")
      #let valor = indicador.at("valor", default: "")
      #let complemento = indicador.at("complemento", default: none)
      #if complemento == none or complemento == "" [
        #rotulo: #valor
      ] else [
        #rotulo: #valor #complemento
      ]
      #linebreak()
    ]
  ]
]
