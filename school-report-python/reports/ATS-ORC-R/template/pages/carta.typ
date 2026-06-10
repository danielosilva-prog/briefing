#import "../components/style.typ": *

#let Carta() = [
  #set page(
    margin: (top: 2cm, right: 0pt, bottom: 2.8cm, left: 0pt),
    footer: [
      #align(center + bottom)[
        #image("../assets/background/Footer.svg", height: 100%)
      ]
    ],
  )
  #set text(
    font: "Rawline",
    size: sizeBody,
  )
  #set par(
    leading: 1.15em,
  )
  #box(
    inset: 2cm,
  )[
    #text(weight: weightTitle, size: sizeSubtitle)[
      Prezado(a) Prefeito(a),
    ]
    #linebreak()
    #linebreak()
    #par[
      Uma educação transformadora não se constrói sozinha. Ela é fruto do esforço coletivo de muitas mãos: professores, gestores escolares, pais e alunos que, com dedicação, compartilham a certeza de que o futuro só pode ser alcançado por meio da educação.
    ]
    #linebreak()
    #par[
      No Ministério da Educação, acreditamos que uma educação de qualidade com equidade só se faz através de muito diálogo e colaboração. É por isso que estamos aqui para caminhar ao lado de vocês, prefeitos e prefeitas, na missão de garantir melhores oportunidades para nossas crianças e jovens.
    ]
    #linebreak()
    #par[
      Este documento traz uma síntese de indicadores educacionais que mostram os desafios e as oportunidades específicas de seu município na educação básica. Nele, você poderá identificar a situação de seu município em relação a diversas políticas e programas do Ministério da Educação, além de dados sobre recursos financeiros disponíveis, como o Fundeb e o Salário-Educação. Cada iniciativa apresentada foi pensada para apoiar você nesse importante trabalho de gestão da educação.
    ]
    #linebreak()
    #par[
      Além disso, um diagnóstico mais detalhado, com ainda mais indicadores, estará disponível no Novo PAR, para você e a equipe da Secretaria Municipal de Educação. O Novo PAR é uma ferramenta essencial para compreender melhor as lacunas e necessidades do seu município, apoiando cada ente na elaboração de um planejamento eficiente e assertivo para atingimento dos objetivos e metas da educação básica. A partir desse planejamento individualizado e pactuado com o MEC, será possível prestar apoio técnico e financeiro de forma mais precisa e alinhada às realidades locais.
    ]
    #linebreak()
    #par[
      Desejo a você muito sucesso na gestão de seu município. Que possamos, juntos, oferecer uma educação com qualidade e equidade, capaz de transformar vidas e construir um futuro melhor para nossas crianças e jovens.
    ]
    #linebreak()
    #text(weight: weightTitle, size: sizeSubtitle)[
      Conte conosco!
    ]
  ]
]
