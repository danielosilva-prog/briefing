#import "../components/style.typ": *

#let ComoOsDadosDevemSerLidos = [
  #set page(
    margin: (top: 2cm, right: 0cm, bottom: 2.8cm, left: 0cm),
    footer: [
      #align(center + bottom)[
        #image("../assets/background/Footer-Branco.svg", height: 100%)
      ]
    ],
    fill: rgb("#0095DA"),
  )

  #set text(
    font: "Rawline",
    size: sizeBody,
    tracking: 0.3pt,
    weight: "semibold",
    fill: txBranco,
  )

  #set par(
    leading: 14pt,
    justify: true,
    first-line-indent: 1cm,
  )

  #box(inset: (x: 2cm))[ ]
]
