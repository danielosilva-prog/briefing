#import "style.typ": *

#let Footer = context [
  #align(bottom)[
    #grid(
      columns: 3,
      rows: 1,
      box(width: 100%, height: 100%)[ 
        #align(left + horizon)[
          #image("../assets/logos/aquiTemMECEnsinoSuperior.svg", height: 50%)
        ]
      ],
      box(width: 100%, height: 100%)[ 
        #align(center + horizon)[
          #text(
           
            counter(page).display(),
            fill: rgb("000"),
            size: sizeBody,
            weight: weightBody,
          )
        ]
      ],
      box(width: 100%, height: 100%)[ 
        #align(right + horizon)[
          #image("../assets/logos/MEC-GOV-povo.png", height: 70%)
        ]
      ]
    )
  ]
]
