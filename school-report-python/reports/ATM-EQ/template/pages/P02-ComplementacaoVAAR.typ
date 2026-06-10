#import "../components/style.typ": *
#import "../components/header.typ": Header
#import "../components/footer.typ": Footer

#let status-icon(status) = {
  v(-.2cm)
  if status == "true" or status == true {
    image("../assets/icons/true.svg", width: .4cm)
  } else if status == "false" or status == false {
    image("../assets/icons/false.svg", width: .4cm)
  } else {
    text(size: sizeBody * .75, fill: txCinza)[Pendente]
  }
}

#let condicionalidade-item(titulo, atendimento) = {
  let atendimentoNum = calc.round(float(atendimento))
  let naoAtendimentoNum = 100 - atendimentoNum
  let atendimentoTexto = str(atendimentoNum) + "%"
  let naoAtendimentoTexto = str(naoAtendimentoNum) + "%"
  align(center + horizon)[
    #set par(justify: false, leading: .8em)
    #grid(
      columns: (1fr, 1fr),
      inset: (y: .125cm),
      gutter: .25cm,
      align(right)[
        #text(size: 7pt)[#titulo]
      ],
      grid(
        columns: (atendimentoNum * 1%, naoAtendimentoNum * 1%),
        gutter: 0cm,
        align(left)[#box(fill: txVerdeEscuro, width: 100%, height: .6cm, inset: (left: .125cm, top: .125cm, bottom: .04cm))[#text(fill: white, weight: "black", size: 7pt)[#atendimentoTexto]]],
        align(right)[#box(fill: rgb("FF0000"), width: 100%, height: .6cm, inset: (right: .0625cm, top: .125cm, bottom: .04cm))[#text(fill: white, weight: "black", size: 7pt)[#naoAtendimentoTexto]]]
      )
    )
  ]
}

