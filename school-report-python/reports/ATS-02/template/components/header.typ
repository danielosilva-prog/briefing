#import "style.typ": *

#let Header(
  universidade: "",
  sigla: "",
  bgColor: bgVerdeEscuro,
  txColor: txBranco,
  titulo: "",
  subtitulo: "",
  mostrarLogo: true,
) = context [

  // Se não passar titulo, usa o nome da universidade
  #let header-title = if titulo == "" { universidade } else { titulo }
  #let header-sub = subtitulo

  // Se sigla for literalmente "sigla", não tenta carregar logo
  #let show-logo = mostrarLogo and sigla != "sigla"

  // Caminho do logo
  #let logo-path = if sigla == "Brasil" {
    "../assets/logos/BANDEIRABRASIL.PNG"
  } else {
    "../assets/logos/" + upper(sigla) + ".PNG"
  }

  #rect(
    width: 100%,
    height: 1.6cm,
    stroke: 0pt,
    inset: 0pt,
  )[
    #grid(
      rows: 1,
      columns: (85%, 15%),
      column-gutter: 0pt,

      box(width: 100%, height: 100%)[
        #align(left + horizon)[
          #rect(
            width: 100%,
            height: 70%,
            inset: (top:10pt, bottom:8pt,left: 8pt),
            stroke: 0pt,
            fill: rgb("0095DA"),
          )[
            #box(inset: 0pt)[
              #align(left + horizon)[

                // TÍTULO
                #box(inset: (top: 3pt))[
                  #text(
                    header-title,
                    weight: weightTitle,
                    fill: txColor,
                    size: sizeBody,
                  )
                ]
               
                #v(-5pt)

                // SUBTÍTULO
                #if header-sub != "" [
                  #text(
                    header-sub,
                    weight: weightBody,
                    fill: txColor,
                    size: sizeCaption,
                  )
                ]
              ]
            ]
          ]
        ]
      ],

      // LADO DIREITO — logo ou quadrado cinza
    
      box(
        height: 100%,
        width: 100%,
        stroke: (paint: rgb("0095DA"), thickness: 1pt),
        inset: 4pt,
        radius: 2pt,
        fill: bgBranco,
      )[        
        #align(center + horizon)[
          #if show-logo [            
            #image(logo-path)
          ] else [
            #rect(
              width: 100%,
              height: 100%,
              fill: rgb("D9D9D9"),
            )[]
          ]
        ]
      ],
    )
  ]
]