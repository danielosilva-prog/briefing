#import "../components/style.typ": *
#import "../components/card.typ": Card

#let DespesaEmpenhada(
  // Destinatário
  destinatario: str,
  // Período 1 (2019-2022)
  p1OrcamentoMedioPeriodo1: str,
  p1OrcamentoAcumuladoPeriodo1: str,
  p1PercentVariacaoOrcamentoPeriodo1: str,
  p1PercentIPCAPeriodo1: str,
  // Periodo 2 (2023-2026)
  p1OrcamentoMedioPeriodo2: str,
  p1OrcamentoAcumuladoPeriodo2: str,
  p1IncrementoOrcamentario: str,
  p1PercentVariacaoOrcamentoPeriodo2: str,
  p1PercentIPCAPeriodo2: str,
  p1PercentIncrementoOrcamentario: str,
  sigla: str,
  universidade: str,
) = [

  // Logo
  #let logo-path = if sigla == "Brasil" {
    "../assets/logos/BANDEIRABRASIL.PNG"
  } else {
    "../assets/logos/" + upper(sigla) + ".PNG"
  }

  #let sigla-final = if sigla == "Brasil" { "IFES" } else { sigla }

  #place(top + right, dy: -3.25cm)[
    #shadow(blur: 5pt, dx: 0pt, dy: 1pt,  fill: rgb(0, 0, 0, 15%), radius: 50%)[
      #box(
        height: 2.5cm,
        width: 2.5cm,
        inset: 4pt,
        radius: 50%,
        fill: bgBranco,
        clip: true
      )[
        #align(center + horizon)[
          #image(logo-path, fit: "contain")
        ]
      ]
    ]
  ]

  // Créditos Totais
  #text(fill: white, weight: "black", size: 18pt)[Créditos Totais]
  #v(-.35cm)
  #set par(leading: 1em)
  #text(fill: white, weight: "regular", size: 10pt)[Lei Orçamentária Anual (LOA) Atualizada + Créditos Extraorçamentários.]

  #v(-.25cm)

  // VISÃO GERAL
  #align(center)[
    #shadow(blur: 5pt, dx: 0pt, dy: 1pt,  fill: rgb(0, 0, 0, 15%), radius: 5pt)[
      #box(fill: white, width: 100%, radius: 5pt, inset: (x:.5cm, top: .75cm, bottom: .35cm))[
        // Título da seção
        #text(
          weight: weightSubtitle,
          size: 14pt,
          fill: rgb(txCinza),
        )[#upper[Visão geral]]

        #v(gap - 12pt)

        #align(center + bottom)[
          // Gráficos
          #grid(
            columns: (48%, 48%),
            column-gutter: 4%,
            // Gráfico 1
            align(center)[
              #image(
                "../assets/charts/P1-G1.svg",
                width: 100%
              )
            ],
            // Gráfico 2
            align(center)[
              #image(
                "../assets/charts/P1-G2.svg",
                width: 100%
              )
            ],
          )
        ]

        // Cards
        #grid(
          columns: (48%, 48%),
          column-gutter: 4%,
          align(left)[
            #grid(
              columns: (49%, 49%),
              column-gutter: 4pt,
              row-gutter: 4pt,
              Card(
                value: p1OrcamentoMedioPeriodo1,
                legend: "Orçamento Médio Anual\n(2019 - 2022)",
                backgroundColor: rgb("#65CCF2"),
                color: rgb("#3C3C3C")
              ),
              Card(
                value: p1OrcamentoAcumuladoPeriodo1,
                legend: "Orçamento Acumulado\n(2019 - 2022)",
                backgroundColor: rgb("#65CCF2"),
                color: rgb("#3C3C3C")
              ),
              Card(
                value: p1PercentVariacaoOrcamentoPeriodo1,
                legend: "Variação Orçamento\n(2019 - 2022)",
                backgroundColor: rgb("#65CCF2"),
                color: rgb("#3C3C3C"),
              ),
              Card(
                value: p1PercentIPCAPeriodo1,
                legend: "IPCA Acumulado\n(2019 - 2022)",
                backgroundColor: rgb("#65CCF2"),
                color: rgb("#3C3C3C"),
              ),
            )
          ],
          align(right)[
            #grid(
              columns: (33%, 33%, 33%),
              column-gutter: 4pt,
              row-gutter: 4pt,
              Card(
                value: p1OrcamentoMedioPeriodo2,
                legend: "Orçamento Médio Anual\n(2023 - 2026)",
                backgroundColor: rgb("#0097CD"),
              ),
              Card(
                value: p1OrcamentoAcumuladoPeriodo2,
                legend: "Orçamento Acumulado\n(2023 - 2026)",
                backgroundColor: rgb("#0097CD"),
              ),
              Card(
                value: p1PercentVariacaoOrcamentoPeriodo2,
                legend: "Variação Orçamento\n(2023 - 2026)",
                backgroundColor: rgb("#0097CD"),
              ),
              Card(
                value: p1PercentIPCAPeriodo2,
                legend: "IPCA Acumulado\n(2023- 2026)",
                backgroundColor: rgb("#0097CD"),
              ),
              Card(
                value: p1IncrementoOrcamentario,
                legend: "Incremento\nOrçamentário",
                backgroundColor: rgb("#0097CD"),
              ),
              Card(
                value: p1PercentIncrementoOrcamentario,
                legend: "% Incremento\nOrçamentário",
                backgroundColor: rgb("#0097CD"),
              ),
            )
          ],
        )

        #v(.05cm)
        #set par(leading: 1em, spacing: 1.25em)
        #align(left)[
          #text(size: 7pt, tracking: 0pt)[#strong[Descrição:]

          #strong[2019-2025:] Considera os valores empenhados da LOA atualizada + TEDs (MEC, FNDE e INEP) e HUs e os valores pagos referentes às bolsas e ajuda de custos informados pela CAPES.

          #strong[2026:] Considera o valor da LOA atualizada + os valores dos Créditos Extraorçamentários da IFES de 2025 corrigido pelo IPCA.

          Os dados relativos às despesas com os Hospital Universitários e as bolsas de pós-graduação foram informados, respectivamente, pela Ebserh e Capes, não sendo bases extraídas diretamente do Tesouro Gerencial.

          O valor do incremento orçamentário corresponde a variação do Orçamento Acumulado entre os dois quadriênios observados.

          ]
        ]
      ]
    ] // Fim Shadow

    #v(gap - 12pt)

    // ORÇAMENTO POR TUPO DE DESPESA
    #shadow(blur: 5pt, dx: 0pt, dy: 1pt,  fill: rgb(0, 0, 0, 15%), radius: 5pt)[
      #box(fill: white, width: 100%, radius: 5pt, inset: (x:.5cm, top: .75cm, bottom: .35cm))[
        // Título da seção
        #text(
          weight: weightSubtitle,
          size: 14pt,
          fill: rgb(txCinza),
        )[#upper[Orçamento por Tipo de Despesa]]

        #v(gap - 12pt)

        #chart-legend((
          (color: "FF7D00", label: "Emendas"),
          (color: "4AB46D", label: "Discricionário"),
          (color: "FFD000", label: "Obrigatório"),
        ))

        #align(center + bottom)[
          #grid(
            columns: (47%, 47%),
            column-gutter: 6%,
            // Gráfico 3
            align(center)[
              #image(
                "../assets/charts/P1-G3.svg",
                width: 100%
              )
            ],
            // Gráfico 4
            align(center)[
              #image(
                "../assets/charts/P1-G4.svg",
                width: 100%
              )
            ],
          )
        ]
      ]
    ] // Fim Shadow

    #v(gap - 12pt)

    // GRUPO DE DESPESA
    #shadow(blur: 5pt, dx: 0pt, dy: 1pt,  fill: rgb(0, 0, 0, 15%), radius: 5pt)[
      #box(fill: white, width: 100%, radius: 5pt, inset: (x:.5cm, top: .75cm, bottom: .35cm))[
        // Título da seção
        #text(
          weight: weightSubtitle,
          size: 14pt,
          fill: rgb(txCinza),
        )[#upper[Grupo de despesa]]

        #v(gap - 12pt)

        #chart-legend((
          (color: "88D088", label: "Capital"),
          (color: "FFD000", label: "Custeio"),
          (color: "0095DA", label: "Pessoal/Encargos"),
        ))


        #v(gap)

        #align(center + bottom)[
          #grid(
            columns: (47%, 47%),
            column-gutter: 6%,
            // Gráfico 5
            align(center)[
              #image(
                "../assets/charts/P1-G5.svg",
                width: 100%
              )
            ],
            // Gráfico 6
            align(center)[
              #image(
                "../assets/charts/P1-G6.svg",
                width: 100%
              )
            ],
          )
        ]
      ]
    ] // Fim Shadow

    #place(bottom + right, dy: -1cm)[
      #text(size: sizeCaption, fill:white, tracking: -0.01em)[Fonte: Tesouro Gerencial/SIAFI (31/12/2025), Ebserh/MEC, Capes/MEC.]
    ]
  ]
]
