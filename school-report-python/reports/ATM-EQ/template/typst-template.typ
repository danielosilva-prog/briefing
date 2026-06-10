// TYP .
// import styles
#import "./components/style.typ": *

// import components
#import "./components/header.typ": Header
#import "./components/footer.typ": Footer

// import páginas de apoio
#import "pages/Capa.typ": Capa
#import "pages/FichaTecnica.typ": FichaTecnica
#import "pages/FichaTecnica2.typ": FichaTecnica
#import "pages/Sumario.typ": Sumario
#import "pages/Plateduc.typ": Plateduc
#import "pages/Diagnostico.typ": Diagnostico
#import "pages/ContraCapa.typ": ContraCapa

// import páginas de conteúdo
#import "pages/P01-Introducao.typ": Introducao
#import "pages/P02-ComplementacaoVAAR.typ": ComplementacaoVAAR
#import "pages/P03-Condicionalidade.typ": Condicionalidade
#import "pages/P04-DiagnosticoCensoDemografico.typ": DiagnosticoCensoDemografico
#import "pages/P05-DiagnosticoCensoEscolar.typ": DiagnosticoCensoEscolar
#import "pages/P06-DiagnosticoEquidade.typ": DiagnosticoEquidade
#import "pages/P07-EstrategiasPlanoDeAcao.typ": EstrategiasPlanoDeAcao
#import "pages/P08-EstrategiasAspectosRelacionais.typ": EstrategiasAspectosRelacionais
#import "pages/P09-EstrategiasAspectosPedagogicos.typ": EstrategiasAspectosPedagogicos
#import "pages/P10-EstrategiasAspectosPedagogicos02.typ": EstrategiasAspectosPedagogicos02
#import "pages/P11-EstrategiasAspectosPedagogicos03.typ": EstrategiasAspectosPedagogicos03
#import "pages/P12-EstrategiasNormativas.typ": EstrategiasNormativas
#import "pages/P13-EstrategiasAspectosFinanceiros.typ": EstrategiasAspectosFinanceiros
#import "pages/P14-Notas.typ": Notas

#let Article(..args) = {

  let dados = args.named()

  set document(title: dados.title)

  set page(
    margin: (top: .25cm, right: .75cm, bottom: 1.5cm, left: .75cm),
    footer: Footer(),
  )

  set text(
    font: "Rawline",
    size: sizeBody,
  )

  set par(
    leading: 1em,
    spacing: 1.5em,
    justify: true,
  )

  Capa(dados)
  //Sumario
  Introducao(dados)
  ComplementacaoVAAR(dados)
  Condicionalidade(dados)
  DiagnosticoCensoDemografico(dados)
  DiagnosticoCensoEscolar(dados)
  DiagnosticoEquidade(dados)
  EstrategiasPlanoDeAcao(dados)
  EstrategiasAspectosRelacionais(dados)
  EstrategiasAspectosPedagogicos(dados)
  EstrategiasAspectosPedagogicos02(dados)
  EstrategiasAspectosPedagogicos03(dados)
  EstrategiasAspectosFinanceiros(dados)
  EstrategiasNormativas(dados)
  //Notas(dados)
  
  //Diagnostico()
  //Plateduc()
  FichaTecnica()
  ContraCapa()
}