#let ComplementacaoVAAR(..args) = {
  let dados = args.at(0)
  let condAnoReferencia = dados.at("condAnoReferencia", default: none)
  let condAnoReferenciaTexto = if condAnoReferencia == none or condAnoReferencia == "" or condAnoReferencia == "-" {
    "-"
  } else {
    str(condAnoReferencia)
  }
  let codProximoAnoReferencia = if condAnoReferenciaTexto == "-" {
    "-"
  } else {
    str(int(condAnoReferenciaTexto) + 1)
  }
  [
    #Header(
      titulo: [A complementação VAAR/FUNDEB #linebreak()no #text(weight: "extrabold")[seu município em 2026]],
      municipio: dados.municipio,
      uf: dados.uf,
      textoDoSumario: "A complementação VAAR/FUNDEB no seu município em 2026"
    )

    #v(-.25cm)

    #grid(
      columns: (74%, 25%),
      inset: 0cm,
      gutter: 1%,
      align(right)[
        #grid(
          columns: (26%, 24%, 46%),
          gutter: 1%,
          inset: (top: 1.3cm, right: 0cm, bottom: 0cm, left: 0cm),
          align(left + top)[
            #text(weight: 400, size: sizeBodySmall)[PIB _per capita_ (#dados.p2PibPerCapitaAno)] \
            #text(dados.p2PibPerCapita, weight: weightTitle, size: sizeTitle)
            #v(-.25cm)
            #text(weight: 400, size: sizeCaption, fill: rgb(txCinza))[#strong[Fonte:] IBGE (#dados.p2PibPerCapitaAno)]
          ],
          align(left + top)[
            #text(weight: 400, size: sizeBodySmall)[Habitantes (#dados.p2NumeroHabitantesAno)] \
            #text(dados.p2NumeroHabitantes, weight: weightTitle, size: sizeTitle)
            #v(-.25cm)
            #text(weight: 400, size: sizeCaption, fill: rgb(txCinza))[#strong[Fonte:] IBGE (#dados.p2NumeroHabitantesAno)]
          ],
          align(left + top)[
            #set par(justify: false, leading: 6pt)
            #v(-0.68cm)
            #box(
              fill: bgTabela,
              inset: (top: 10pt, x: 10pt, bottom: 6pt),
              radius: 2pt,
              width: 100%
            )[
              #grid(
                columns: (40%, 60%),
                gutter: 10pt,
                inset: (top: 0cm, right: 0cm, bottom: 0cm, left: 0cm),
                align(left + top)[
                  #text(weight: 400, size: sizeBody * 0.6)[População#linebreak()quilombola #if dados.populacaoQuilombolaAno != "-" [(#dados.populacaoQuilombolaAno)]:] \
                  #v(-.25cm)
                  #text(dados.populacaoQuilombola, weight: weightTitle, size: sizeTitle)
                  #v(-.35cm)
                  #text(weight: 400, size: sizeCaption, fill: rgb(txCinza))[#strong[Fonte:] IBGE (#dados.populacaoQuilombolaAno)]
                ],
                align(left + top)[
                  #text(weight: 400, size: sizeBody * 0.6)[Comunidades quilombolas certificadas #if dados.comunidadesQuilombolasAno != "-" [(#dados.comunidadesQuilombolasAno)]:] \
                  #v(-.25cm)
                  #text(dados.comunidadesQuilombolas, weight: weightTitle, size: sizeTitle)
                  #v(-.35cm)
                  #text(weight: 400, size: sizeCaption, fill: rgb(txCinza))[#strong[Fonte:] Fundação Cultural Palmares (2025)]
                ]
              )
            ]
          ]
        )
      ],
      align(left + horizon)[
        #if "chartMapaMunicipio" in dados and dados.chartMapaMunicipio != none {
          image("../" + dados.chartMapaMunicipio, height: 3.8cm)
        }
      ],
    )

    #v(-.5cm)

    #grid(
      columns: (1fr, 1fr),
      gutter: 2%,
      inset: 0cm,

      align(center + top)[
        #v(.35cm)
        #set par(leading: .8em)
        #text(size: sizeChartTitle, fill: txCinza, weight: weightTitleChart)[Valor previsto da complementação VAAR #linebreak() em seu município em #dados.p2AnoReferencia:] \
        #v(.1cm)
        #text(size: sizeTotalizerBig, fill: pneerqMarrom, weight: weightSubtitle)[#format-currency(dados.p2ValorComplementacaoVAARAnoReferencia)]
         \ #set par(justify: false, leading: .7em)
        #text(size: sizeBodySmall, weight: 400)[Valor médio previsto do VAAR#linebreak()por ente federativo em seu estado (#dados.p2ValorComplementacaoVAARMediaUFAno):]
        #v(-.15cm)
        #text(weight: "black")[#dados.p2ValorComplementacaoVAARMediaUF]
        #v(-.05cm)
        #align(center)[
          #text(
            size: sizeCaption,
            fill: rgb(txCinza)
          )[
            #strong[Fonte:] MEC/FNDE (#dados.p2AnoReferencia)
          ]
        ]
      ],

      align(center + top)[
        #box(
          fill: white,
          inset: (top: .32cm, right: .45cm, bottom: .16cm, left: .45cm),
        )[
          #align(center)[
            #text(
              "Valores previstos do VAAR pelo município",
              size: sizeChartTitle,
              fill: txCinza,
              weight: weightTitleChart,
            )
          ]
          #v(-.25cm)
          #if dados.chartVaarMunicipio != none {
            image("../" + dados.chartVaarMunicipio, height: 2.9cm, fit: "contain")
          }
          #v(-.45cm)
          #align(center)[
            #text(
              size: sizeCaption,
              fill: rgb(txCinza),
              hyphenate: false
            )[
            #strong[Fonte:] MEC/FNDE (2023-2025)
            ]
          ]
        ]
      ]
    )

    #v(-.125cm)

    #align(center)[
      #box(
        fill: bgTabela,
        inset: (top: .5cm, right: .62cm, bottom: .3cm, left: .62cm),
        radius: (top-right: 20pt, bottom-left: 20pt),
        width: 13cm
      )[

        #text(
          weight: weightTitle,
          fill: pneerqMarrom,
          size: sizeBody * .9
        )[Condicionalidades e indicadores em #dados.municipio\-#dados.uf (#codProximoAnoReferencia)]

        #v(-.125cm)

        #align(left)[
          #grid(
            columns: (auto, 1fr),
            gutter: .25cm,
            row-gutter: 12pt,
            status-icon(dados.condSelecaoDiretor), text(size: 9pt)[Seleção por critérios técnicos do cargo de diretor escolar],
            status-icon(dados.condParticipacaoSaeb), text(size: 9pt)[Participação (>=80%) no Sistema de Avaliação da Educação Básica - Saeb],
            status-icon(dados.condReducaoDesigualdades), text(size: 9pt)[Redução de desigualdades de aprendizagem],
            status-icon(dados.condRegulamentacaoIcms), text(size: 9pt)[Regulamentação do ICMS Educacional no estado],
            status-icon(dados.condReferenciaisBncc), text(size: 9pt)[Referenciais curriculares alinhados à Base Nacional Comum Curricular],
            status-icon(dados.condAvancoAtendimento), text(size: 9pt)[Avanço no indicador de atendimento],
            status-icon(dados.condAvancoAprendizagem), text(size: 9pt)[Avanço no indicador de aprendizagem],
          )
        ]
      ]
    ]

    #grid(
      columns: (48%, 48%),
      gutter: 4%,
      inset: 0cm,

      align(center + top)[
        #box(
          fill: white,
          inset: (top: .28cm, right: 0cm, bottom: .1cm, left: 0cm),
        )[
          #align(center)[
            #text(
              "Cumprimento das condicionalidades\n pelos entes federativos no Brasil (" + condAnoReferenciaTexto + ")",
              size: sizeBody * .8,
              fill: txCinza,
              weight: weightSubtitle,
            )
          ]
          #v(-.25cm)

          #condicionalidade-item("Seleção por critérios técnicos do cargo de diretor escolar", dados.percentualCumprimentoCondicionalidade1Brasil)
          #v(-.7cm)
          #condicionalidade-item("Participação (>=80%) no Sistema de Avaliação da Educação Básica - Saeb", dados.percentualCumprimentoCondicionalidade2Brasil)
          #v(-.7cm)
          #condicionalidade-item("Redução de desigualdades de aprendizagem", dados.percentualCumprimentoCondicionalidade3Brasil)
          #v(-.7cm)
          #condicionalidade-item("Regulamentação do ICMS Educacional no estado", dados.percentualCumprimentoCondicionalidade4Brasil)
          #v(-.7cm)
          #condicionalidade-item("Referenciais curriculares alinhados à Base Nacional Comum Curricular", dados.percentualCumprimentoCondicionalidade5Brasil)
        ]
      ],

      align(right + top)[
        #box(
          fill: white,
          inset: (top: .28cm, right: 0cm, bottom: .1cm, left: 0cm),
        )[
          #align(center)[
            #text(
              "Cumprimento das condicionalidades\n pelos entes federativos na UF (" + condAnoReferenciaTexto + ")",
              size: sizeBody * .8,
              fill: txCinza,
              weight: weightSubtitle,
            )
          ]
          #v(-.25cm)

          #condicionalidade-item("Seleção por critérios técnicos do cargo de diretor escolar", dados.percentualCumprimentoCondicionalidade1UF)
          #v(-.7cm)
          #condicionalidade-item("Participação (>=80%) no Sistema de Avaliação da Educação Básica - Saeb", dados.percentualCumprimentoCondicionalidade2UF)
          #v(-.7cm)
          #condicionalidade-item("Redução de desigualdades de aprendizagem", dados.percentualCumprimentoCondicionalidade3UF)
          #v(-.7cm)
          #condicionalidade-item("Regulamentação do ICMS Educacional no estado", dados.percentualCumprimentoCondicionalidade4UF)
          #v(-.7cm)
          #condicionalidade-item("Referenciais curriculares alinhados à Base Nacional Comum Curricular", dados.percentualCumprimentoCondicionalidade5UF)
        ]
      ],
    )

    #v(-12pt)

    #align(center)[
      #chart-legend((
        (color:  txVerdeEscuro, label: "Cumprido"),
        (color: "FF0000", label: "Não cumprido"),
      ))
    ]

    #v(0pt)

    #align(center)[
      #text(
        size: sizeCaption,
        fill: rgb(txCinza)
      )[
        #strong[Fonte:] MEC/FNDE (#condAnoReferenciaTexto)
      ]
    ]

    #box(
      inset: (top: .5cm, right: .42cm, bottom: .4cm, left: .42cm),
      fill: rgb(pneerqLaranja),
      radius: (bottom: .5cm, right: .5cm),
      width: 100%,
    )[
      #set text(fill: white, size: sizeBodySmall, tracking: -.01em)
      #text(weight: weightTitle, size: sizeBody * .95)[Como funciona o cálculo da Condicionalidade III do VAAR?]

      #v(-2pt)

      A condicionalidade é avaliada em duas dimensões: desempenho de alunos pretos, pardos e indígenas (PPI) e desempenho dos alunos de menor nível socioeconômico (NSE) em cada rede de ensino.

      Para cumprir a condicionalidade e se habilitar no VAAR, é necessário melhorar, simultaneamente, a taxa de aprendizagem adequada nos dois grupos de estudantes em comparação com a edição anterior do Saeb. Melhorar apenas um dos grupos não é suficiente.
    ]
  ]
}
