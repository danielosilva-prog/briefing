#import "../components/style.typ": *

#import "../components/header.typ": Header

#let DiagnosticoCensoDemografico(..args) = {
  let dados = args.at(0)

  [
    #Header(
      titulo: [#text(weight: "extrabold")[Diagnóstico] para compreensão #linebreak()de desigualdades raciais],
      municipio: dados.municipio,
      uf: dados.uf,
      bgColor: rgb("0C8C59"),
      textoDoSumario: "Diagnóstico para compreensão de desigualdades raciais"
    )

    #align(center)[
      #box(
        stroke: .75pt + txCinza,
        inset: (top: 12pt, x: 8pt, bottom: 7pt),
      )[
        #text(
          weight: weightSubtitle,
          size: sizeTitle,
          fill: rgb(txCinza),
        )[#upper[Dados do CadÚnico - 2025]]
      ]

      #v(gap * .65)

      #text(
        weight: weightSubtitle,
        size: sizeBody,
        fill: rgb(txCinza),
      )[#upper[Atendimento em creche e em pré-escola, por raça/cor (CadÚnico)]]

      #v(-.4cm)

      #place(top + right, dx: 1cm, dy: 5.6cm)[

        #move(dx: -.5cm)[
          #image("../assets/icons/warning.svg", height: .6cm)
        ]

        #v(-.35cm)

        #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: (left: .125cm))[
          #box(
            inset: (top: .4cm, bottom: .35cm, right: .5cm, left: .125cm),
            fill: rgb("#fff5c2"),
            width: 3.6cm,
            radius: (left: .125cm)
          )[
            #set par(justify: false)
            #text(
              size: sizeCaption
            )[
              São identificados pelo #strong[Cadastro Único] os estudantes cujas famílias são consideradas de baixa renda.
            ]
          ]
        ]
      ]

      #place(top + left, dx: -.75cm, dy: 4.8cm)[

        #move(dx: .25cm)[
          #image("../assets/icons/instructions.png", height: .8cm)
        ]

        #v(-.35cm)

        #shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 15%), radius: (right: .125cm))[
          #box(
            inset: (top: .4cm, bottom: .35cm, right: .25cm, left: .25cm),
            fill: bgTabela,
            width: 3.85cm,
            radius: (right: .125cm)
          )[
            #set par(justify: false, leading: .8em)
            #text(
              size: sizeCaption,
              tracking: -.15pt
            )[
              #strong[Como ler os dados?]#linebreak() Veja se há diferenças consideráveis entre os grupos de raça/cor dos estudantes. Desigualdades de acesso educacional desde a primeira infância podem estar na raiz das desigualdades de aprendizagem ao longo da trajetória educacional.
            ]
          ]
        ]
      ]

      #if "chartAtendimentoCrechePreEscola" in dados and dados.chartAtendimentoCrechePreEscola != none {
        image("../" + dados.chartAtendimentoCrechePreEscola, height: 4.8cm)
      }

      #align(center)[
        #text(
          size: sizeCaption,
          fill: rgb(txCinza)
        )[
          #strong[Fonte:] CadÚnico (02/2025). Dados tratados por MEC/SEGAPE e MEC/SECADI. #linebreak()
          #strong[Nota:] Creche corresponde à faixa etária de 0 a 3 anos e pré-escola, à faixa etária de 4 a 6 anos. Foram consideradas como estudantes as crianças que frequentavam escola ou creche em rede pública. Crianças sem declaração de raça/cor foram excluídas do cálculo; Possíveis divergências entre os valores apresentados nos gráficos desta página se devem pela consideração de bases de dados e metodologias de coleta distintas (CadÚnico e Censo Escolar).
        ]
      ]

      #v(.15cm)

      #box(
        stroke: .75pt + txCinza,
        inset: (top: 12pt, x: 8pt, bottom: 7pt),
      )[
        #text(
          weight: weightSubtitle,
          size: sizeTitle,
          fill: rgb(txCinza),
        )[#upper[Dados do Censo Escolar - 2025]]
      ]

      #v(.15cm)

      #text(
        weight: weightSubtitle,
        size: sizeBody,
        fill: rgb(txCinza),
      )[#upper[Distribuição de matrículas por raça/cor e por escolas quilombolas]]

      #v(gap - 12pt)

      #if "chartDistribuicaoMatriculas" in dados and dados.chartDistribuicaoMatriculas != none {
        image("../" + dados.chartDistribuicaoMatriculas, height: 4.8cm)
      }

      #v(-.25cm)

      #align(center)[
        #text(
          size: sizeCaption,
          fill: rgb(txCinza)
        )[
          #strong[Fonte:] Inep, Censo Escolar (2025). Dados tratados por MEC/SEGAPE e MEC/SECADI.  #linebreak()
          #strong[Nota:] Consideram-se matrículas da rede municipal em escolas em funcionamento. A categoria Quilombola reúne matrículas em escolas quilombolas e não se sobrepõe às categorias de raça/cor.
        ]
      ]

      #v(gap * .8)

      #text(
        weight: weightSubtitle,
        size: sizeBody,
        fill: rgb(txCinza),
      )[#upper[Série histórica do percentual de declaração racial]]

      #v(gap - 12pt)

      #if "chartDeclaracaoRacial" in dados and dados.chartDeclaracaoRacial != none {
        image("../" + dados.chartDeclaracaoRacial, height: 4.1cm)
      }

      #v(0cm)

      #align(center)[
        #text(
          size: sizeCaption,
          fill: rgb(txCinza)
        )[
          #strong[Fonte:] Inep, Censo Escolar (2007-2025). Dados tratados por MEC/SEGAPE e MEC/SECADI.  #linebreak()
          #strong[Nota:] Consideram-se matrículas da rede municipal com informação declarada de raça/cor, conforme o dado disponível em cada ano da série.
        ]
      ]
    ]
  ]
}
