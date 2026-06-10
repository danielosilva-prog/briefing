#import "../components/style.typ": *

#import "../components/header.typ": Header

#let Condicionalidade(..args) = {

  let dados = args.at(0)

  // Cores específicas da página
  let corDesigualdadeRacial = rgb("725FA9")
  let corDesigualdadeSocioeconomica = rgb("FA7E17")
  let corReduziu = rgb("118D45")
  let corNaoReduziu = rgb("9A1915")
  let corEstavel = rgb("265793")

  ////////////
  // Verificação da Desigualdade Racial
  // VALORES POSSÍVEIS:
  // Não reduziu a desigualdade racial
  // Reduziu a desigualdade racial
  // Desigualdade racial estável
  // Ausência de dados suficientes

  let reduziuDesigualdadeRacial = if "reduziuDesigualdadeRacial" in dados { dados.at("reduziuDesigualdadeRacial") } else { "Ausência de dados suficientes" }

  let p3PercentualRacial2019 = if "p3PercentualRacial2019" in dados { dados.at("p3PercentualRacial2019") } else { "-%" }
  let p3PercentualRacial2023 = if "p3PercentualRacial2023" in dados { dados.at("p3PercentualRacial2023") } else { "-%" }
  let p3DiferencaPercentualRacial = if "p3DiferencaPercentualRacial" in dados { dados.at("p3DiferencaPercentualRacial") } else { "-%" }
  let exibeDetalheDesigualdadeRacial = p3PercentualRacial2019 != "-%" or p3PercentualRacial2023 != "-%"

  // Verificar se a diferença foi negativa, mas dentro da margem de erro
  //if (p3DiferencaPercentualRacial != "-%" and p3DiferencaPercentualRacial.starts-with("-")) {
    //"Variou a desigualdade socioeconômico DENTRO DA MARGEM DE ERRO"
  //}

  let mapaResultadoDR = (
    "Não reduziu a desigualdade racial": (
      cor: corNaoReduziu,
      conteudo: [#upper("Não reduziu")#linebreak()a desigualdade racial],
      margem: "Não"
    ),

    "Reduziu a desigualdade racial": (
      cor: corReduziu,
      conteudo: [#upper("Reduziu")#linebreak()a desigualdade racial],
      margem: "Sim"
    ),

    "Desigualdade racial estável": (
      cor: corEstavel,
      conteudo: [#upper("Não reduziu") a desigualdade racial, mas dentro da margem de erro],
      margem: "Sim"
    ),
    // Nova opção
    "Variou a desigualdade racial DENTRO DA MARGEM DE ERRO": (
      cor: corEstavel,
      conteudo: [#upper("Variou") a desigualdade racial, mas dentro da margem de erro],
      margem: "Sim"
    ),

    "Ausência de dados suficientes": (
      cor: rgb("999"),
      // conteudo: [#upper("Ausência de")#linebreak()dados suficientes],
      conteudo: [Ausência de#linebreak()dados suficientes],
      margem: ""
    ),
  )

  let corResultadoDesigualdadeRacial = mapaResultadoDR.at(reduziuDesigualdadeRacial).cor
  let conteudoDesigualdadeRacial = mapaResultadoDR.at(reduziuDesigualdadeRacial).conteudo

  let resultadoDesigualdadeRacial = (
    cor: corResultadoDesigualdadeRacial,
    conteudo: conteudoDesigualdadeRacial,
    margem: dados.margemDeErroDesigualdadeRacial
  )

  // Verificar se não foi reduzido, mas está dentro da margem de erro
  if resultadoDesigualdadeRacial.margem == "Sim" and (reduziuDesigualdadeRacial == "Não reduziu a desigualdade racial" or reduziuDesigualdadeRacial == "Reduziu a desigualdade racial") {
    resultadoDesigualdadeRacial = (
      cor: corEstavel,
      conteudo: [#text(size: 10.5pt)[Variou a desigualdade racial #upper("dentro da margem de erro")]],
      margem: "Sim"
    )
  }

  ////////////
  // Verificação da Desigualdade Socioeconômica
  // VALORES POSSÍVEIS:
  // Não reduziu a desigualdade socioeconômica
  // Reduziu a desigualdade socioeconômica
  // Desigualdade socioeconômica estável
  // Ausência de dados suficientes
  let reduziuDesigualdadeSocioeconomica = if "reduziuDesigualdadeSocioeconomica" in dados { dados.at("reduziuDesigualdadeSocioeconomica") } else { "Ausência de dados suficientes" }

  let p3PercentualSocioeconomica2019 = if "p3PercentualSocioeconomica2019" in dados { dados.at("p3PercentualSocioeconomica2019") } else { "-%" }
  let p3PercentualSocioeconomica2023 = if "p3PercentualSocioeconomica2023" in dados { dados.at("p3PercentualSocioeconomica2023") } else { "-%" }
  let p3DiferencaPercentualSocioeconomica = if "p3DiferencaPercentualSocioeconomica" in dados { dados.at("p3DiferencaPercentualSocioeconomica") } else { "-%" }
  let exibeDetalheDesigualdadeSocioeconomica = p3PercentualSocioeconomica2019 != "-%" or p3PercentualSocioeconomica2023 != "-%"

  let mapaResultadoDS = (
    "Não reduziu a desigualdade socioeconômica": (
      cor: corNaoReduziu,
      conteudo: [#upper("Não reduziu") a desigualdade socioeconômica],
      margem: "Não"
    ),

    "Reduziu a desigualdade socioeconômica": (
      cor: corReduziu,
      conteudo: [#upper("Reduziu") a desigualdade socioeconômica],
      margem: "Sim"
    ),

    "Desigualdade socioeconômica estável": (
      cor: corEstavel,
      conteudo: [#upper("Não reduziu") a desigualdade socioeconômica, mas dentro da margem de erro],
      margem: "Sim"
    ),

    "Ausência de dados suficientes": (
      cor: rgb("999"),
      // conteudo: [#upper("Ausência de") dados suficientes],
      conteudo: [Ausência de dados suficientes],
      margem: ""
    ),
  )

  let corResultadoDesigualdadeSocioeconomica = mapaResultadoDS.at(reduziuDesigualdadeSocioeconomica).cor
  let conteudoDesigualdadeSocioeconomica = mapaResultadoDS.at(reduziuDesigualdadeSocioeconomica).conteudo

  let resultadoDesigualdadeSocioeconomica = (
    cor: corResultadoDesigualdadeSocioeconomica,
    conteudo: conteudoDesigualdadeSocioeconomica,
    margem: dados.margemDeErroDesigualdadeSocioeconomica
  )

  // Verificar se não foi reduzido, mas está dentro da margem de erro
  if resultadoDesigualdadeSocioeconomica.margem == "Sim" and (reduziuDesigualdadeSocioeconomica == "Não reduziu a desigualdade socioeconômica" or reduziuDesigualdadeSocioeconomica == "Reduziu a desigualdade socioeconômica") {
    resultadoDesigualdadeSocioeconomica = (
      cor: corEstavel,
      conteudo: [#text(size: 10.5pt)[Variou a desigualdade socioeconômica #upper("dentro da margem de erro")]],
      margem: "Sim"
    )
  }

  // Habilitado
  let habilitadoCondicionalidade = if "habilitadoCondicionalidade" in dados { dados.at("habilitadoCondicionalidade") } else { "Não" }
  let habilitadoCondicionalidadeMotivo = if "habilitadoCondicionalidadeMotivo" in dados { dados.at("habilitadoCondicionalidadeMotivo") } else { "" }
  let habilitadoCondicionalidadeTexto = if habilitadoCondicionalidade == "Sim" { "Habilitado na condicionalidade III" } else { "Inabilitado na condicionalidade III" }
  let corHabilitado = if habilitadoCondicionalidade == "Sim" { corReduziu } else { corNaoReduziu }
  let p3AnoReferencia = if "p3AnoReferencia" in dados { dados.at("p3AnoReferencia") } else { "-" }

  [

    #Header(
      titulo: [A condicionalidade III do VAAR #linebreak() no seu #text(weight: "extrabold")[município em #p3AnoReferencia]],
      municipio: dados.municipio,
      uf: dados.uf,
      textoDoSumario: "A condicionalidade III do VAAR no seu município em " + str(p3AnoReferencia)
    )
  ]
  
  v(.25cm)

  box(
    inset: (top: .5cm, right: .42cm, bottom: .4cm, left: .42cm),
    fill: rgb(pneerqLaranja),
    radius: (top: .5cm, right: .5cm),
    width: 100%,
  )[
    #set text(fill: white, size: sizeBodySmall, tracking: -.01em)
    #strong[#upper[Como analisar]:] se seu município aumentou a aprendizagem adequada do grupo vulnerável, houve redução da desigualdade. Se diminui a taxa de aprendizagem para além da margem de erro, não houve redução da desigualdade.
  ]

  v(.65cm)

  box(
    inset: 0cm,
  )[
    ////////////
    //
    // Desigualdade racial
    //
    ////////////
    ////////////
    #box(
      inset: (left: .5cm, top: -1cm)
    )[
      #place(
        top + left,
        dx: -.5cm,
        dy: -.35cm
      )[
        #box(
          width: .25cm,
          height: .75cm,
          fill: corDesigualdadeRacial
        )
      ]
      #text(weight: "black", size: sizeTotalizerSmall)[#upper("Desigualdade racial")]
    ]

    #v(-.4cm)

    #box(
      fill: bgTabela,
      inset: (x:.5cm, top:.75cm, bottom: .75cm),
      radius: (right:8pt, bottom-left: 8pt),
      width: 100%
    )[
      #if exibeDetalheDesigualdadeRacial {
        align(center)[
          #text(size: sizeBodySmall)[Alunos #strong[pretos, pardos e indígenas] com aprendizagem adequada]
          #v(-.25cm)
          #set par(spacing: .5cm)

          #grid(
            columns: (1fr, 1fr),
            gutter: .5cm,
            align(center)[
              #v(.5cm)
              #if "chartAlunosAprendizagemAdequada" in dados and dados.chartAlunosAprendizagemAdequada != none {
                image("../" + dados.chartAlunosAprendizagemAdequada, height: 4cm, fit: "contain")
              }
            ],
            align(center + horizon)[
              // Variação percentual
              #align(center)[
                #box()[
                  #box(inset: (x:.125cm, top:.35cm, bottom:.25cm))[#text(size: sizeBodySmall)[Variação percentual]]
                  #v(-.5cm)
                  #box(inset: (x:.125cm, top:.35cm, bottom:.25cm))[#text(size: sizeTitlePage, weight: "black", fill: resultadoDesigualdadeRacial.cor)[#dados.p3DiferencaPercentualRacial]]
                ]
              ]

              #v(-.25cm)

              // Margem de erro
              #align(center)[
                #box()[
                  #box(inset: (x:.125cm, top:.35cm, bottom:.25cm))[#text(size: sizeBodySmall)[Dentro da margem de erro?]]
                  #box(fill: resultadoDesigualdadeRacial.cor, inset: (x:.25cm, top:.35cm, bottom:.25cm), radius: 4pt)[#text(fill: txBranco, weight: "extrabold", size: sizeBodySmall)[#resultadoDesigualdadeRacial.margem]]
                ]
              ]

              #v(-.25cm)

              // Resultado
              #box(
                inset: (x:0cm),
              )[
                #box(
                  fill: resultadoDesigualdadeRacial.cor,
                  inset: (x:.5cm, top:.6cm, bottom: .45cm),
                  radius: 8pt
                )[
                  #set par(leading: 10pt, justify: false)
                  #text(fill: txBranco, size: sizeTitle, weight: "extrabold", hyphenate: false)[#resultadoDesigualdadeRacial.conteudo]
                ]
              ]
            ],
          )
        ]
      } else {
        align(center)[
          #box(
            fill: resultadoDesigualdadeRacial.cor,
            inset: (x:.5cm, top:.6cm, bottom: .45cm),
            radius: 8pt

          )[
            #set par(leading: 10pt, justify: false)
            #text(fill: txBranco, size: sizeTitle, weight: "extrabold", hyphenate: false)[#resultadoDesigualdadeRacial.conteudo]
          ]
        ]
      }
    ]
    #v(-0.25cm)

    #box(inset:(right: 1cm, left: 3cm, y: .5cm))[
      #grid(
        columns: (auto, 1fr),
        gutter: 0cm,
        align(center + horizon)[

        ],
        align(center + horizon)[
          #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 15%), radius: 4pt)[
            #box(
              fill: white,
              //stroke: (left:.5pt + black, y:.5pt + black),
              inset: (x:.5cm, top: .5cm, bottom: .35cm),
              radius: (right: 8pt),
              width: 100%
            )[
              #text(size: 8pt)[A margem de erro é definida na Tabela 2 da NOTA TÉCNICA Nº 4/2025/CGEE/DIRED-INEP e varia de acordo com o porte da rede de ensino. Veja no QR Code os valores negativos que são considerados dentro da margem de erro por porte.]
            ]
          ]
        ]
      )

      #place(left + horizon, dx: -2.5cm)[
        #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: 4pt)[
          #box(
            fill: white,
            inset: .25cm,
            radius: 4pt,
            width: 2.5cm
          )[#image("../assets/qrcodes/py/nota-tecnica-4-cond-3.svg", width: 100%, fit: "contain")]
        ]
      ]
    ]


    #v(.5cm)

    ////////////
    //
    // Desigualdade socioeconômica
    //
    ////////////
    #box(
      inset: (left: .5cm)
    )[
      #place(
        top + left,
        dx: -.5cm,
        dy: -.35cm
      )[
        #box(
          width: .25cm,
          height: .75cm,
          fill: corDesigualdadeSocioeconomica
        )
      ]
      #text(weight: "black", size: sizeTotalizerSmall)[#upper("Desigualdade socioeconômica")]
    ]

    #v(-.4cm)

    #box(
      fill: bgTabela,
      inset: (x:.5cm, top:.75cm, bottom: .75cm),
      radius: (right:8pt, bottom-left: 8pt),
      width: 100%
    )[
      #if exibeDetalheDesigualdadeSocioeconomica {
        align(center)[
          #text(size: sizeBodySmall)[Alunos #strong[de baixo NSE] com aprendizagem adequada]
          #v(-.25cm)
          #set par(spacing: .5cm)

          #grid(
            columns: (1fr, 1fr),
            gutter: .5cm,
            align(center)[
              #v(.5cm)
              #if "chartAlunosBaixoNSE" in dados and dados.chartAlunosBaixoNSE != none {
                image("../" + dados.chartAlunosBaixoNSE, height: 4cm, fit: "contain")
              }
            ],
            align(center + horizon)[

              // Variação percentual
              #align(center)[
                #box()[
                  #box(inset: (x:.125cm, top:.35cm, bottom:.25cm))[#text(size: sizeBodySmall)[Variação percentual]]
                  #v(-.5cm)
                  #box(inset: (x:.125cm, top:.35cm, bottom:.25cm))[#text(size: sizeTitlePage, weight: "black", fill: resultadoDesigualdadeSocioeconomica.cor)[#dados.p3DiferencaPercentualSocioeconomica]]
                ]
              ]

              #v(-.25cm)

              // Margem de erro
              #align(center)[
                #box()[
                  #box(inset: (x:.125cm, top:.35cm, bottom:.25cm))[#text(size: sizeBodySmall)[Dentro da margem de erro?]]
                  #box(fill: resultadoDesigualdadeSocioeconomica.cor, inset: (x:.25cm, top:.35cm, bottom:.25cm), radius: 4pt)[#text(fill: txBranco, weight: "extrabold")[#resultadoDesigualdadeSocioeconomica.margem]]
                ]
              ]

              #v(-.25cm)

              // Resultado
              #box(
                inset: (x:0cm),
              )[
                #box(
                  fill: resultadoDesigualdadeSocioeconomica.cor,
                  inset: (x:.5cm, top:.6cm, bottom: .45cm),
                  radius: 8pt
                )[
                  #set par(leading: 10pt, justify: false)
                  #text(fill: txBranco, size: sizeTitle, weight: "extrabold", hyphenate: false)[#resultadoDesigualdadeSocioeconomica.conteudo]
                ]
              ]
            ]
          )
        ]
      } else {
        align(center)[
          #box(
            fill: resultadoDesigualdadeSocioeconomica.cor,
            inset: (x:.5cm, top:.6cm, bottom: .45cm),
            radius: 8pt

          )[
            #set par(leading: 10pt, justify: false)
            #text(fill: txBranco, size: sizeTitle, weight: "extrabold", hyphenate: false)[#resultadoDesigualdadeSocioeconomica.conteudo]
          ]
        ]
      }
    ]

    #v(.25cm)

    ////////////
    //
    // Resultado final
    //
    ////////////
    #align(center)[
      #text(weight: "light", size: sizeTotalizerSmall)[#upper("Resultado final")]
      #v(-.65cm)
      #box(
        fill: corHabilitado,
        inset: (x:.5cm, top: .6cm, bottom: .35cm),
        radius: 8pt,
        width: 100%
      )[
        #set par(leading: 10pt, justify: false)
        #text(weight: "black", fill: txBranco, size: sizeTotalizerSmall)[#upper(habilitadoCondicionalidadeTexto)]
        #if (habilitadoCondicionalidadeMotivo != "") {
          v(-.45cm)
          text(weight: "regular", fill: txBranco, size: sizeBodySmall)[#habilitadoCondicionalidadeMotivo]
        }
      ]
    ]

    #v(-.25cm)

    #align(center)[
      #text(size: sizeCaption, fill: txCinza)[#strong[Fonte:] MEC/FNDE (#p3AnoReferencia)]
    ]
  ]

  if reduziuDesigualdadeRacial != "Ausência de dados suficientes" and reduziuDesigualdadeSocioeconomica != "Ausência de dados suficientes" {
    place(right + horizon, dy:.85cm, dx: .35cm)[
      #box(
        stroke: (y: (thickness: 1pt, paint: rgb("#00000030"), dash: "dashed"), right: (thickness: 1pt, paint: rgb("#00000030"), dash: "dashed")),
        height: 10.8cm,
        width: 2.55cm)[]
    ]
    place(right + horizon, dy:.4cm, dx: .34cm)[
      #box(
        stroke: (top: (thickness: 1pt, paint: rgb("#00000030"), dash: "dashed")),
        width: 1.3cm)[]
    ]
  }
}
