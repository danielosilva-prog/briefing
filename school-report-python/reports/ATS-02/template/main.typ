#import "./typst-template.typ": Article

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
#let template-params = data.at("template_params", default: (:))

#let article-args = (
  ..template-params,
  title: metadata.at("title", default: "Relatório Orçamentário"),
  universidade: template-params.at(
    "universidade",
    default: metadata.at("universidade", default: params.at("universidade", default: "-")),
  ),
  sigla: template-params.at(
    "sigla",
    default: metadata.at("sigla", default: params.at("sigla", default: "-")),
  ),
)

#Article(..article-args)[]
