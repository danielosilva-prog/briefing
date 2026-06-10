#import "style.typ": *

#let TotalizerWithImage(
  img: image,
  value: str,
  description: str,
  fonte: str,
  boxWidth: length,
  centered: bool,
) = [
  #set image(
    width: 23%,
  )
  #box(width: boxWidth)[
    #align(if centered { center } else { left })[
      #img
      #text(if (description == "Campi") {emph[#description]} else { description }, size: sizeBody, weight: weightSubtitle, fill: corTitulosTextosGeral)
      #linebreak()
      #text(
        value,
        fill: corTitulosTextosGeral,
        weight: weightBody,
        size: sizeTotalizerSmall,
      )
      #linebreak()
      #if fonte != none {
        [
          #text("Fonte:", size: sizeCaption, weight: weightSubtitle)
          #text(fonte, size: sizeCaption, weight: weightBody)
        ]
      }
    ]
  ]
]
