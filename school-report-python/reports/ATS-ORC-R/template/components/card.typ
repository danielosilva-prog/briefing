#import "./style.typ": *

#let Card(
  value: "",
  legend: "",
  color: txBranco,
  backgroundColor: txCinza,
  width: 100%,
  trackingText: 0pt
) = context [
  #rect(
    fill: backgroundColor,
    inset: (x: 2pt, top: 10pt, bottom: 6pt),
    width: width
  )[
    #align(center)[
      #set par(justify: false, leading: 1em)
      #text(
        size: sizeSubtitle*.9,
        tracking: -.5pt,
        weight: weightSubtitle,
        fill: color,
        hyphenate: false
      )[#value]
      #v(-6pt)
      #align(center)[#text(size: sizeCaption*.85, fill: color, tracking: -.25pt)[#legend]]
    ]
  ]
]

