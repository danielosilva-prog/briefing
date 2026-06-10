#import "../components/style.typ": *
#import "../components/card.typ": Card

#let CreditoRecebidoPorDestaque(
  // Destinatário
  destinatario: str,
  /////
  // Orçamento Geral
  /////
  // Período 1 (2019-2022)
  p2CreditoRecebidoMedioPeriodo1: str,
  p2CreditoRecebidoAcumuladoPeriodo1: str,
  p2PercentVariacaoOrcamentoPeriodo1: str,
  p2PercentIPCAPeriodo1: str,
  // Periodo 2 (2023-2026)
  p2CreditoRecebidoMedioPeriodo2: str,
  p2CreditoRecebidoAcumuladoPeriodo2: str,
  p2IncrementoOrcamentario: str,
  p2PercentVariacaoOrcamentoPeriodo2: str,
  p2PercentIPCAPeriodo2: str,
  p2PercentIncrementoOrcamentario: str,
  /////
  // Creditos Extraorçamentários
  /////
  // Período 1 (2019-2022)
  p2CECreditoRecebidoMedioPeriodo1: str,
  p2CECreditoRecebidoAcumuladoPeriodo1: str,
  p2CEPercentVariacaoOrcamentoPeriodo1: str,
  p2CEPercentIPCAPeriodo1: str,
  // Periodo 2 (2023-2026)
  p2CECreditoRecebidoMedioPeriodo2: str,
  p2CECreditoRecebidoAcumuladoPeriodo2: str,
  p2CEIncrementoOrcamentario: str,
  p2CEPercentVariacaoOrcamentoPeriodo2: str,
  p2CEPercentIPCAPeriodo2: str,
  p2CEPercentIncrementoOrcamentario: str,
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

  #v(1cm)

  // ORÇAMENTO GERAL
  #text(fill: white, weight: "black", size: 20pt)[Lei Orçamentária Anual]
  #v(-.35cm)
  #set par(leading: 1em)
  #text(fill: white, weight: "regular", size: 10pt)[Despesas empenhadas por meio da utilização dos créditos orçamentários#linebreak()reservados à IFES na Lei Orçamentária Anual (LOA) Atualizada
]

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

        #v(gap - 6pt)

        #align(center + bottom)[
          // Gráficos
          #grid(
            columns: (48%, 48%),
            column-gutter: 4%,
            // Gráfico 1
            align(center)[
              #image(
                "../assets/charts/P2-G1.svg",
                width: 100%
              )
            ],
            // Gráfico 2
            align(center)[
              #image(
                "../assets/charts/P2-G2.svg",
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
                value: p2CreditoRecebidoMedioPeriodo1,
                legend: "Crédito Recebido Médio Anual\n(2019 - 2022)",
                backgroundColor: rgb("#FFE799"),
                color: rgb("#3C3C3C")
              ),
              Card(
                value: p2CreditoRecebidoAcumuladoPeriodo1,
                legend: "Crédito Recebido Acumulado\n(2019 - 2022)",
                backgroundColor: rgb("#FFE799"),
                color: rgb("#3C3C3C")
              ),
              Card(
                value: p2PercentVariacaoOrcamentoPeriodo1,
                legend: "Variação Orçamento\n(2019 - 2022)",
                backgroundColor: rgb("#FFE799"),
                color: rgb("#3C3C3C"),
              ),
              Card(
                value: p2PercentIPCAPeriodo1,
                legend: "IPCA Acumulado\n(2019 - 2022)",
                backgroundColor: rgb("#FFE799"),
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
                value: p2CreditoRecebidoMedioPeriodo2,
                legend: "Crédito Recebido Médio Anual\n(2023 - 2026)",
                backgroundColor: rgb("#F9C620"),
                  color: rgb("#3C3C3C"),
              ),
              Card(
                value: p2CreditoRecebidoAcumuladoPeriodo2,
                legend: "Crédito Recebido Acumulado\n(2023 - 2026)",
                backgroundColor: rgb("#F9C620"),
                  color: rgb("#3C3C3C"),
              ),
              Card(
                value: p2PercentVariacaoOrcamentoPeriodo2,
                legend: "Variação Orçamento\n(2023 - 2026)",
                backgroundColor: rgb("#F9C620"),
                color: rgb("#3C3C3C"),
              ),
              Card(
                value: p2PercentIPCAPeriodo2,
                legend: "IPCA Acumulado\n(2023 - 2026)",
                backgroundColor: rgb("#F9C620"),
                color: rgb("#3C3C3C"),
              ),
              Card(
                value: p2IncrementoOrcamentario,
                legend: "Incremento\nOrçamentário",
                backgroundColor: rgb("#F9C620"),
                color: rgb("#3C3C3C"),
              ),
              Card(
                value: p2PercentIncrementoOrcamentario,
                legend: "% Incremento\nOrçamentário",
                backgroundColor: rgb("#F9C620"),
                color: rgb("#3C3C3C"),
              ),
            )
          ],
        )

        #v(.05cm)
        #set par(leading: 1em, spacing: 1.25em)
        #align(left)[
          #text(size: 7pt, tracking: 0pt)[#strong[Descrição:]

          #strong[2019-2025:] Considera os valores empenhados da LOA atualizada.

          #strong[2026:] Considera o valor da LOA atualizada.

          O valor do incremento orçamentário corresponde à variação do Orçamento Acumulado entre os dois quadriênios.
          ]
        ]
      ]
    ] // Fim Shadow
  ]

  #place(top + right, dy: -.75cm)[
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

  #v(gap * 3)


  // CRÉDITOS EXTRAORÇAMENTÁRIOS
  #text(fill: white, weight: "black", size: 20pt)[Créditos Extraorçamentários]
  #v(-.35cm)
  #set par(leading: 1em)
  #text(fill: white, weight: "regular", size: 12pt)[TEDs (MEC, FNDE e INEP), CAPES e HUs.]

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

        #v(gap - 6pt)

        #align(center + bottom)[
          // Gráficos
          #grid(
            columns: (48%, 48%),
            column-gutter: 4%,
            // Gráfico 1
            align(center)[
              #image(
                "../assets/charts/P2-G3.svg",
                width: 100%
              )
            ],
            // Gráfico 2
            align(center)[
              #image(
                "../assets/charts/P2-G4.svg",
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
                value: p2CECreditoRecebidoMedioPeriodo1,
                legend: "Crédito Recebido Médio Anual\n(2019 - 2022)",
                backgroundColor: rgb("#FFE799"),
                color: rgb("#3C3C3C")
              ),
              Card(
                value: p2CECreditoRecebidoAcumuladoPeriodo1,
                legend: "Crédito Recebido Acumulado\n(2019 - 2022)",
                backgroundColor: rgb("#FFE799"),
                color: rgb("#3C3C3C")
              ),
              Card(
                value: p2CEPercentVariacaoOrcamentoPeriodo1,
                legend: "Variação Orçamento\n(2019 - 2022)",
                backgroundColor: rgb("#FFE799"),
                color: rgb("#3C3C3C"),
              ),
              Card(
                value: p2CEPercentIPCAPeriodo1,
                legend: "IPCA Acumulado\n(2019 - 2022)",
                backgroundColor: rgb("#FFE799"),
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
                value: p2CECreditoRecebidoMedioPeriodo2,
                legend: "Crédito Recebido Médio Anual\n(2023 - 2026)",
                backgroundColor: rgb("#F9C620"),
                  color: rgb("#3C3C3C"),
              ),
              Card(
                value: p2CECreditoRecebidoAcumuladoPeriodo2,
                legend: "Crédito Recebido Acumulado\n(2023 - 2026)",
                backgroundColor: rgb("#F9C620"),
                  color: rgb("#3C3C3C"),
              ),
              Card(
                value: p2CEPercentVariacaoOrcamentoPeriodo2,
                legend: "Variação Orçamento\n(2023 - 2026)",
                backgroundColor: rgb("#F9C620"),
                color: rgb("#3C3C3C"),
              ),
              Card(
                value: p2CEPercentIPCAPeriodo2,
                legend: "IPCA Acumulado\n(2023 - 2026)",
                backgroundColor: rgb("#F9C620"),
                color: rgb("#3C3C3C"),
              ),
              Card(
                value: p2CEIncrementoOrcamentario,
                legend: "Incremento\nOrçamentário",
                backgroundColor: rgb("#F9C620"),
                color: rgb("#3C3C3C"),
              ),
              Card(
                value: p2CEPercentIncrementoOrcamentario,
                legend: "% Incremento\nOrçamentário",
                backgroundColor: rgb("#F9C620"),
                color: rgb("#3C3C3C"),
              ),
            )
          ],
        )
        #v(.05cm)
        #set par(leading: 1em, spacing: 1.25em)
        #align(left)[
          #text(size: 7pt, tracking: 0pt)[#strong[Descrição:]

          #strong[2019-2025:] Considera os valores empenhados dos TEDs (MEC, FNDE e INEP) e HUs e os valores pagos referentes às bolsas e ajuda de custos informados pela CAPES.

          #strong[2026:] Considera os valores dos Créditos Extraorçamentários da IFES de 2025 corrigidos pelo IPCA.

          Os dados relativos às despesas com os Hospitais Universitários e as bolsas de pós-graduação foram informados, respectivamente, pela Ebserh e Capes, não sendo bases extraídas diretamente do Tesouro Gerencial.

          O valor do incremento orçamentário corresponde à variação do Orçamento Acumulado entre os dois quadriênios.
          ]
        ]
      ]
    ] // Fim Shadow


    #v(gap - 12pt)

    #set par(leading: 1.25em)

    #place(bottom + right, dy: -1cm)[
      #text(size: sizeCaption, fill:white, tracking: -0.01em)[Fonte: Tesouro Gerencial/SIAFI (31/12/2025), Ebserh/MEC, Capes/MEC.]
    ]
  ]
]
