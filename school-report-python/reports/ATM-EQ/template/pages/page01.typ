// ============================================================================
// PÁGINA 01 - EXEMPLO
// ============================================================================

#import "../components/style.typ": *
#import "../components/cards.typ": Card
#import "../components/totalizers.typ": Totalizer, TotalizerGrid

/// Página 01 - Visão Geral
///
/// Args:
///   data: Dados das queries
///   charts: Gráficos gerados
#let Page01(
  data: (:),
  charts: (:),
) = [
  = Visão Geral

  == Indicadores Principais

  #TotalizerGrid(
    columns: 3,
    totalizers: (
      Totalizer(
        value: data.at("valor1", default: "-"),
        description: "Indicador 1"
      ),
      Totalizer(
        value: data.at("valor2", default: "-"),
        description: "Indicador 2"
      ),
      Totalizer(
        value: data.at("valor3", default: "-"),
        description: "Indicador 3"
      ),
    )
  )

  #v(20pt)

  == Gráficos

  #Card(title: "Gráfico Principal")[
    // Aqui virá o gráfico decodificado
    #box(
      width: 100%,
      height: 300pt,
      fill: bgCinzaClaro,
    )[
      #align(center + horizon)[
        #text("Gráfico será inserido aqui", fill: txCinza)
      ]
    ]
  ]

  #pagebreak()
]

