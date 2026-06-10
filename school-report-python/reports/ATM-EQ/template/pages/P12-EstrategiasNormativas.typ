#import "../components/style.typ": *

#import "../components/header.typ": Header

#let EstrategiasNormativas(..args) = {

  let dados = args.at(0)

  [

    #Header(
      titulo: [#v(.58cm)#text(weight: "extrabold")[Normativo]],
      municipio: dados.municipio,
      uf: dados.uf,
      bgColor: rgb("265793"),
      esconderDoSumario: false,
      textoDoSumario: "Normativo"
    )

    #v(-.3cm)

    #box(
      inset: (right: .22cm)
    )[
      #set text(fill: black, size: sizeBodySmall, tracking: -.025em)

      #set par(spacing: 1.5em)

      #box(
        fill: rgb("EAEAEA50"),
        inset: (top: .7cm, right: .6cm, bottom: .6cm, left: .6cm),
        radius: (top-left: 20pt, bottom-right: 20pt)
      )[

        #set par(leading: 1.15em, spacing: 18pt)

        A trajetória da educação brasileira rumo à equidade e ao reconhecimento de sua diversidade étnico-racial é marcada por importantes marcos legais. Abaixo, reunimos os principais instrumentos normativos que estruturam essa política pública fundamental, demonstrando um esforço do Estado brasileiro para reparar dívidas históricas e garantir direitos educacionais à população negra, quilombola e indígena.​

        #v(-.9cm)
​
        #align(left + horizon)[
          #box(height: .6cm, fill: pneerqLaranja, radius: 50%, inset: (x: .25cm, top: .15cm))[
                #text(size: 12pt, weight: "black", fill: white)[2025]]
        ]

        #v(-.3cm)

        - #link("https://www.gov.br/mec/pt-br/pneerq/PDF/portarias8388392025.pdf")[#strong[#underline("Portaria nº 838/2025")]]: estabelece a Câmara Tripartite de Gestão Técnica e Monitoramento (CGTM)​
        - #link("https://www.gov.br/mec/pt-br/pneerq/PDF/portarias8388392025.pdf")[#strong[#underline("Portaria nº 839/2025")]]: institui a Câmara Técnica de Participação Social (CTPS)​
        - #link("http://www.in.gov.br/web/dou/-/portaria-n-207-de-2-de-abril-de-2025-621884719")[#strong[#underline("Portaria nº 207, de 2 de abril de 2025")]]: institui o Comitê Permanente de Monitoramento e Avaliação do Programa de Bolsa Permanência - CPMAPBP, no âmbito do Ministério da Educação.​

        #v(-.25cm)

        #align(left + horizon)[
          #box(height: .6cm, fill: pneerqLaranja, radius: 50%, inset: (x: .25cm, top: .15cm))[
                #text(size: 12pt, weight: "black", fill: white)[2024]]
        ]
        #v(-.3cm)

        - #link("https://pesquisa.in.gov.br/imprensa/jsp/visualiza/index.jsp?data=31/10/2024&jornal=515&pagina=71&totalArquivos=516")[#strong[#underline("Portaria nº 1.082, de 29 de outubro de 2024")]]: altera a Portaria MEC nº 470, de 14 de maio de 2024, que institui a PNEERQ.​
        - #link("https://www.in.gov.br/en/web/dou/-/portaria-n-470-de-14-de-maio-de-2024-559544343")[#strong[#underline("Portaria nº 470, de 14 de maio de 2024")]]: institui a Política Nacional de Equidade, Educação para as Relações Étnico-Raciais e Educação Escolar Quilombola (PNEERQ).​

        #v(-.25cm)

        #align(left + horizon)[
          #box(height: .6cm, fill: pneerqLaranja, radius: 50%, inset: (x: .25cm, top: .15cm))[
                #text(size: 12pt, weight: "black", fill: white)[2023]]
        ​]
        #v(-.3cm)

        - #link("https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14723.htm")[#strong[#underline("Lei nº 14.723, de 13 de novembro de 2023")]]: atualiza e amplia as ações afirmativas para ingresso nas instituições federais de educação superior e de ensino técnico de nível médio para estudantes pretos, pardos, indígenas, quilombolas e com deficiência.​
        - #link("https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/decreto/d11786.htm#:~:text=DECRETO%20N%C2%BA%2011.786%2C%20DE%2020,e%20o%20seu%20Comit%C3%AA%20Gestor")[#strong[#underline("Decreto nº 11.786")]], de 20 de novembro de 2023, institui a Política Nacional de Gestão Territorial e Ambiental Quilombola e seu comitê gestor.​
        - #link("https://www.gov.br/fnde/pt-br/acesso-a-informacao/legislacao/resolucoes/2024/resolucao-no-17-de-15-de-agosto-de-2024#:~:text=Disp%C3%B5e%20sobre%20as%20orienta%C3%A7%C3%B5es%2C%20diretrizes,municipais%20e%20do%20Distrito%20Federal")[#strong[#underline("Portaria nº 988, de 23 de maio de 2023")]]: institui a Comissão Nacional de Educação Escolar Quilombola.
        - #strong[#underline("Portaria n. 991, de 23 de maio de 2023")]: institui a Comissão Nacional para a Educação das Relações Étnico-Raciais e para o Ensino de História e Cultura Afro-Brasileira e Africana – Cadara.​
        #v(-.25cm)

        #align(left + horizon)[
          #box(height: .6cm, fill: pneerqLaranja, radius: 50%, inset: (x: .25cm, top: .15cm))[
                #text(size: 12pt, weight: "black", fill: white)[2016]]
        ]
        #v(-.3cm)

        - #link("https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2016/decreto/d8750.htm")[#strong[#underline("Decreto n° 8.750")]], de 9 de maio de 2016, que institui o Conselho Nacional de Povos e Comunidades Tradicionais.​

        #v(-.25cm)

        #align(left + horizon)[
          #box(height: .6cm, fill: pneerqLaranja, radius: 50%, inset: (x: .25cm, top: .15cm))[
                #text(size: 12pt, weight: "black", fill: white)[2012]]
        ​]
        #v(-.3cm)

        - #link("https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2012/lei/l12711.htm")[#strong[#underline("Lei nº 12.711, de 29 de agosto de 2012")]]: dispõe sobre o ingresso nas universidades federais e nas instituições federais de ensino técnico de nível médio, bem como dá outras providências.​
        - #link("http://portal.mec.gov.br/index.php?option=com_docman&view=download&alias=11091-pceb016-12&category_slug=junho-2012-pdf&Itemid=30192")[#strong[#underline("Parecer CNE/CEB nº 16/2012")]], sobre as Diretrizes Curriculares Nacionais para a Educação Escolar Quilombola, aprovado em 5 de junho de 2012.
        - #link("http://portal.mec.gov.br/index.php?option=com_docman&view=download&alias=11963-rceb008-12-pdf&category_slug=novembro-2012-pdf&Itemid=30192")[#strong[#underline("Resolução nº 8/2012")]], que define as #link("http://portal.mec.gov.br/index.php?option=com_docman&view=download&alias=11963-rceb008-12-pdf&category_slug=novembro-2012-pdf&Itemid=30192")[#underline("Diretrizes Curriculares Nacionais para a Educação Escolar Quilombola na Educação Básica")].​

        #v(-.25cm)

        #align(left + horizon)[
          #box(height: .6cm, fill: pneerqLaranja, radius: 50%, inset: (x: .25cm, top: .15cm))[
                #text(size: 12pt, weight: "black", fill: white)[2010]]
        ​]
        #v(-.3cm)

        - #link("https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2010/lei/l12288.htm")[#strong[#underline("Lei nº 12.288, de 20 de julho de 2010")]]: institui o Estatuto da Igualdade Racial.​

        #v(-.25cm)

        #align(left + horizon)[
          #box(height: .6cm, fill: pneerqLaranja, radius: 50%, inset: (x: .25cm, top: .15cm))[
                #text(size: 12pt, weight: "black", fill: white)[2008]]
        ]
        #v(-.3cm)

        - #link("https://www.planalto.gov.br/ccivil_03/leis/2003/l10.639.htm")[#strong[#underline("Lei nº 10.639, de 9 de janeiro de 2003")]], modificada pela #link("https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2008/lei/l11645.htm")[#strong[#underline("Lei nº 11.645/2008")]]: torna obrigatória a inclusão do ensino sobre a história e cultura afro-brasileira e indígena nos currículos escolares.​

        #v(-.25cm)

        #align(left + horizon)[
          #box(height: .6cm, fill: pneerqLaranja, radius: 50%, inset: (x: .25cm, top: .15cm))[
                #text(size: 12pt, weight: "black", fill: white)[2004]]
        ​]
        #v(-.3cm)

        - #strong[#underline("Resolução CNE/CP nº 1/2004")] institui as Diretrizes Curriculares Nacionais para a Educação das Relações Étnico-Raciais e para o Ensino de História e Cultura Afro-Brasileira e Africana, conforme o Artigo 26-A da LDB (Lei nº 9.394/1996).

        #v(-1cm) ​

        #align(left + horizon)[
          #box(height: .6cm, fill: pneerqLaranja, radius: 50%, inset: (x: .25cm, top: .15cm))[
                #text(size: 12pt, weight: "black", fill: white)[2003]]
        ​]
        #v(-.3cm)

        - #strong[#underline("Lei nº 10.639, de 9 de janeiro de 2003")], alterou a LDB (Lei nº 9.394/1996) para tornar obrigatório o ensino de História e Cultura Afro-Brasileira em escolas públicas e privadas de ensino fundamental e médio no Brasil.​
      ]
    ]
  ]
}