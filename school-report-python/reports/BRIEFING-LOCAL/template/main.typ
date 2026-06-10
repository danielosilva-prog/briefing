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

#set document(title: title)
#set page(
  paper: "a4",
  margin: (top: 2.4cm, right: 2.0cm, bottom: 4.0cm, left: 3.0cm),
  header: pad(left: -3.0cm, right: -2.0cm, image("assets/header.png", width: 100%)),
  footer: pad(left: -2cm, right: -2cm, image("assets/footer.png", width: 100%)),
)
#set text(font: "Rawline", size: 14pt, lang: "pt")
#set par(leading: 0.4em, spacing: 0.2em, justify: false)

#align(center)[
  #text(size: 14pt, weight: "bold")[#title]
]

#v(0.4cm)

#for section in briefing-sections [
  #block(below: 0.68cm, breakable: false)[
    #text(weight: "bold")[#section.at("numero", default: "") #section.at("titulo", default: "")]

    #v(0.26cm)

    #for indicador in section.at("indicadores", default: ()) [
      #let rotulo = indicador.at("rotulo", default: "")
      #let valor = indicador.at("valor", default: "")
      #let complemento = indicador.at("complemento", default: none)
      #if complemento == none or complemento == "" [
        #strong[#rotulo]: #valor
      ] else [
        #strong[#rotulo]: #valor #complemento
      ]
      #linebreak()
    ]
  ]
]

#if briefing-sections.len() == 0 [
  #text(style: "italic")[Nenhum indicador encontrado para a UF #params.at("uf", default: "").]
]
