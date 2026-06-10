// ============================================================================
// SHARED CAPA (COVER PAGE) COMPONENT
// ============================================================================
// Capa padrão para relatórios SEGAPE
// ============================================================================

#import "style.typ": *

/// Capa padrão SEGAPE
///
/// Args:
///   universidade: Nome completo da universidade
///   sigla: Sigla da universidade
///   titulo-relatorio: Título do relatório
///   subtitulo-relatorio: Subtítulo opcional
///   ano: Ano de referência
///   background-image: Imagem de fundo (opcional)
///   logo-universidade: Logo da universidade
///   logo-programa: Logo do programa (ex: Aqui Tem MEC)
///   logo-mec: Logo MEC + Governo
///   show-bandeira: Se deve mostrar bandeira do Brasil
#let Capa(
  universidade: "",
  sigla: "",
  titulo-relatorio: "Relatório",
  subtitulo-relatorio: none,
  ano: "",
  background-image: none,
  logo-universidade: none,
  logo-programa: "../assets/logos/aquiTemMECEnsinoSuperior.svg",
  logo-mec: "../assets/logos/MEC-GOV-povo.png",
  show-bandeira: true,
) = [
  #set page(
    margin: 0pt,
    background: if background-image != none [
      #image(background-image, width: 100%, height: 100%)
    ]
  )

  #grid(
    rows: (15%, 1fr, 15%),
    columns: 1,

    // HEADER - Logos institucionais
    box(
      width: 100%,
      height: 100%,
      inset: (left: 30pt, right: 30pt, top: 20pt),
    )[
      #grid(
        columns: (1fr, auto, 1fr),
        column-gutter: 10pt,
        align: horizon,

        // Logo MEC + Governo (esquerda)
        align(left)[
          #if logo-mec != none [
            #image(logo-mec, height: 60pt)
          ]
        ],

        // Bandeira Brasil (centro)
        align(center)[
          #if show-bandeira [
            #image("../assets/logos/bandeiraBrasil.svg", height: 50pt)
          ]
        ],

        // Logo da Universidade (direita)
        align(right)[
          #if logo-universidade != none [
            #image(logo-universidade, height: 70pt)
          ] else if sigla != "" [
            #let logo-path = "../assets/logos/" + upper(sigla) + ".PNG"
            #image(logo-path, height: 70pt)
          ]
        ],
      )
    ],

    // MAIN CONTENT - Título do relatório
    box(
      width: 100%,
      height: 100%,
      inset: (left: 50pt, right: 50pt),
    )[
      #align(center + horizon)[
        #block[
          // Nome da Universidade
          #text(
            universidade,
            size: 18pt,
            weight: "bold",
            fill: mecAzul,
          )

          #v(20pt)

          // Título do Relatório
          #text(
            titulo-relatorio,
            size: 28pt,
            weight: "black",
            fill: corTitulosTextosGeral,
          )

          // Subtítulo (se existir)
          #if subtitulo-relatorio != none [
            #v(10pt)
            #text(
              subtitulo-relatorio,
              size: 16pt,
              weight: "regular",
              fill: txCinza,
            )
          ]

          // Ano
          #if ano != "" [
            #v(20pt)
            #text(
              ano,
              size: 22pt,
              weight: "bold",
              fill: mecAzul,
            )
          ]
        ]
      ]
    ],

    // FOOTER - Logo do programa
    box(
      width: 100%,
      height: 100%,
      inset: (left: 30pt, right: 30pt, bottom: 20pt),
    )[
      #align(center + bottom)[
        #if logo-programa != none [
          #image(logo-programa, height: 60pt)
        ]
      ]
    ],
  )
]

/// Capa simples (sem background elaborado)
#let CapaSimples(
  titulo: "Relatório",
  subtitulo: none,
  instituicao: "",
  ano: "",
) = [
  #set page(margin: 2cm)

  #align(center + horizon)[
    #block[
      #text(
        instituicao,
        size: 16pt,
        weight: "bold",
        fill: mecAzul,
      )

      #v(30pt)

      #text(
        titulo,
        size: 24pt,
        weight: "black",
        fill: corTitulosTextosGeral,
      )

      #if subtitulo != none [
        #v(10pt)
        #text(
          subtitulo,
          size: 14pt,
          weight: "regular",
          fill: txCinza,
        )
      ]

      #if ano != "" [
        #v(30pt)
        #text(
          ano,
          size: 18pt,
          weight: "bold",
          fill: mecAzul,
        )
      ]
    ]
  ]
]
