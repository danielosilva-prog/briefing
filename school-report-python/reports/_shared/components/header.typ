// ============================================================================
// SHARED HEADER COMPONENT
// ============================================================================
// Cabeçalho padrão para relatórios SEGAPE
// ============================================================================

#import "style.typ": *

/// Cabeçalho padrão SEGAPE
///
/// Args:
///   universidade: Nome da universidade
///   sigla: Sigla da universidade (para buscar logo)
///   bgColor: Cor de fundo do cabeçalho
///   txColor: Cor do texto
///   titulo: Título customizado (se vazio, usa nome da universidade)
///   subtitulo: Subtítulo opcional
///   mostrarLogo: Se deve mostrar logo da universidade
///   logo-base-path: Caminho base para os logos (relativo ao template)
#let Header(
  universidade: "",
  sigla: "",
  bgColor: mecAzul,
  txColor: txBranco,
  titulo: "",
  subtitulo: "",
  mostrarLogo: true,
  logo-base-path: "../assets/logos/",
) = context [

  // Se não passar titulo, usa o nome da universidade
  #let header-title = if titulo == "" { universidade } else { titulo }
  #let header-sub = subtitulo

  // Se sigla for literalmente "sigla", não tenta carregar logo
  #let show-logo = mostrarLogo and sigla != "sigla" and sigla != ""

  // Caminho do logo (tenta PNG, depois SVG)
  #let logo-path = logo-base-path + upper(sigla) + ".PNG"

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

      // LADO ESQUERDO - Título e Subtítulo
      box(width: 100%, height: 100%)[
        #align(left + horizon)[
          #rect(
            width: 100%,
            height: 60%,
            inset: (left: 10pt),
            stroke: 0pt,
            fill: bgColor,
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

      // LADO DIREITO — Logo ou quadrado cinza
      box(
        height: 100%,
        width: 100%,
        stroke: (paint: bgColor, thickness: 1pt),
        inset: 4pt,
        radius: 2pt,
        fill: bgBranco,
      )[
        #align(center + horizon)[
          #if show-logo [
            #image(logo-path, height: 85%)
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
