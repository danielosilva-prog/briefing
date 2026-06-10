#import "../components/style.typ": *
#import "../components/card.typ": Card

#let CreditoRecebidoPorDestaque26443(
  // Destinatário
  destinatario: str,
  // Período 1 (2019-2021)
  p7CreditoRecebidoMedioPeriodo1: str,
  p7CreditoRecebidoAcumuladoPeriodo1: str,
  p7PercentVariacaoOrcamentoPeriodo1: str,
  p7PercentIPCAPeriodo1: str,
  // Periodo 2 (2023-2025)
  p7CreditoRecebidoMedioPeriodo2: str,
  p7CreditoRecebidoAcumuladoPeriodo2: str,
  p7IncrementoOrcamentario: str,
  p7PercentVariacaoOrcamentoPeriodo2: str,
  p7PercentIPCAPeriodo2: str,
  p7PercentIncrementoOrcamentario: str,
) = [

#hide[
    = Crédito Recebido por Destaque (EBSERH - UO 26443)
  ]

  // VISÃO GERAL
  #align(center)[
    #text(
      weight: weightSubtitle,
      size: 14pt,
      fill: rgb(txCinza),
    )[#upper[Visão geral]]
  ]

  #v(gap - 6pt)

  #grid(
    columns: (48%, 48%),
    column-gutter: 4%,
    // Gráfico 1
    align(left)[
      #image(
        "../assets/charts/P6-G1.svg",
        width: 100%,
      )
    ],
    // Gráfico 2
    align(right)[
      #image(
        "../assets/charts/P6-G2.svg",
        width: 100%,
      )
    ],
  )

  #v(gap)

  #grid(
    columns: (48%, 48%),
    column-gutter: 4%,
    align(left)[
      #grid(
        columns: (49%, 49%),
        column-gutter: 4pt,
        row-gutter: 4pt,
        Card(
          value: p7CreditoRecebidoMedioPeriodo1,
          legend: "Crédito Recebido Médio Anual\n(2019 - 2021)",
          backgroundColor: rgb("#E1C8EA"),
          color: rgb("#3C3C3C")
        ),
        Card(
          value: p7CreditoRecebidoAcumuladoPeriodo1,
          legend: "Crédito Recebido Acumulado\n(2019 - 2021)",
          backgroundColor: rgb("#E1C8EA"),
          color: rgb("#3C3C3C")
        ),
        Card(
          value: p7PercentVariacaoOrcamentoPeriodo1,
          legend: "Variação Orçamento\n(2019 - 2021)",
          backgroundColor: rgb("#E1C8EA"),
          color: rgb("#3C3C3C"),
        ),
        Card(
          value: p7PercentIPCAPeriodo1,
          legend: "IPCA Acumulado\n(2019 - 2021)",
          backgroundColor: rgb("#E1C8EA"),
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
          value: p7CreditoRecebidoMedioPeriodo2,
          legend: "Crédito Recebido Médio Anual\n(2023 - 2025)",
          backgroundColor: rgb("#7800A3"),
        ),
        Card(
          value: p7CreditoRecebidoAcumuladoPeriodo2,
          legend: "Crédito Recebido Acumulado\n(2023 - 2025)",
          backgroundColor: rgb("#7800A3"),
        ),
        Card(
          value: p7PercentVariacaoOrcamentoPeriodo2,
          legend: "Variação Orçamento\n(2023 - 2025)",
          backgroundColor: rgb("#7800A3"),
        ),
        Card(
          value: p7PercentIPCAPeriodo2,
          legend: "IPCA Acumulado\n(2023- 2025)",
          backgroundColor: rgb("#7800A3"),
        ),
        Card(
          value: p7IncrementoOrcamentario,
          legend: "Incremento\nOrçamentário",
          backgroundColor: rgb("#7800A3"),
        ),
        Card(
          value: p7PercentIncrementoOrcamentario,
          legend: "% Incremento\nOrçamentário",
          backgroundColor: rgb("#7800A3"),
        ),
      )
    ],
  )

  #v(gap * 6)

  // RESULTADO LEI
  #align(center)[
    #text(
      weight: weightSubtitle,
      size: 14pt,
      fill: rgb(txCinza),
    )[#upper[Resultado Lei]]
  ]

  #v(gap - 6pt)

  #align(center)[
    #chart-legend((
      (color: "11B880", label: "Discricionário"),
      (color: "FD9696", label: "Emendas"),
      (color: "FFC769", label: "Obrigatório"),
    ))
  ]

  #grid(
    columns: (47%, 47%),
    column-gutter: 6%,
    // Gráfico 3
    align(left)[
      #image(
        "../assets/charts/P6-G3.svg",
        width: 100%,
      )
    ],
    // Gráfico 4
    align(right)[
      #image(
        "../assets/charts/P6-G4.svg",
        width: 100%,
      )
    ],
  )

  #v(gap * 6)

  // Grupo de despesa
  #align(center)[
    #text(
      weight: weightSubtitle,
      size: 14pt,
      fill: rgb(txCinza),
    )[#upper[Grupo de despesa]]
  ]

  #v(gap - 6pt)

  #align(center)[
    #chart-legend((
      (color: "E290FF", label: "Pessoal/Encargos"),
      (color: "88D088", label: "Custeio"),
      (color: "65CCF2", label: "Capital"),
    ))
  ]

  #grid(
    columns: (47%, 47%),
    column-gutter: 6%,
    // Gráfico 5
    align(left)[
      #image(
        "../assets/charts/P6-G5.svg",
        width: 100%,
      )
    ],
    // Gráfico 6
    align(right)[
      #image(
        "../assets/charts/P6-G6.svg",
        width: 100%,
      )
    ],
  )

  // FONTE E NOTA — FIXAS NA MARGEM INFERIOR
  #place(bottom)[

    #set par(leading: 1.25em)

    #grid(
      columns: (30%, 64%),
      column-gutter: 6%,

      align(left)[
        #text(size: sizeCaption, tracking: -0.01em)[Fonte: Tesouro Gerencial/SIAFI (31/12/2025)

          Valores Nominais]
      ],

      align(right)[
        #text(
          size: sizeCaption,
          tracking: -0.01em,
        )[Crédito Recebido por Destaque: Corresponde aos créditos enviados

        pela EBSERH (UO 26443) #destinatario (geralmente por meio de TED).

        Resultado Lei: Obrigatório (Res. Lei = 0 e 1); Discricionário (Res. Lei = 2 e 3); Emendas (Res. Lei = 6, 7, 8 e 9).
]
      ],
    )
  ]
]