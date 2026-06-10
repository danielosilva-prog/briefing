#import "../components/style.typ": *
#import "../components/card.typ": Card

#let CreditoRecebidoPorDestaque26290(
  // Destinatário
  destinatario: str,
  // Período 1 (2019-2021)
  p4CreditoRecebidoMedioPeriodo1: str,
  p4CreditoRecebidoAcumuladoPeriodo1: str,
  p4PercentVariacaoOrcamentoPeriodo1: str,
  p4PercentIPCAPeriodo1: str,
  // Periodo 2 (2023-2025)  
  p4CreditoRecebidoMedioPeriodo2: str,
  p4CreditoRecebidoAcumuladoPeriodo2: str,
  p4IncrementoOrcamentario: str,
  p4PercentVariacaoOrcamentoPeriodo2: str,
  p4PercentIPCAPeriodo2: str,
  p4PercentIncrementoOrcamentario: str,
) = [

  #hide[
    = Crédito Recebido por Destaque (INEP - UO 26290)
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
        "../assets/charts/P4-G1.svg",
        width: 100%,
      )
    ],
    // Gráfico 2
    align(right)[
      #image(
        "../assets/charts/P4-G2.svg",
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
          value: p4CreditoRecebidoMedioPeriodo1,
          legend: "Crédito Recebido Médio Anual\n(2019 - 2021)",
          backgroundColor: rgb("#A2EDA2"),
          color: rgb("#3C3C3C")
        ),
        Card(
          value: p4CreditoRecebidoAcumuladoPeriodo1,
          legend: "Crédito Recebido Acumulado\n(2019 - 2021)",
          backgroundColor: rgb("#A2EDA2"),
          color: rgb("#3C3C3C")
        ),
        Card(
          value: p4PercentVariacaoOrcamentoPeriodo1,
          legend: "Variação Orçamento\n(2019 - 2021)",
          backgroundColor: rgb("#A2EDA2"),
          color: rgb("#3C3C3C"),
        ),
        Card(
          value: p4PercentIPCAPeriodo1,
          legend: "IPCA Acumulado\n(2019 - 2021)",
          backgroundColor: rgb("#A2EDA2"),
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
          value: p4CreditoRecebidoMedioPeriodo2,
          legend: "Crédito Recebido Médio Anual\n(2023 - 2025)",
          backgroundColor: rgb("#008F00"),
        ),
        Card(
          value: p4CreditoRecebidoAcumuladoPeriodo2,
          legend: "Crédito Recebido Acumulado\n(2023 - 2025)",
          backgroundColor: rgb("#008F00"),
        ),
        Card(
          value: p4PercentVariacaoOrcamentoPeriodo2,
          legend: "Variação Orçamento\n(2023 - 2025)",
          backgroundColor: rgb("#008F00"),
        ),
        Card(
          value: p4PercentIPCAPeriodo2,
          legend: "IPCA Acumulado\n(2023- 2025)",
          backgroundColor: rgb("#008F00"),
        ),
        Card(
          value: p4IncrementoOrcamentario,
          legend: "Incremento\nOrçamentário",
          backgroundColor: rgb("#008F00"),
        ),
        Card(
          value: p4PercentIncrementoOrcamentario,
          legend: "% Incremento\nOrçamentário",
          backgroundColor: rgb("#008F00"),
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
        "../assets/charts/P4-G3.svg",
        width: 100%,
      )
    ],
    // Gráfico 4
    align(right)[
      #image(
        "../assets/charts/P4-G4.svg",
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
        "../assets/charts/P4-G5.svg",
        width: 100%,
      )
    ],
    // Gráfico 6
    align(right)[
      #image(
        "../assets/charts/P4-G6.svg",
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
        
        pelo INEP (UO 26290) #destinatario (geralmente por meio de TED).
        
        Resultado Lei: Obrigatório (Res. Lei = 0 e 1); Discricionário (Res. Lei = 2 e 3); Emendas (Res. Lei = 6, 7, 8 e 9).]
      ],
    )
  ]
]
