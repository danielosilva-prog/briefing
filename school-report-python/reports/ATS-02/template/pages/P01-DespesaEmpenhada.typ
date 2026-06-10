#import "../components/style.typ": *
#import "../components/card.typ": Card

#let DespesaEmpenhada( 
  // Destinatário
  destinatario: str,
  // Período 1 (2019-2021)
  p1OrcamentoMedioPeriodo1: str,
  p1OrcamentoAcumuladoPeriodo1: str,
  p1PercentVariacaoOrcamentoPeriodo1: str,
  p1PercentIPCAPeriodo1: str,
  // Periodo 2 (2023-2025)  
  p1OrcamentoMedioPeriodo2: str,
  p1OrcamentoAcumuladoPeriodo2: str,
  p1IncrementoOrcamentario: str,
  p1PercentVariacaoOrcamentoPeriodo2: str,
  p1PercentIPCAPeriodo2: str,
  p1PercentIncrementoOrcamentario: str,
) = [

  #hide[
    = Despesa Empenhada
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
        "../assets/charts/P1-G1.svg",
        width: 100%,
      )
    ],
    // Gráfico 2
    align(right)[
      #image(
        "../assets/charts/P1-G2.svg",
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
          value: p1OrcamentoMedioPeriodo1,
          legend: "Orçamento Médio Anual\n(2019 - 2021)",
          backgroundColor: rgb("#65CCF2"),
          color: rgb("#3C3C3C")
        ),
        Card(
          value: p1OrcamentoAcumuladoPeriodo1,
          legend: "Orçamento Acumulado\n(2019 - 2021)",
          backgroundColor: rgb("#65CCF2"),
          color: rgb("#3C3C3C")
        ),
        Card(
          value: p1PercentVariacaoOrcamentoPeriodo1,
          legend: "Variação Orçamento\n(2019 - 2021)",
          backgroundColor: rgb("#65CCF2"),
          color: rgb("#3C3C3C"),
        ),
        Card(
          value: p1PercentIPCAPeriodo1,
          legend: "IPCA Acumulado\n(2019 - 2021)",
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
          legend: "Orçamento Médio Anual\n(2023 - 2025)",
          backgroundColor: rgb("#0097CD"),
        ),
        Card(
          value: p1OrcamentoAcumuladoPeriodo2,
          legend: "Orçamento Acumulado\n(2023 - 2025)",
          backgroundColor: rgb("#0097CD"),
        ),
        Card(
          value: p1PercentVariacaoOrcamentoPeriodo2,
          legend: "Variação Orçamento\n(2023 - 2025)",
          backgroundColor: rgb("#0097CD"),
        ),
        Card(
          value: p1PercentIPCAPeriodo2,
          legend: "IPCA Acumulado\n(2023- 2025)",
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
        "../assets/charts/P1-G3.svg",
        width: 100%,
      )
    ],
    // Gráfico 4
    align(right)[
      #image(
        "../assets/charts/P1-G4.svg",
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
        "../assets/charts/P1-G5.svg",
        width: 100%,
      )
    ],
    // Gráfico 6
    align(right)[
      #image(
        "../assets/charts/P1-G6.svg",
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
        )[Orçamento Originário: Despesas empenhadas por meio da utilização dos créditos
        
        orçamentários reservados #destinatario na Lei Orçamentária Anual (LOA).

          Resultado Lei: Obrigatório (Res. Lei= 0 e 1); Discricionário (Res. Lei = 2 e 3); Emendas (Res. Lei = 6, 7, 8 e 9))]
      ],
    )
  ]
]
