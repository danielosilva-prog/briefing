#import "../components/style.typ": *

#let FichaTecnica() = [
  #set page(
    margin: (top: .5cm, right: 0pt, bottom: 2.8cm, left: 0pt),
    footer: [
      #align(center + bottom)[
        #image("../assets/backgrounds/footer.svg", width: 100%)
      ]
    ],
  )

  #set text(
    font: "Rawline",
    size: 9pt,
  )

  #let lineSpacing = -1.45em

  #set par(
    spacing: 2.25em,
    leading: 1em,
  )

  #v(30pt)
  #align(center)[

    // Governo Federal
    #text(weight: weightSubtitle)[REPÚBLICA FEDERATIVA DO BRASIL]

    Luiz Inácio Lula da Silva
    #v(lineSpacing)
    #text(weight: weightTitle)[Presidente da República Federativa do Brasil]

    Camilo Sobreira de Santana
    #v(lineSpacing)
    #text(weight: weightTitle)[Ministro de Estado da Educação]

    Evânio Antônio de Araújo Júnior
    #v(lineSpacing)
    #text(weight: weightTitle)[Secretário de Gestão da Informação, Inovação e Avaliação de Políticas Educacionais]

    Zara Figueiredo
    #v(lineSpacing)
    #text(weight: weightTitle)[Secretária de Educação Continuada, Alfabetização de Jovens e Adultos, Diversidade e Inclusão]

    // Ficha Técnica
    #text(weight: weightSubtitle)[FICHA TÉCNICA]

    #text(weight: weightTitle)[COORDENAÇÃO DO PROJETO]

    Camila Porto Fasolo
    #v(lineSpacing)
    #text(weight: weightTitle)[Diretora de Monitoramento e Avaliação de Políticas Educacionais]

    Daniel Lopes de Castro
    #v(lineSpacing)
    #text(weight: weightTitle)[Diretor de Programa]

    Fernando de Barros Filgueiras
    #v(lineSpacing)
    #text(weight: weightTitle)[Diretor de Inovação, Estratégia Digital e Conhecimento]

    Andrei Zwetsch Cavalheiro
    #v(lineSpacing)
    #text(weight: weightTitle)[Coordenador-Geral de Monitoramento]

    Lucas Evencio Soares Dutra
    #v(lineSpacing)
    #text(weight: weightTitle)[Coordenador-Geral de Informações Estratégicas em Educação]

    Giovanna Megumi Ishida Tedesco
    #v(lineSpacing)
    #text(weight: weightTitle)[Coordenadora-Geral de Avaliação]

    #text(weight: weightTitle)[GERENTE DE PROJETO]
    #v(lineSpacing)
    Luiz Rogério Lopes Silva

    #text(weight: weightTitle)[CONCEPÇÃO, PESQUISA E REDAÇÃO]
    #v(lineSpacing)
    Caio de Oliveira Callegari
    #v(lineSpacing)
    Deborah Piego
    #v(lineSpacing)
    Francisco Moraes da Costa Marques
    #v(lineSpacing)
    Lara Oliveira Vilela
    #v(lineSpacing)
    Leticia Cortellazzi Garcia

    #text(weight: weightTitle)[GESTÃO E ENGENHARIA DE DADOS]
    #v(lineSpacing)
    Anderson Gregorio Marques Soares
    #v(lineSpacing)
    Eduardo Chagas Lustoza

    #text(weight: weightTitle)[PROJETO GRÁFICO]
    #v(lineSpacing)
    André José Ribeiro Guimarães
    #v(lineSpacing)
    Marina Lobo Ferraz

    #text(weight: weightTitle)[FONTE PRINCIPAL DOS DADOS]
    #v(lineSpacing)
    Censo da Educação Básica - Inep (2025)
    
    #v(10pt)

    Brasília (DF), Março de 2026

    #place(bottom + center)[ #image("../assets/logos/fichatecnica.png", height: 1.5cm)]


  ]
]
