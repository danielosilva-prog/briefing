#import "../components/style.typ": *

#import "../components/header.typ": Header

#let DiagnosticoCensoEscolar(..args) = {
  let dados = args.at(0)
  let normalize-infra-percent = value => {
    let text-value = str(value)
    if text-value == "100,0%" {
      "100%"
    } else {
      text-value
    }
  }

  [
    #Header(
      titulo: [#text(weight: "extrabold")[Diagnóstico] para compreensão #linebreak() de desigualdades raciais],
      municipio: dados.municipio,
      uf: dados.uf,
      bgColor: rgb("0C8C59"),
      esconderDoSumario: true,
    )

    #v(-6pt)

    #align(center)[

      #text(
        weight: weightSubtitle,
        size: sizeBody,
        fill: rgb(txCinza),
      )[#upper[Docentes com formação adequada por perfil da escola]]

      #v(gap - 12pt)

      #if "chartNivelFormacaoProfessores" in dados and dados.chartNivelFormacaoProfessores != none {
        image("../" + dados.chartNivelFormacaoProfessores, height: 5.5cm)
      }

      #v(-6pt)

      #place(top + right, dx: 1cm, dy: 4cm)[

        #move(dx: -.5cm)[
          #image("../assets/icons/warning.svg", height: .6cm)
        ]

        #v(-.35cm)

        #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: (left: .25cm))[
          #box(
            inset: (top: .5cm, bottom: .35cm, right: .5cm, left: .125cm),
            fill: rgb("fff5c2"),
            width: 3.9cm,
            radius: (left: .25cm)
          )[
            #set par(justify: false, leading: .8em)
            #text(
              size: sizeCaption
            )[
              Caso a rede não tenha escolas de uma determi-nada classificação, o gráfico mostrará apenas “-“. Isso não significa 0% de formação, mas que não há escolas com este perfil.
            ]
          ]
        ]
      ]

      #align(center)[
        #text(
          size: sizeCaption,
          fill: rgb(txCinza),
          tracking: -.2pt
        )[
          #strong[Fonte:] Inep, Censo Escolar e Indicador de Adequação da Formação Docente (2024). Dados tratados por MEC/SEGAPE e MEC/SECADI.  #linebreak()
          #strong[Nota:] Consideraram-se apenas escolas municipais em funcionamento. PPI refere-se a estudantes pretos, pardos e indígenas. As escolas foram classificadas de forma mutuamente exclusiva em escolas quilombolas, escolas com 60% ou mais de estudantes PPI e escolas com maioria não PPI, desconsiderando-se os estudantes sem declaração de raça/cor.
        ]
      ]
      #v(-.25cm)

      #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: .25cm)[
        #box(
          //stroke: 1pt + txCinza,
          inset: (top: .35cm, x: .35cm, bottom: .25cm),
          radius: .25cm,
          fill: white
        )[
          #place(top + left, dx: -.8cm, dy: -.15cm)[
            #image("../assets/icons/info.svg", height: .6cm)
          ]
          #text(size: sizeCaption)[
            #strong[Escolas maioria PPI:] são aquelas em que 60% ou mais dos estudantes são pretos, pardos ou indígenas.
            #linebreak()
            #strong[Escolas maioria não-PPI:] são aquelas em que 60% ou mais dos estudantes não são pretos, pardos ou indígenas.
          ]
        ]
      ]

      #v(gap - 12pt)
      
      #box(
        stroke: .75pt + txCinza,
        inset: (top: 12pt, x: 8pt, bottom: 7pt),
      )[
        #text(
          weight: weightSubtitle,
          size: sizeTitle,
          fill: rgb(txCinza),
        )[#upper[Dados do Censo Escolar - 2024]]
      ]


      #text(
        weight: weightSubtitle,
        size: sizeBody,
        fill: rgb(txCinza),
      )[#upper[Taxa média de aprovação no ensino fundamental por perfil das escolas]]

      #v(-10pt)

      #if "chartTaxaRendimento" in dados and dados.chartTaxaRendimento != none {
        image("../" + dados.chartTaxaRendimento, height: 4.2cm)
      }

      #v(-6pt)

      #place(bottom + right, dx: 1cm, dy: -10.8cm)[

        #move(dx: -.5cm)[
          #image("../assets/icons/warning.svg", height: .6cm)
        ]

        #v(-.35cm)

        #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: (left: .25cm))[
          #box(
            inset: (top: .5cm, bottom: .35cm, right: .5cm, left: .125cm),
            fill: rgb("#fff5c2"),
            width: 3.9cm,
            radius: (left: .25cm)
          )[
            #set par(justify: false, leading: .8em)
            #text(
              size: sizeCaption
            )[
              Caso a rede não tenha escolas de uma determi-nada classificação, o gráfico mostrará apenas “-“. Isso não significa 0% de formação, mas que não há escolas com este perfil.
            ]
          ]
        ]
      ]

      #align(center)[
        #text(
          size: sizeCaption,
          fill: rgb(txCinza),
          tracking: -.2pt
        )[
          #strong[Fonte:] Inep, Censo Escolar e Rendimento Escolar (2024). Dados tratados por MEC/SEGAPE e MEC/SECADI. #linebreak()
          #strong[Nota:] Consideraram-se apenas escolas municipais em funcionamento. PPI refere-se a estudantes pretos, pardos e indígenas. As escolas foram classificadas de forma mutuamente exclusiva em escolas quilombolas, escolas com 60% ou mais de estudantes PPI e escolas com maioria não PPI, desconsiderando-se os estudantes sem declaração de raça/cor nesse cálculo., desconsiderando-se os estudantes sem declaração de raça/cor.
        ]
      ]

      #v(gap - 8pt)

      #text(
        weight: weightSubtitle,
        size: sizeBody*.91,
        fill: rgb(txCinza),
        tracking: -.2pt
      )[#upper[Estudantes em escolas com infraestrutura básica adequada, por raça/cor e por escolas quilombolas]]

      #v(gap - 18pt)

      #if "tabelaInfraestruturaBasica" in dados and dados.tabelaInfraestruturaBasica.len() > 0 {
        let infraRows = dados.tabelaInfraestruturaBasica
        let infraCells = infraRows.map(row => (
          [#row.at("indicador", default: "-")],
          [#normalize-infra-percent(row.at("percentualBrancaFmt", default: "-"))],
          [#normalize-infra-percent(row.at("percentualPretaFmt", default: "-"))],
          [#normalize-infra-percent(row.at("percentualPardaFmt", default: "-"))],
          [#normalize-infra-percent(row.at("percentualAmarelaFmt", default: "-"))],
          [#normalize-infra-percent(row.at("percentualIndigenaFmt", default: "-"))],
          [#normalize-infra-percent(row.at("percentualNaoDeclaradaFmt", default: "-"))],
          [#normalize-infra-percent(row.at("percentualQuilombolaFmt", default: "-"))],
        )).flatten()

        set table(
          align: (x, y) => if x == 0 { left } else { right },
          stroke: none,
          fill: (x, y) =>
            if calc.rem(y, 2) != 0 {
              rgb("F2F2F2")
            } else {
              rgb("fff")
            }
        )
        set table.cell(inset: (top: 8pt, x: 8pt, bottom: 6pt))
        show table.cell: text.with(size: sizeBody * .7)
        show table.cell.where(y: 0): text.with(weight: weightTitle, size: sizeBody, fill: black)
        show table.cell.where(x: 0): text.with(weight: "regular", size: sizeBody, fill: black)
        show table.cell: text.with(weight: "black", fill: txCinzaEscuro)

        table(
          columns: (auto, auto, auto, auto, auto, auto, auto, auto),
          table.header(
            [Indicador],
            [Branca],
            [Preta],
            [Parda],
            [Amarela],
            [Indígena],
            [Não declarada],
            [Quilombola],
          ),
          ..infraCells,
        )

        v(-12pt)

        align(center)[
          #text(
            size: sizeCaption,
            fill: rgb(txCinza),
          )[
            #strong[Fonte:] Inep, Censo Escolar (2024). Dados tratados por MEC/SEGAPE e MEC/SECADI. #linebreak()
            #strong[Nota:] Consideraram-se apenas escolas municipais em funcionamento. Nas colunas de raça/cor, foram excluídos os estudantes matriculados em escolas quilombolas. A coluna Quilombola apresenta exclusivamente estudantes matriculados nessas escolas.
          ]
        ]
      } else {
        if "chartInfraestruturaBasicaEmptyState" in dados and dados.chartInfraestruturaBasicaEmptyState != none {
          image("../" + dados.chartInfraestruturaBasicaEmptyState, height: 5cm)
        }
      }      
    ]
  ]
}
