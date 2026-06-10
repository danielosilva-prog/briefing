#import "../components/style.typ": *

#import "../components/header.typ": Header

#let EstrategiasAspectosFinanceiros(..args) = {

  let dados = args.at(0)

  [

    #Header(
      titulo: [#text(weight: "extrabold")[Estratégias] de ação para a #linebreak()promoção da equidade racial],
      municipio: dados.municipio,
      uf: dados.uf,
      bgColor: rgb("265793"),
      textoDoSumario: "Estratégias: Aspectos de gestão financeira e condições de oferta"
    )

    #grid(
      columns: (auto, 1fr),
      gutter: .5cm,
      box(
        fill: rgb("00000050"),
        radius: (top-left: 2cm),
        width: 2cm,
        height: 2cm,
        inset: (left: .82cm, top: 1.25cm)
      )[#text(fill: white, weight: "black", size: 64pt)[4]],
      box(
        inset: (top: .7cm)
      )[
        #set par(leading: 14pt)
        #text(size: 18pt, weight: "light", fill: black)[Aspectos de #text(weight: "extrabold")[gestão financeira] #linebreak() e condições de #text(weight: "extrabold")[oferta]]
      ]
    )

    #box(
      inset: (right: .22cm)
    )[
      #set text(fill: black, size: sizeBodySmall)

      #grid(
        columns: (37%, 60%),
        gutter: 3%,
        align(left + horizon)[
          #box(
            inset: (top: .5cm, right: 0cm, bottom: .5cm, left: .5cm),
            width: 100%,
            radius: (left:8pt, top-right:40pt, bottom-right: 8pt)
          )[
            #text()[
              De acordo com o art. 211 da Constituição Federal, as redes de ensino devem exercer ação redistributiva em relação a suas escolas. Isto está relacionado ao conceito de “progressividade”, ou #strong[“investir mais em quem mais precisa”].​

              Na perspectiva da equidade racial, o significado prático é – entre outros pontos já tratados – conduzir a gestão financeira da rede priorizando investimentos nas trajetórias educacionais dos estudantes mais vulneráveis.
            ]
          ]
        ],
        box(
          inset: (top: .75cm, right: .5cm, bottom: .5cm, left: .5cm),
          fill: rgb(pneerqLaranja),
          width: 100%,
          radius: (left:8pt, bottom-left:20pt, top-right: 8pt, bottom-right: 8pt)
        )[
          #text(fill: txBranco)[
            #strong[O FUNDEB tem levado mais recursos para financiar a Educação Escolar Quilombola (EEQ)!​]

            Entre 2023 e 2026, o valor aluno/ano da matrícula de aluno quilombola cresceu: na comparação com uma matrícula em área urbana, o valor quilombola é agora #strong[40% maior]!​

            Veja também a comparação do valor mínimo aluno/ano de estudante de pré-escola quilombola parcial, que #strong[cresceu 56% nos últimos anos]:​

            #align(center)[
              #grid(
              columns: (1fr, 1fr),
              gutter: .5cm,
              box(
                fill: txBranco,
                width: 100%,
                radius: 4pt,
                inset: (top:.35cm, x: .25cm, bottom: .25cm)
              )[
                #text(fill: pneerqMarrom, weight: "extrabold", size: sizeBodySmall)[2022#linebreak() R\$ 6.155,76 aluno/ano​]
              ],

              box(
                fill: txBranco,
                width: 100%,
                radius: 4pt,
                inset: (top:.35cm, x: .25cm, bottom: .25cm)
              )[
                #text(fill: pneerqMarrom, weight: "extrabold", size: sizeBodySmall)[2026#linebreak() R\$ 9.600,09 aluno/ano​​]
              ]
              )
            ]
          ]
        ]
      )

      #set par(spacing: 1.5em)

      #box(
        fill: rgb("EAEAEA50"),
        inset: (top: .75cm, right: .75cm, bottom: .6cm, left: .75cm),
        radius: (top-left: 20pt, bottom-right: 20pt),
        width: 100%
      )[

        #set par(leading: 1.15em, spacing: 16pt)

        #set par(leading: .75em)
        #text(weight: weightTitle, size: sizeBody)[Como investir em ações de equidade racial na sua rede de ensino?​]

        #set par(leading: 1em)

        #align(left + horizon)[
          #grid(
            columns: (auto, 1fr),
            gutter: .25cm,
            row-gutter: 9pt,
            align(center + horizon)[
              #box(width: .8cm, height: .8cm, fill: pneerqLaranja, radius: 50%, inset: (top: .15cm))[
                #text(size: 14pt, weight: "black", fill: white)[1]]
            ],
            text(size: 9pt)[
              Priorização de investimento em manutenção e melhoria da infraestrutura para escolas em territórios mais vulneráveis e/ou que atendam estudantes mais vulneráveis;​
            ],
            align(center + horizon)[
              #box(width: .8cm, height: .8cm, fill: pneerqLaranja, radius: 50%, inset: (top: .15cm))[
                #text(size: 14pt, weight: "black", fill: white)[2]]
            ],
            text(size: 9pt)[
              Priorização de investimento na construção de novas escolas, novas salas de aula e novos espaços escolares para regiões mais vulneráveis, incluindo territórios quilombolas e indígenas;​
            ],
            align(center + horizon)[
              #box(width: .8cm, height: .8cm, fill: pneerqLaranja, radius: 50%, inset: (top: .15cm))[
                #text(size: 14pt, weight: "black", fill: white)[3]]
            ],
            text(size: 9pt)[
              Ampliação de vagas em creche e no tempo integral com prioridade de matrícula para alunos PPI, quilombolas e de maior vulnerabilidade social;​
            ],
            align(center + horizon)[
              #box(width: .8cm, height: .8cm, fill: pneerqLaranja, radius: 50%, inset: (top: .15cm))[
                #text(size: 14pt, weight: "black", fill: white)[4]]
            ],
            text(size: 9pt)[
              Criação de incentivos salariais e de carreira para estimular a atribuição de profissionais da educação mais experientes e melhor formados em escolas vulneráveis;​
            ],
            align(center + horizon)[
              #box(width: .8cm, height: .8cm, fill: pneerqLaranja, radius: 50%, inset: (top: .15cm))[
                #text(size: 14pt, weight: "black", fill: white)[5]]
            ],
            text(size: 9pt)[
              Elaboração de processos seletivos com ação afirmativa para profissionais PPI e quilombolas, além da valorização do conhecimento sobre equidade racial em todos os processos seletivos; ​
            ],
            align(center + horizon)[
              #box(width: .8cm, height: .8cm, fill: pneerqLaranja, radius: 50%, inset: (top: .15cm))[
                #text(size: 14pt, weight: "black", fill: white)[6]]
            ],
            text(size: 9pt)[
              Realização de formações em rede relacionadas à equidade racial;​
            ],
            align(center + horizon)[
              #box(width: .8cm, height: .8cm, fill: pneerqLaranja, radius: 50%, inset: (top: .15cm))[
                #text(size: 14pt, weight: "black", fill: white)[7]]
            ],
            text(size: 9pt)[
              Aquisição de materiais e brinquedos pedagógicos para promoção da ERER e da EEQ;​
            ],
            align(center + horizon)[
              #box(width: .8cm, height: .8cm, fill: pneerqLaranja, radius: 50%, inset: (top: .15cm))[
                #text(size: 14pt, weight: "black", fill: white)[8]]
            ],
            text(size: 9pt)[
              Criação de PDDE local com recursos ampliados para escolas mais vulneráveis e com verbas destinadas especificamente à promoção da equidade racial;​
            ],
            align(center + horizon)[
              #box(width: .8cm, height: .8cm, fill: pneerqLaranja, radius: 50%, inset: (top: .15cm))[
                #text(size: 14pt, weight: "black", fill: white)[9]]
            ],
            text(size: 9pt)[
              Melhoria da oferta de alimentação escolar, com cardápios escolares que dialoguem com a cultura alimentar e a biodiversidade presente nos territórios e com a contratação de merendeiras/os quilombolas para as escolas quilombolas da Rede. ​
            ],
            align(center + horizon)[
              #box(width: .8cm, height: .8cm, fill: pneerqLaranja, radius: 50%, inset: (top: .15cm))[
                #text(size: 14pt, weight: "black", fill: white)[10]]
            ],
            text(size: 9pt)[
              Melhoria do transporte escolar para atendimento adequado das escolas mais vulneráveis, inclusive garantindo meios de acesso às comunidades quilombolas e indígenas.​
            ],
          )
        ]
      ]

      #v(-.95cm)

      #align(left + horizon)[
        #align(right + bottom)[
          #set par(justify: false)
          #grid(
            columns: (40%, 56%),
            gutter: 4%,
            grid(
              columns: (1fr, auto),
              gutter: .25cm,
              box(inset:(bottom: .125cm))[Conheça as receitas educacionais que seu município recebe, por meio do painel de receitas no Novo PAR​],
              shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: 4pt)[
                #box(
                  fill: white,
                  inset: .25cm,
                  radius: 4pt,
                  width: 2.5cm
                )[#image("../assets/qrcodes/py/novo-par.svg", width: 100%)]
              ]
            ),
            grid(
              columns: (1fr, auto),
              gutter: .25cm,
              box(inset:(bottom: .125cm))[Faça o curso de 80h do MEC sobre #strong[Financiamento e Gestão Financeira para a Equidade na Educação Básica]. Seus técnicos, diretores e professores também podem fazer!​],
              shadow(blur: 4pt, dx: 1pt, dy: 1pt,  fill: rgb(0, 0, 0, 25%), radius: 4pt)[
                #box(
                  fill: white,
                  inset: .25cm,
                  radius: 4pt,
                  width: 2.5cm
                )[#image("../assets/qrcodes/py/formacao-secadi.svg", width: 100%)]
              ]
            )
          )
        ]
      ]
    ]
  ]
}