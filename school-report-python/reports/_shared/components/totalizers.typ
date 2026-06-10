// ============================================================================
// SHARED TOTALIZERS
// ============================================================================
// Componentes de totalizadores para relatórios SEGAPE
// ============================================================================

#import "style.typ": *

/// Totalizador simples (valor + descrição)
///
/// Args:
///   value: Valor a ser exibido
///   description: Descrição do valor
///   value-size: Tamanho do valor
///   value-color: Cor do valor
///   value-weight: Peso da fonte do valor
///   desc-size: Tamanho da descrição
///   desc-color: Cor da descrição
#let Totalizer(
  value: "",
  description: "",
  value-size: sizeTotalizerSmall,
  value-color: corTitulosTextosGeral,
  value-weight: weightSubtitle,
  desc-size: sizeBody,
  desc-color: rgb("000"),
) = [
  #box(width: 100%)[
    #align(center)[
      // Valor
      #text(
        value,
        fill: value-color,
        weight: value-weight,
        size: value-size,
      )
      #linebreak()

      // Descrição
      #set par(
        justify: false,
        leading: 1em
      )
      #par[
        #text(
          description,
          size: desc-size,
          weight: weightBody,
          fill: desc-color,
        )
      ]
    ]
  ]
]

/// Totalizador grande (destaque)
#let TotalizerBig(
  value: "",
  description: "",
) = Totalizer(
  value: value,
  description: description,
  value-size: sizeTotalizerBig,
  value-weight: "black",
)

/// Totalizador com imagem/ícone
///
/// Args:
///   value: Valor a ser exibido
///   description: Descrição do valor
///   image: Caminho da imagem/ícone
///   image-height: Altura da imagem
#let TotalizerWithImage(
  value: "",
  description: "",
  image: none,
  image-height: 40pt,
) = [
  #box(width: 100%)[
    #align(center)[
      // Imagem (se fornecida)
      #if image != none [
        #v(5pt)
        #box(height: image-height)[
          #image(image, height: image-height)
        ]
        #v(10pt)
      ]

      // Valor
      #text(
        value,
        fill: corTitulosTextosGeral,
        weight: weightSubtitle,
        size: sizeTotalizerSmall,
      )
      #linebreak()

      // Descrição
      #set par(
        justify: false,
        leading: 1em
      )
      #par[
        #text(
          description,
          size: sizeBody,
          weight: weightBody,
        )
      ]
    ]
  ]
]

/// Grid de totalizadores
///
/// Args:
///   totalizers: Array de totalizadores
///   columns: Número de colunas
///   gap: Espaçamento entre totalizadores
#let TotalizerGrid(
  totalizers: (),
  columns: 3,
  gap: 20pt,
) = [
  #grid(
    columns: columns,
    column-gutter: gap,
    row-gutter: gap,
    ..totalizers
  )
]

/// Totalizador com cor de destaque
///
/// Args:
///   value: Valor
///   description: Descrição
///   color: Cor de destaque (fundo ou valor)
///   bg-colored: Se true, colore o fundo; se false, colore o valor
#let TotalizerColored(
  value: "",
  description: "",
  color: mecAzul,
  bg-colored: false,
) = [
  #if bg-colored [
    #box(
      width: 100%,
      fill: color,
      radius: 5pt,
      inset: 10pt,
    )[
      #Totalizer(
        value: value,
        description: description,
        value-color: txBranco,
        desc-color: txBranco,
      )
    ]
  ] else [
    #Totalizer(
      value: value,
      description: description,
      value-color: color,
    )
  ]
]
