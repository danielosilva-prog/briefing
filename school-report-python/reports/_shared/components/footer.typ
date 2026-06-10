// ============================================================================
// SHARED FOOTER COMPONENT
// ============================================================================
// Rodapé padrão para relatórios SEGAPE
// ============================================================================

#import "style.typ": *

/// Rodapé padrão SEGAPE com logos e numeração de páginas
///
/// Args:
///   show-page-number: Se deve mostrar número da página
///   logo-left: Caminho do logo esquerdo (padrão: logo do programa)
///   logo-right: Caminho do logo direito (padrão: MEC + Governo)
///   logo-left-height: Altura do logo esquerdo
///   logo-right-height: Altura do logo direito
#let Footer(
  show-page-number: true,
  logo-left: "../assets/logos/aquiTemMECEnsinoSuperior.svg",
  logo-right: "../assets/logos/MEC-GOV-povo.png",
  logo-left-height: 50%,
  logo-right-height: 70%,
) = context [
  #align(bottom)[
    #grid(
      columns: (1fr, auto, 1fr),
      rows: 1,
      column-gutter: 10pt,

      // LOGO ESQUERDO
      box(width: 100%, height: 100%)[
        #align(left + horizon)[
          #if logo-left != none [
            #image(logo-left, height: logo-left-height)
          ]
        ]
      ],

      // NÚMERO DA PÁGINA (CENTRO)
      box(width: 100%, height: 100%)[
        #align(center + horizon)[
          #if show-page-number [
            #text(
              counter(page).display(),
              fill: rgb("000"),
              size: sizeBody,
              weight: weightBody,
            )
          ]
        ]
      ],

      // LOGO DIREITO
      box(width: 100%, height: 100%)[
        #align(right + horizon)[
          #if logo-right != none [
            #image(logo-right, height: logo-right-height)
          ]
        ]
      ]
    )
  ]
]

/// Rodapé simples sem logos (apenas número da página)
#let FooterSimple(
  text-color: rgb("000"),
) = context [
  #align(center + bottom)[
    #text(
      counter(page).display(),
      fill: text-color,
      size: sizeBody,
      weight: weightBody,
    )
  ]
]
