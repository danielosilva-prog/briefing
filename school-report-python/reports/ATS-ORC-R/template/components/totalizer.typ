#import "style.typ": *

#let Totalizer(
  value: str,
  description: str,
) = [
  #box(width: 100%)[
    #align(center)[
      #text(
        value,
        fill: corTitulosTextosGeral,
        weight: weightSubtitle,
        size: sizeTotalizerSmall,
      )
      #linebreak()
      #set par(
        justify: false,
        leading: 1em
      )
      #par[
        #text(description, size: sizeBody, weight: weightBody)
      ]
    ]
  ]
]
