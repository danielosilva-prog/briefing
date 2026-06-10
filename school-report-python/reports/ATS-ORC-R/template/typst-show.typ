// TYP SHOW
#show: Article.with(
  $if(title)$
    title: "$title$",
  $endif$

  $if(params.universidade)$
    universidade: "$params.universidade$",
  $endif$

  $if(params.sigla)$
    sigla: "$params.sigla$",
  $endif$
)
