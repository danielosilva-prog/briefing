#import "../components/style.typ": *

#let FichaTecnica() = [
  #set page(
    margin: (top: 1cm, right: 0pt, bottom: 2.8cm, left: 0pt),
    footer: [
      #align(center + bottom)[
        #image("../assets/background/Footer.svg", height: 100%)
      ]
    ],
  )

  #set text(
    font: "Rawline",
    size: 9pt,
  )

  #let lineSpacing = -1.25em

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
    #text(weight: weightTitle)[Secretaria de Gestão da Informação, Inovação e Avaliação de Políticas Educacionais]

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
    #text(weight: weightTitle)[Diretor de Informações Estratégicas e Inovação]

    Andrei Zwetsch Cavalheiro
    #v(lineSpacing)
    #text(weight: weightTitle)[Coordenador-Geral de Monitoramento]

    Giovanna Megumi Ishida Tedesco
    #v(lineSpacing)
    #text(weight: weightTitle)[Coordenadora-Geral de Avaliação]

    #text(weight: weightTitle)[GERENTE DE PROJETO]
    #v(lineSpacing)
    Luiz Rogério Lopes Silva

    #text(weight: weightTitle)[PESQUISA E REDAÇÃO]
    #v(lineSpacing)
    Robson Bento Santos
    #v(lineSpacing)
    Luiz Felipe Vieira Silva
    #v(lineSpacing)
    Marcelo Contatto dos Santos
    #v(lineSpacing)
    Oeber Izidoro Pereira

    #text(weight: weightTitle)[GESTÃO E ENGENHARIA DE DADOS]
    #v(lineSpacing)
    João Pedro Oliveira dos Santos
    #v(lineSpacing)
    Anderson Gregorio Marques Soares
    #v(lineSpacing)
    Escritório de Dados SEGAPE

    #text(weight: weightTitle)[PROJETO GRÁFICO]
    #v(lineSpacing)
    André José Ribeiro Guimarães
    #v(lineSpacing)
    Lara Vitória Silva Santos Barros
    #v(lineSpacing)
    Marina Lobo Ferraz

    #text(weight: weightTitle)[FONTE PRINCIPAL DOS DADOS]
    #v(lineSpacing)
    Subsecretaria de Planejamento e Orçamento (SPO)
    
    #v(20pt)

    Brasília (DF), Setembro de 2025

    #v(20pt)

    #place(bottom + center)[ #image("../assets/logos/triade-fichatecnica.png", height: 1.5cm)]


  ]
]
