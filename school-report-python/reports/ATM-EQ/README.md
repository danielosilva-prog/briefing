# ATM-EQ Developer Guide

Relatorio `ATM-EQ` (Aqui Tem MEC Equidade) no `school-report-python`.

Este guia foi feito para continuidade de desenvolvimento: criar e ajustar queries, integrar campos no Typst, criar charts e validar a geracao end-to-end.

## 1. Arquitetura do Report

Fluxo de dados:

1. `report.yaml` define `parameters`, `queries` e `template.entry`.
2. O executor roda as queries BigQuery e gera um objeto `data`:
   - `data.queries.<query_name>`
   - `data.charts.<chart_name>` (charts em SVG base64, gerados por `charts.py`)
3. `template/main.typ`:
   - le `data` (`sys.inputs`)
   - mapeia campos explicitos em `article-args`
   - chama `#Article(..article-args)[]`
4. `template/typst-template.typ` distribui `dados` para as paginas `template/pages/*`.

Regra importante:
- Campos usados em `pages/*.typ` como `dados.campoX` devem estar mapeados em `template/main.typ`.

## 2. Estrutura Atual Relevante

- `report.yaml`: definicao do report, parametros e queries.
- `queries/*.sql`: consultas BigQuery.
- `charts.py`: bootstrap de carregamento dos modulos de chart via `@chart(...)`.
- `charts/grafico_mapa_municipio_info.py`: chart do mapa municipal (`graficoMapaMunicipio`).
- `docs/*.md`: documentacao tecnica do ATM-EQ (mapeamentos, catalogo BQ, dicionario).
- `scripts/*.py`: utilitarios locais do report (ex.: exportacao de metadados BQ).
- `scripts/generate_p03_motivos.py`: monta um pacote de revisao da P03 com um municipio representante por `motivo`, salvando artefatos JSON/CSV focados na Condicionalidade III e, opcionalmente, PDFs completos do ATM-EQ.
- `scripts/sql/*.sql`: SQLs auxiliares de apoio ao desenvolvimento.
- `scripts/atm_eq_*.sql`: SQLs principais de materializacao das tabelas derivadas no sandbox.
- `scripts/report_batch/*`: runner de geracao em lote do ATM-EQ, no mesmo espirito do batch do ATM em R.
- `scripts/materialize_inep_censo_derived_tables.py`: materializa tabelas auxiliares no sandbox para indicadores que nao devem ler `inep_censo` diretamente no runtime do report.
- `scripts/load_fundeb_base_repasse_estimativa.py`: publica no sandbox apenas os ajustes locais de `fundeb_base_repasse_estimativa` para VAAR `Previsto` de `2023` e `2024`, preservando o schema logico da base oficial.
- `template/main.typ`: orquestrador de dados para `Article`.
- `template/typst-template.typ`: composicao das paginas.
- `template/pages/*.typ`: layout e conteudo.

## 3. Queries Atuais

Definidas em `report.yaml`:

- `municipio_info` -> `queries/grafico_mapa_municipio_info.sql`
- `grafico_crescimento_vaar_fundeb_2023_2026` -> `queries/grafico_crescimento_vaar_fundeb_2023_2026.sql`
- `p2_pib_per_capita` -> `queries/p2_pib_per_capita.sql`
- `p2_numero_habitantes` -> `queries/p2_numero_habitantes.sql`
- `p2_populacao_quilombola` -> `queries/p2_populacao_quilombola.sql`
- `p2_comunidades_quilombolas_certificadas` -> `queries/p2_comunidades_quilombolas_certificadas.sql`
- `p3_condicionalidade_iii_vaar` -> `queries/p3_condicionalidade_iii_vaar.sql`
- `p2_vaar_media_uf` -> `queries/p2_vaar_media_uf.sql`
- `p2_vaar_previsto_municipio` -> `queries/p2_vaar_previsto_municipio.sql`
- `tabela_condicionalidades` -> `queries/tabela_condicionalidades.sql`
- `grafico_condicionalidades_uf` -> `queries/grafico_condicionalidades_uf.sql`
- `grafico_condicionalidades_brasil` -> `queries/grafico_condicionalidades_brasil.sql`
- `grafico_vaar_municipio_2023_2025` -> `queries/grafico_vaar_municipio_2023_2025.sql`
- `grafico_atendimento_creche_pre_escola` -> `queries/grafico_atendimento_creche_pre_escola.sql`
- `grafico_distribuicao_matriculas` -> `queries/grafico_distribuicao_matriculas.sql`
- `grafico_declaracao_racial` -> `queries/grafico_declaracao_racial.sql`
- `grafico_nivel_formacao_professores` -> `queries/grafico_nivel_formacao_professores.sql`
- `grafico_taxa_rendimento` -> `queries/grafico_taxa_rendimento.sql`
- `tabela_infraestrutura_basica` -> `queries/tabela_infraestrutura_basica.sql`

Parametro unico atual:
- `cod_ibge` (`string`)

## 4. Charts Atuais (`charts.py`)

Registrados no framework:

- `graficoCrescimentoVaarFundeb` (data: `grafico_crescimento_vaar_fundeb_2023_2026`)
- `graficoCondicionalidadesUfPercentual` (data: `grafico_condicionalidades_uf`)
- `graficoCondicionalidadesBrasilPercentual` (data: `grafico_condicionalidades_brasil`)
- `graficoValoresPrevistosVaarMunicipio` (data: `grafico_vaar_municipio_2023_2025`)
- `graficoDistribuicaoMatriculas` (data: `grafico_distribuicao_matriculas`)
- `graficoDeclaracaoRacial` (data: `grafico_declaracao_racial`)
- `graficoNivelFormacaoProfessores` (data: `grafico_nivel_formacao_professores`)
- `graficoAtendimentoCrechePreEscola` (data: `grafico_atendimento_creche_pre_escola`)
- `graficoTaxaRendimento` (data: `grafico_taxa_rendimento`)
- `graficoMapaMunicipio` (data: `municipio_info`)

Observacao importante sobre `graficoMapaMunicipio`:
- a query `grafico_mapa_municipio_info.sql` agora retorna os centroides do municipio e da capital da UF;
- o chart usa os 4 pontos (`municipioLat/Lon` e `municipioLatCap/LonCap`) para desenhar a ligacao municipio -> capital, replicando a ideia usada no ATM em R;
- se o municipio do relatorio ja for a capital, o chart colapsa para o modo de um ponto so.

Padrao esperado:
- usar `@chart("nome", data="query_name")`
- assinatura: `def chart_fn(df, ctx) -> plt.Figure | None`

## 5. Como Integrar Nova Query no Typst

Passos:

1. Criar `queries/nova_query.sql` usando `@cod_ibge` quando aplicavel.
2. Adicionar em `report.yaml`:
   - `name: nova_query`
   - `file: queries/nova_query.sql`
3. No `template/main.typ`, mapear campos:
   - `#let nova = queries.at("nova_query", default: ())`
   - `#let nova-row = nova.at(0, default: (:))`
   - adicionar em `article-args` os campos que paginas usam.
4. Usar em pagina:
   - `dados.campoNovo`

Exemplo:

```typst
#let q = queries.at("minha_query", default: ())
#let row = q.at(0, default: (:))

#let article-args = (
  ..template-params,
  meuCampo: template-params.at("meuCampo", default: row.at("meuCampo", default: "-")),
)
```

## 6. Como Integrar Novo Chart no Typst

Passos:

1. Criar chart em `charts.py` com `@chart(...)`.
2. Garantir que o `data=` referencia query existente em `report.yaml`.
3. Em `main.typ`, mapear:
   - `chartX: charts.at("nomeDoChart", default: none)`
4. Em pagina Typst:
   - charts temporarios ficam salvos na raiz de `template/`
   - paginas estao em `template/pages/`, entao use `../` no path do chart dinamico

Exemplo:

```typst
#if dados.chartX != none {
  image("../" + dados.chartX, width: 100%)
}
```

Quando `--keep-chart-files` e usado:
- os arquivos temporarios `.chart_*.svg` e `.data_*.json` ficam preservados na raiz de `template/`;
- para o ATM-EQ, isso significa:
  - `reports/ATM-EQ/template/.chart_<nome>_<id>.svg`
  - `reports/ATM-EQ/template/.data_<id>.json`

Sem essa flag:
- o comportamento padrao continua sendo apagar esses arquivos ao final da renderizacao.

## 7. Convencao no `main.typ` (Atual)

`main.typ` segue o padrao do `ATS-02`:

- `empty-data`
- leitura de `data_file` e `data`
- extracao de `metadata`, `params`, `queries`, `charts`, `template_params`
- `article-args` explicito
- `#Article(..article-args)[]`

## 8. Comandos de Teste

Gerar report completo:

```powershell
uv run schoolreport generate ATM-EQ cod_ibge=3304557 --output output/atm-eq.pdf
```

Gerar report completo preservando os SVGs temporarios dos charts:

```powershell
uv run schoolreport generate ATM-EQ cod_ibge=3304557 --output output/atm-eq.pdf --keep-chart-files
```

Inspecionar somente dados das queries:

```powershell
uv run schoolreport generate ATM-EQ cod_ibge=3304557 --data-only --output output/atm-eq.json
```

Testar especificamente a pagina P03 / Condicionalidade III:

```powershell
uv run schoolreport generate ATM-EQ cod_ibge=3304557 --data-only --output output/atm-eq-p3-check.json
uv run schoolreport generate ATM-EQ cod_ibge=3304557 --output output/atm-eq-p3-check.pdf
```

Gerar pacote de revisao da P03 por `motivo`:

```powershell
uv run python reports/ATM-EQ/scripts/generate_p03_motivos.py --skip-pdfs
uv run python reports/ATM-EQ/scripts/generate_p03_motivos.py --limit 3
uv run python reports/ATM-EQ/scripts/generate_p03_motivos.py --limit 3 --keep-chart-files
```

Uso pratico do script `generate_p03_motivos.py`:
- seleciona um municipio representante por `motivo` da tabela publica da Condicionalidade III, respeitando o ultimo `ano` disponivel de cada municipio;
- reaproveita a query oficial `queries/p3_condicionalidade_iii_vaar.sql` para salvar a saida ja transformada da P03, alinhada com a regra atual do report;
- com `--skip-pdfs`, gera apenas artefatos de revisao da P03;
- com `--limit N`, restringe a quantidade de representantes processados, util para smoke tests;
- com `--keep-chart-files`, preserva os SVGs temporarios dos charts quando os PDFs sao gerados.

Saida padrao do script:
- `output/atm-eq-p03-motivos-reais/representantes_por_motivo.json`
- `output/atm-eq-p03-motivos-reais/representantes_por_motivo.csv`
- `output/atm-eq-p03-motivos-reais/p03_revisao_por_motivo.json`
- `output/atm-eq-p03-motivos-reais/p03_revisao_por_motivo.csv`
- `output/atm-eq-p03-motivos-reais/p03_payloads/*.json`
- `output/atm-eq-p03-motivos-reais/pdfs/*.pdf` quando os PDFs sao habilitados
- `output/atm-eq-p03-motivos-reais/manifesto_pdfs.json` quando os PDFs sao habilitados

Listar reports:

```powershell
uv run schoolreport reports list
```

Rodar o batch do ATM-EQ:

```powershell
uv run python reports/ATM-EQ/scripts/report_batch/run_atm_eq_batch.py
```

Materializar tabelas derivadas do INEP censo no sandbox:

```powershell
uv run python reports/ATM-EQ/scripts/materialize_inep_censo_derived_tables.py
```

Carregar no sandbox a tabela auxiliar de ajustes locais de `fundeb_base_repasse_estimativa`:

```powershell
uv run python reports/ATM-EQ/scripts/load_fundeb_base_repasse_estimativa.py
```

Quando refazer essa carga:
- sempre que os CSVs locais derivados de `scripts/ajuste_vaar_2023.pdf` e `scripts/ajuste_vaar_2024.pdf` forem atualizados;
- sempre que a tabela sandbox de ajustes locais do VAAR `Previsto` precisar ser reconstruida;
- sempre que o schema logico espelhado de `fundeb_base_repasse_estimativa` precisar ser revalidado.

Esse comando recria/publica no sandbox:
- `fundeb_base_repasse_estimativa`

## 9. Convencoes de Arquivo e Rotulos

Padrao local atual do diretorio `ATM-EQ`:

- `UTF-8 without BOM` para `.py`, `.typ`, `.yaml`, `.yml` e `.sql`.
- `LF` como final de linha para os mesmos tipos.
- As regras locais ficam em:
  - `.gitattributes`
  - `.editorconfig`

Regras praticas para queries e charts:

- Quando a base tiver valores oficiais estaveis, prefira comparacao direta a regex.
- Para `grafico_atendimento_creche_pre_escola.sql`, a tabela materializada usa `educacao_mds_cadunico.pessoa_historico`:
  - `Creche` corresponde a `0 a 3 anos`
  - `Pré-Escola` corresponde a `4 a 6 anos`
- A saida exibida do campo `etapa` nessa query deve permanecer:
  - `Creche`
  - `Pré-Escola`
- Rotulos exibidos de raca/cor devem usar acentuacao correta quando aparecem no report ou no chart:
  - `Indígena`
  - `Não declarada`

Para indicadores derivados de `inep_censo`, o runtime do report deve ler tabelas previamente materializadas no sandbox, e nao consultar a base individualizada diretamente.

Excecoes atuais importantes:
- `grafico_distribuicao_matriculas.sql` ja foi migrada na query oficial do report para usar diretamente as tabelas publicas do Censo Escolar 2025;
- a tabela materializada `atm_eq_grafico_distribuicao_matriculas` foi mantida provisoriamente na logica anterior, para nao quebrar o fluxo ja existente enquanto a migracao completa nao e consolidada.
- `grafico_atendimento_creche_pre_escola.sql` continua lendo a tabela materializada no sandbox, agora alimentada por CadUnico.

Dataset de destino atual:
- `br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico`

## 9.1 Tabelas auxiliares no sandbox

Tabelas materializadas derivadas de INEP/CadUnico:
- `atm_eq_grafico_distribuicao_matriculas`
- `atm_eq_grafico_atendimento_creche_pre_escola`
- `atm_eq_tabela_infraestrutura_basica`

Tabela auxiliar de ajustes locais de VAAR `Previsto`:
- `fundeb_base_repasse_estimativa`

## 9.2 Consultas ativas que usam `br-mec-segape-sandbox.projeto_segape_dmape_relat_automatico`

Consultas definidas em `report.yaml` que leem diretamente tabelas do dataset sandbox:

- `grafico_atendimento_creche_pre_escola` -> `atm_eq_grafico_atendimento_creche_pre_escola`
- `grafico_crescimento_vaar_fundeb_2023_2026` -> `fundeb_base_repasse_estimativa` para `2023-2024`, com `UNION ALL` para a base oficial nos anos posteriores
- `grafico_vaar_municipio_2023_2025` -> `fundeb_base_repasse_estimativa` para `2023-2024`, com `UNION ALL` para a base oficial nos anos posteriores
- `p2_comunidades_quilombolas_certificadas` -> `comunidade_quilombola_certificada_municipio`
- `p2_vaar_previsto_municipio` -> `fundeb_base_repasse_estimativa` para `2023-2024`, com `UNION ALL` para a base oficial nos anos posteriores
- `p6_diagnostico_equidade` -> `atm_eq_pneerq_diagnostico_equidade_municipio` e `atm_eq_pneerq_diagnostico_equidade_uf`
- `tabela_infraestrutura_basica` -> `atm_eq_tabela_infraestrutura_basica`
- base: `br-mec-segape.indicador_politica_fundeb_base.fundeb_base_repasse_estimativa`
- carga: `load_fundeb_base_repasse_estimativa.py`
- ajustes locais: `scripts/local/ajuste_vaar_2023.csv` e `scripts/local/ajuste_vaar_2024.csv`
- PDFs de referencia versionados: `scripts/ajuste_vaar_2023.pdf` e `scripts/ajuste_vaar_2024.pdf`
- uso atual: complementar as queries de VAAR `Previsto` para `2023` e `2024`; anos posteriores continuam na base oficial

## 10. Dicionario de Campos do Template (Base e Ano de Referencia)

Campos mapeados em `template/main.typ` e usados nas paginas:

| Campo (`dados.*`) | Origem principal | Base BigQuery | Regra de ano de referencia |
|---|---|---|---|
| `municipio` | `municipio_info` (`municipioNome`) | `educacao_dados_mestres.municipio` | Cadastro mestre (sem ano de referencia na query). |
| `uf` | `municipio_info` (`UF`) | `educacao_dados_mestres.municipio` | Cadastro mestre (sem ano de referencia na query). |
| `p2PibPerCapita` | `p2_pib_per_capita` | `educacao_ibge_dados_abertos.ibge_pib_municipio` | Valor do ano retornado em `p2PibPerCapitaAno` (coluna explicita na query). |
| `p2PibPerCapitaAno` | `p2_pib_per_capita` | `educacao_ibge_dados_abertos.ibge_pib_municipio` | Ano explicito retornado pela query (ultimo ano com dado para o municipio). |
| `p2NumeroHabitantes` | `p2_numero_habitantes` | `educacao_ibge_dados_abertos.ibge_estimativa_populacao` | Valor do ano retornado em `p2NumeroHabitantesAno` (coluna explicita na query). |
| `p2NumeroHabitantesAno` | `p2_numero_habitantes` | `educacao_ibge_dados_abertos.ibge_estimativa_populacao` | Ano explicito retornado pela query (ultimo ano com dado para o municipio). |
| `populacaoQuilombola` | `p2_populacao_quilombola` | `educacao_ibge_dados_abertos.ibge_censo_populacao_quilombola` | Soma da populacao quilombola no ultimo ano disponivel para o municipio. |
| `populacaoQuilombolaAno` | `p2_populacao_quilombola` | `educacao_ibge_dados_abertos.ibge_censo_populacao_quilombola` | Ano explicito retornado pela query (ultimo ano com dado para o municipio). |
| `comunidadesQuilombolas` | `p2_comunidades_quilombolas_certificadas` | `projeto_segape_dmape_relat_automatico.comunidade_quilombola_certificada_municipio` (sandbox) | Contagem de comunidades certificadas para o municipio. |
| `comunidadesQuilombolasAno` | `p2_comunidades_quilombolas_certificadas` | `projeto_segape_dmape_relat_automatico.comunidade_quilombola_certificada_municipio` (sandbox) | Referencia fixa `2022`, coerente com o Censo Demografico 2022 usado na P02. |
| `p2AnoReferencia` | `p2_vaar_previsto_municipio` | `projeto_segape_dmape_relat_automatico.fundeb_base_repasse_estimativa` (sandbox) para `2023-2024` + `indicador_politica_fundeb_base.fundeb_base_repasse_estimativa` para anos posteriores | Ano da ultima combinacao `ano + portaria` com status `Previsto` para VAAR no municipio. |
| `p2ValorComplementacaoVAARAnoReferencia` | `p2_vaar_previsto_municipio` | `projeto_segape_dmape_relat_automatico.fundeb_base_repasse_estimativa` (sandbox) para `2023-2024` + `indicador_politica_fundeb_base.fundeb_base_repasse_estimativa` para anos posteriores | Soma do valor previsto de VAAR do municipio para a ultima combinacao `ano + portaria` (status `Previsto`). |
| `p2PortariaReferencia` | `p2_vaar_previsto_municipio` | `projeto_segape_dmape_relat_automatico.fundeb_base_repasse_estimativa` (sandbox) para `2023-2024` + `indicador_politica_fundeb_base.fundeb_base_repasse_estimativa` para anos posteriores | Portaria associada a estimativa mais recente de VAAR usada na P02. |
| `p2ValorComplementacaoVAARMediaUF` | `p2_vaar_media_uf` | `indicador_politica_fundeb_base.fundeb_base_repasse_estimativa` + `educacao_dados_mestres.municipio` | Valor medio previsto da UF no ano retornado em `p2ValorComplementacaoVAARMediaUFAno`. |
| `p2ValorComplementacaoVAARMediaUFAno` | `p2_vaar_media_uf` | `indicador_politica_fundeb_base.fundeb_base_repasse_estimativa` | Ano explicito da media prevista de VAAR por UF. |
| `condSelecaoDiretor` | `tabela_condicionalidades` | `educacao_politica_fundeb.fundeb_condicionalidade` | Ultimo ano disponivel para o municipio (`MAX(ano_exercicio)` combinado com indicadores). |
| `condParticipacaoSaeb` | `tabela_condicionalidades` | `educacao_politica_fundeb.fundeb_condicionalidade` | Mesmo ano de referencia da tabela de condicionalidades. |
| `condReducaoDesigualdades` | `tabela_condicionalidades` | `educacao_politica_fundeb.fundeb_condicionalidade` | Mesmo ano de referencia da tabela de condicionalidades. |
| `condRegulamentacaoIcms` | `tabela_condicionalidades` | `educacao_politica_fundeb.fundeb_condicionalidade` | Mesmo ano de referencia da tabela de condicionalidades. |
| `condReferenciaisBncc` | `tabela_condicionalidades` | `educacao_politica_fundeb.fundeb_condicionalidade` | Mesmo ano de referencia da tabela de condicionalidades. |
| `condAvancoAtendimento` | `tabela_condicionalidades` | `educacao_politica_fundeb.fundeb_indicador` | Mesmo ano de referencia da tabela de condicionalidades. |
| `condAvancoAprendizagem` | `tabela_condicionalidades` | `educacao_politica_fundeb.fundeb_indicador` | Mesmo ano de referencia da tabela de condicionalidades. |
| `condAnoReferencia` | `tabela_condicionalidades` | `educacao_politica_fundeb.fundeb_condicionalidade` + `educacao_politica_fundeb.fundeb_indicador` | Ano explicito retornado em `tabela_condicionalidades.anoReferencia`. |
| `p3PercentualRacial2019` | `p3_condicionalidade_iii_vaar` | `educacao_politica_fundeb.fundeb_resultado_condicionalidade_iii_vaar` | Proporcao de estudantes PPI com aprendizagem adequada no Saeb 2019, formatada em percentual. |
| `p3PercentualRacial2023` | `p3_condicionalidade_iii_vaar` | `educacao_politica_fundeb.fundeb_resultado_condicionalidade_iii_vaar` | Proporcao de estudantes PPI com aprendizagem adequada no Saeb 2023, formatada em percentual. |
| `p3DiferencaPercentualRacial` | `p3_condicionalidade_iii_vaar` | `educacao_politica_fundeb.fundeb_resultado_condicionalidade_iii_vaar` | Diferenca absoluta em pontos percentuais do indicador racial (`indice_ppi`). |
| `reduziuDesigualdadeRacial` | `p3_condicionalidade_iii_vaar` | `educacao_politica_fundeb.fundeb_resultado_condicionalidade_iii_vaar` | Status textual derivado do `motivo` oficial da tabela publica da Condicionalidade III. |
| `p3PercentualSocioeconomica2019` | `p3_condicionalidade_iii_vaar` | `educacao_politica_fundeb.fundeb_resultado_condicionalidade_iii_vaar` | Proporcao de estudantes de baixo NSE com aprendizagem adequada no Saeb 2019, formatada em percentual. |
| `p3PercentualSocioeconomica2023` | `p3_condicionalidade_iii_vaar` | `educacao_politica_fundeb.fundeb_resultado_condicionalidade_iii_vaar` | Proporcao de estudantes de baixo NSE com aprendizagem adequada no Saeb 2023, formatada em percentual. |
| `p3DiferencaPercentualSocioeconomica` | `p3_condicionalidade_iii_vaar` | `educacao_politica_fundeb.fundeb_resultado_condicionalidade_iii_vaar` | Diferenca absoluta em pontos percentuais do indicador socioeconomico (`indice_nse`). |
| `reduziuDesigualdadeSocioeconomica` | `p3_condicionalidade_iii_vaar` | `educacao_politica_fundeb.fundeb_resultado_condicionalidade_iii_vaar` | Status textual derivado do `motivo` oficial da tabela publica da Condicionalidade III. |
| `habilitadoCondicionalidade` | `p3_condicionalidade_iii_vaar` | `educacao_politica_fundeb.fundeb_resultado_condicionalidade_iii_vaar` | `Sim`/`Nao` a partir de `indicador_habilitado`. |
| `habilitadoCondicionalidadeMotivo` | `p3_condicionalidade_iii_vaar` | `educacao_politica_fundeb.fundeb_resultado_condicionalidade_iii_vaar` | Texto oficial do campo `motivo` da tabela publica. |
| `chartCrescimentoVaarFundeb` | `graficoCrescimentoVaarFundeb` | `projeto_segape_dmape_relat_automatico.fundeb_base_repasse_estimativa` (sandbox) para `2023-2024` + `indicador_politica_fundeb_base.fundeb_base_repasse_estimativa` para `2025-2026` | Serie fixa de `2023` a `2026`, usando `status = Previsto`; `2023` e `2024` usam os ajustes locais do sandbox e `2025-2026` seguem a base oficial. |
| `chartCondicionalidadesUf` | `graficoCondicionalidadesUfPercentual` | `educacao_politica_fundeb.fundeb_condicionalidade` | Usa o ano explicito `anoReferencia` retornado em cada linha da query UF. |
| `chartCondicionalidadesBrasil` | `graficoCondicionalidadesBrasilPercentual` | `educacao_politica_fundeb.fundeb_condicionalidade` | Usa o ano explicito `anoReferencia` retornado em cada linha da query Brasil. |
| `chartVaarMunicipio` | `graficoValoresPrevistosVaarMunicipio` | `projeto_segape_dmape_relat_automatico.fundeb_base_repasse_estimativa` (sandbox) para `2023-2024` + `indicador_politica_fundeb_base.fundeb_base_repasse_estimativa` para `2025` | Serie fixa 2023, 2024 e 2025 (VAAR `Previsto`), usando a ultima `portaria` disponivel em cada ano. |
| `chartDistribuicaoMatriculas` | `graficoDistribuicaoMatriculas` | `educacao_inep_dados_abertos.inep_censo_escolar_educacao_basica_matricula` + `educacao_inep_dados_abertos.inep_censo_escolar_educacao_basica_escola` | Consulta oficial do report usa diretamente o Censo Escolar 2025, com recorte municipal, escolas em funcionamento e quilombola por `id_tipo_localizacao_diferenciada = 3`. |
| `chartDeclaracaoRacial` | `graficoDeclaracaoRacial` | `educacao_inep_dados_abertos.censo_escolar_escola` + tabelas publicas do Censo Escolar 2025 | Serie historica do percentual de declaracao racial; mantem a serie historica anterior e acrescenta o ponto de 2025 com as tabelas publicas mais recentes. |
| `chartNivelFormacaoProfessores` | `graficoNivelFormacaoProfessores` | `educacao_inep_dados_abertos.inep_adequacao_formacao_docente_escola` + `educacao_inep_dados_abertos.censo_escolar_escola` | `MAX(ano_censo)` no municipio; classifica escolas municipais em funcionamento entre `PPI >= 60%`, `PPI < 60%` e `Quilombola`. |
| `chartAtendimentoCrechPreEscola` | `graficoAtendimentoCrechePreEscola` | `projeto_segape_dmape_relat_automatico.atm_eq_grafico_atendimento_creche_pre_escola` (sandbox) | Tabela materializada a partir de `educacao_mds_cadunico.pessoa_historico`, usando a ultima carga historica completa de 2025. |
| `tabelaInfraestruturaBasica` | query/tabela ja integrada no `main.typ` | `projeto_segape_dmape_relat_automatico.atm_eq_tabela_infraestrutura_basica` (sandbox) | Ano explicito retornado pela tabela materializada. |
| `chartTaxaRendimento` | `graficoTaxaRendimento` | `educacao_inep_dados_abertos.inep_rendimento_escolar_escola` + `educacao_inep_dados_abertos.censo_escolar_escola` | `MAX(ano)` no municipio; considera apenas aprovacao, desagrega anos iniciais e finais, e usa a mesma classificacao de perfis de escola da P05. |

Observacao importante:
- Todos os campos acima podem ser sobrescritos por `template_params` quando enviados na execucao.
- Para charts do ATM-EQ, estados vazios devem ser resolvidos no Python, que gera um SVG padronizado; o Typst apenas renderiza `dados.chartX`.

### 10.1 Valores atuais de ano de referencia (exemplo validado)

Referencia da validacao:
- comando: `uv run schoolreport generate ATM-EQ cod_ibge=3304557 --data-only --output output/atm-eq-check.json`
- municipio exemplo: `3304557` (Rio de Janeiro/RJ)

Anos retornados nas consultas:
- `grafico_crescimento_vaar_fundeb_2023_2026.anoReferencia`: `2023, 2024, 2025, 2026`
- `p2PibPerCapitaAno`: `2021`
- `p2NumeroHabitantesAno`: `2025`
- `populacaoQuilombolaAno`: `2022`
- `comunidadesQuilombolasAno`: `2022`
- `p3_condicionalidade_iii_vaar`: ano de referencia `2026` na tabela fonte; os campos textuais sao derivados do `motivo` da linha do municipio.
- `p2ValorComplementacaoVAARMediaUFAno`: `2026`
- `p2_vaar_previsto_municipio.p2AnoReferencia`: `2026`
- `p2_vaar_previsto_municipio.p2ValorComplementacaoVAARAnoReferencia`: `0.0`
- `tabela_condicionalidades.anoReferencia`: `2025`
- `grafico_condicionalidades_uf.anoReferencia`: `2025`
- `grafico_condicionalidades_brasil.anoReferencia`: `2025`
- `grafico_vaar_municipio_2023_2025.anoReferencia`: `2023, 2024, 2025`
- `grafico_distribuicao_matriculas.anoReferencia`: `2025`
- `grafico_atendimento_creche_pre_escola.anoReferencia`: `2025` (CadUnico, ultima carga historica completa disponivel na materializacao)
- `tabela_infraestrutura_basica.anoReferencia`: `2024`
- `grafico_nivel_formacao_professores.anoReferencia`: `2024`
- `grafico_declaracao_racial.anoReferencia`: faixa historica ate `2025`
- `grafico_taxa_rendimento.anoReferencia`: `2024`

## 11. Troubleshooting

### 11.0 Materializacao do INEP censo

Quando atualizar os indicadores que dependem de dado individualizado, rode:

```powershell
uv run python reports/ATM-EQ/scripts/materialize_inep_censo_derived_tables.py
```

Esse passo recria no sandbox:
- `atm_eq_grafico_distribuicao_matriculas`
- `atm_eq_grafico_atendimento_creche_pre_escola`
- `atm_eq_tabela_infraestrutura_basica`

Regra atual desses derivados:
- usa `identificacao_unica` para evitar dupla contagem;
- quando a matricula estiver em escola quilombola (`tipo_localizacao_diferenciada = '3'`), ela entra apenas em `Quilombola`;
- o recorte e de rede municipal com escola em funcionamento.

Observacao:
- no estado atual do projeto, essa etapa de materializacao continua necessaria para `grafico_atendimento_creche_pre_escola` e `tabela_infraestrutura_basica`;
- `grafico_distribuicao_matriculas` ja esta resolvida na query oficial do report com as tabelas publicas de `2025`, sem depender da tabela materializada do sandbox.

### 11.0.2 Carga dos ajustes locais de VAAR `Previsto`

Quando atualizar a tabela auxiliar usada no grafico de crescimento do VAAR, rode:

```powershell
uv run python reports/ATM-EQ/scripts/load_fundeb_base_repasse_estimativa.py
```

Esse passo recria no sandbox:
- `fundeb_base_repasse_estimativa`

Regra atual dessa carga:
- preserva o schema logico de `indicador_politica_fundeb_base.fundeb_base_repasse_estimativa`;
- publica apenas as linhas de VAAR `Previsto` de `2023` e `2024` por CSVs locais derivados dos PDFs de ajuste;
- preserva o nome textual da portaria na coluna `portaria`;
- registra o artefato local usado na carga em `tabela_origem`;
- e complementa as queries de VAAR `Previsto`, que continuam fazendo `UNION ALL` com a base oficial para os anos posteriores.

Insumos locais esperados:
- PDFs versionados: `scripts/ajuste_vaar_2023.pdf` e `scripts/ajuste_vaar_2024.pdf`
- CSVs locais nao versionados: `scripts/local/ajuste_vaar_2023.csv` e `scripts/local/ajuste_vaar_2024.csv`
- portarias esperadas:
  - `2023`: `Anexo III da Portaria MEC/MF nº 3, de 25 de abril de 2024`
  - `2024`: `Anexo III da Portaria nº 3, de 28 de Abril de 2025`

Especificamente para `grafico_atendimento_creche_pre_escola`:
- a tabela materializada usa `educacao_mds_cadunico.pessoa_historico`;
- a referencia temporal deve ser descrita no report pelo mes/ano efetivamente usado na materializacao, e nao por uma descricao interna do processo.

### 11.0.1 Tabelas publicas do Censo Escolar 2025

Aprendizado importante do projeto:
- `educacao_politica_inep_censo.inep_censo` ainda vai ate `2024`;
- `educacao_politica_inep.inep_censo` ainda vai ate `2024`;
- `educacao_inep_dados_abertos.sinopses_estatisticas_basica_sexo_raca_cor` ainda vai ate `2023`;
- para `2025`, as tabelas publicas disponiveis relevantes sao:
  - `educacao_inep_dados_abertos.inep_censo_escolar_educacao_basica_matricula`
  - `educacao_inep_dados_abertos.inep_censo_escolar_educacao_basica_escola`
  - `educacao_inep_dados_abertos.inep_censo_escolar_educacao_basica_turma`
  - `educacao_inep_dados_abertos.inep_censo_escolar_educacao_basica_docente`
- para localizacao diferenciada em `2025`, o codigo quilombola segue sendo `3`.

### 11.1 Typst: "unexpected argument"
- Verifique assinatura da funcao em `components/*.typ` ou `pages/*.typ`.
- Ajuste chamada para nomes de argumentos existentes.

### 11.2 Typst: chart dinamico "file not found"
- Se a pagina esta em `template/pages/`, use `image("../" + dados.chartX, ...)`.
- Para inspecionar o SVG final gerado pelo pipeline, use `--keep-chart-files` e abra os arquivos `.chart_*.svg` preservados em `reports/ATM-EQ/template/`.

### 11.3 Grafico vazio
- Validar primeiro `--data-only` da query.
- Confirmar se colunas esperadas pelo `charts.py` existem.

### 11.4 Problemas de encoding no Windows
- Preferir `UTF-8 without BOM` em `.sql`, `.typ`, `.yaml`, `.yml` e `.py`.
- No `ATM-EQ`, preferir tambem `LF` como final de linha.
- Em sessao local:
  - `PYTHONUTF8=1`
  - `PYTHONIOENCODING=utf-8`
- Erro tipico quando ha BOM em `.sql`: `Illegal input character "\357" at [1:1]`.

### 11.5 Paths `:Zone.Identifier`
- Sao ADS do Windows (nao sao arquivos de negocio).
- Se aparecerem no git, remover do tracking.

### 11.6 Escala de grafico e quebra de pagina (Typst + SVG dinamico)

Sintoma comum:
- grafico parece pequeno (efeito de "zoom out"), mesmo com caixa grande;
- ou grafico empurra conteudo para a pagina seguinte.

Causa principal:
- interacao entre `figsize` do Matplotlib (proporcao do SVG) e `image(..., width/height, fit: "contain")` no Typst.

Regras praticas:
- se usar `width + height + fit: "contain"`:
  - o grafico ocupa no maximo a caixa definida;
  - se o ratio do SVG for menor que o ratio da caixa, o grafico aparenta "encolhido" (sobram margens internas visuais).
- para aumentar ocupacao visual sem aumentar quebra:
  - ajustar o ratio do SVG no `charts.py` para ficar proximo ao ratio esperado pela pagina;
  - ajustar `subplots_adjust(...)` para reduzir area vazia interna do plot.
- para reduzir quebra de pagina:
  - limitar `height` da imagem no Typst (mesma regra para qualquer SVG gerado pelo Python);
  - evitar titulos/eixos redundantes dentro do grafico quando o texto ja existe na pagina.

Sequencia recomendada de ajuste:
1. Congelar baseline (PDF pipeline e PDF typst-test).
2. Ajustar primeiro `figsize` + `subplots_adjust` no Python.
3. Ajustar depois a caixa no Typst (`height`/`fit`) apenas nas paginas com overflow.
4. Validar pagina total e leitura visual do grafico.

### 11.7 Erro `lxml` no `uv sync` (Windows + Python 3.14)

Sintoma comum:
- `uv sync` falha ao construir `lxml==5.4.0`;
- erro menciona `Microsoft Visual C++ 14.0 or greater is required`.

Causa:
- o projeto usa dependencias que incluem `geobr` -> `lxml`;
- com Python 3.14 no Windows, pode nao haver wheel precompilado para `lxml`, forçando build local em C.

Correcao recomendada no projeto:
- usar Python 3.12 no ambiente virtual (alinhado com configuracao `py312` no repositorio).

Passos:
```powershell
uv python install 3.12
Remove-Item -Recurse -Force .venv
uv venv --python 3.12
uv sync
```

Validacao:
```powershell
.\.venv\Scripts\python --version
```
- esperado: `Python 3.12.x`.

Alternativa (nao recomendada para este projeto):
- instalar `Microsoft C++ Build Tools` para compilar `lxml` localmente no Python 3.14.

### 11.8 P03: regra de negocio da Condicionalidade III

Fonte principal da pagina P03:
- `educacao_politica_fundeb.fundeb_resultado_condicionalidade_iii_vaar`

Regra importante:
- os textos `reduziuDesigualdadeRacial` e `reduziuDesigualdadeSocioeconomica` nao devem ser recalculados apenas por sinal de indice, margem de erro ou `NULL`;
- a regra oficial usada no report deve seguir o mapeamento publico de `motivo` em `docs/tabela_publica_condicionalidade_III_VAAR_fundeb_2026_motivos.csv`;
- a query `p3_condicionalidade_iii_vaar.sql` implementa esse mapeamento por `motivo`, com fallback para a logica por indices apenas se surgir um motivo novo fora da tabela publica.

Casos validados manualmente no desenvolvimento:
- `1100114` (`Jaru`) -> motivo `Nao reduziu a desigualdade socioeconomica.` -> `Racial = Reduziu`, `Socioeconomica = Nao reduziu`
- `1100122` (`Ji-Parana`) -> motivo `Nao reduziu a desigualdade racial.` -> `Racial = Nao reduziu`, `Socioeconomica = Reduziu`
- `4202537` (`Bom Jesus`) -> motivo `Habilitado porque nao aumentou a desigualdade socioeconomica...` -> `Racial = Ausencia de dados suficientes`, `Socioeconomica = Desigualdade socioeconomica estavel`
- `1706258` (`Crixas do Tocantins`) -> motivo `Habilitado porque reduziu a desigualdade racial e nao aumentou a desigualdade socioeconomica.` -> `Racial = Reduziu`, `Socioeconomica = Estavel`
- `4126355` (`Serranopolis do Iguacu`) -> motivo `Habilitado porque reduziu a desigualdade socioeconomica e nao aumentou a desigualdade racial.` -> `Racial = Estavel`, `Socioeconomica = Reduziu`

### 11.9 Typst preview vs PDF final (P03)

Para a pagina P03, o preview do editor pode nao reproduzir exatamente o mesmo posicionamento do PDF final gerado pela CLI.

Aprendizado validado:
- `typst-test.typ` em preview do editor pode mostrar o simbolo de subtracao em posicao diferente do PDF;
- `uv run typst compile ...` e o PDF gerado pelo pipeline `schoolreport generate` renderizam a P03 de forma consistente entre si;
- portanto, para ajustes finos de layout na P03, use o PDF final como referencia e nao apenas o preview do editor.

Comandos uteis:

```powershell
uv run typst compile reports/ATM-EQ/template/typst-test.typ output/atm-eq-typst-test-cli.pdf
uv run schoolreport generate ATM-EQ cod_ibge=3304557 --output output/atm-eq-p3-check.pdf
```

### 11.10 Performance do mapa (`geobr`)

Aprendizado importante do desenvolvimento recente:
- a lentidao percebida no fim do pipeline (`27/28` ou `28/28`) vinha principalmente de `graficoMapaMunicipio`;
- o problema original nao era a P3 nem o PDF final, e sim o custo frio do `geobr` a cada execucao do CLI;
- como cada `schoolreport generate ...` sobe um processo novo, cache apenas em memoria nao resolvia o problema entre uma execucao e outra.

Estado atual:
- `grafico_mapa_municipio_info.sql` passou a fornecer `municipioLat`, `municipioLon`, `municipioLatCap` e `municipioLonCap`;
- o ponto do municipio nao depende mais de `geobr.read_municipality(...)` no caminho critico;
- `geobr` segue sendo usado para a geometria do estado;
- o helper de chart mantem cache persistente local em `reports/ATM-EQ/.cache/geobr/` para reduzir custo frio repetido.

Implicacao pratica:
- o ATM-EQ hoje segue estrategia mais proxima do ATM em R para o mapa;
- para regeneracoes locais sucessivas, a tendencia e o mapa ficar bem mais rapido do que na implementacao original.

### 11.11 Batch runner do ATM-EQ

Foi adicionado um runner de lote proprio do report em:
- `reports/ATM-EQ/scripts/report_batch/run_atm_eq_batch.py`

Objetivo:
- planejar ou executar a geracao em lote do `ATM-EQ` usando o mesmo fluxo real do CLI:
  - `uv run schoolreport generate ATM-EQ cod_ibge=...`

Recursos principais:
- `EXECUTE = False` por padrao (dry-run);
- filtros por `FILTER_UFS`, `FILTER_REGIOES`, `FILTER_COD_IBGE` e `MAX_MUNICIPIOS`;
- agrupamento de saida por `brasil`, `regiao` ou `uf`;
- `SKIP_EXISTING` para retomada;
- execucao sequencial ou paralela;
- logs estruturados em CSV e resumo JSON.

Saida padrao:
- `reports/ATM-EQ/scripts/report_batch/output/atm_eq_batch_prod/`
- `reports/ATM-EQ/scripts/report_batch/output/atm_eq_batch_prod/_logs/`

Configuracao inicial atual:
- o script vem preenchido com os 5 municipios de maior populacao quilombola usados na validacao do ATM-EQ:
  - `2930105` Senhor do Bonfim/BA
  - `2927408` Salvador/BA
  - `2100204` Alcantara/MA
  - `3135209` Januaria/MG
  - `1500107` Abaetetuba/PA

## 12. Checklist para Nova Entrega

Antes de commit:

1. Query adicionada e registrada no `report.yaml`.
2. Campos mapeados em `main.typ` (quando usados em paginas).
3. Chart criado em `charts.py` (se necessario).
4. Pagina Typst integrada para consumir apenas o SVG gerado pelo Python.
5. Validar encoding (`UTF-8 without BOM`) e final de linha (`LF`) nos arquivos alterados do `ATM-EQ`.
6. Teste `--data-only` e teste de PDF executados.
7. Commit em Conventional Commits.

## 13. Pendencias Atuais (Queries e Integracao)

Itens que ainda merecem acompanhamento:

1. Consolidacao das tabelas materializadas auxiliares
Status atual: `grafico_atendimento_creche_pre_escola` e `tabela_infraestrutura_basica` dependem de tabelas do sandbox.
Status atual: `grafico_distribuicao_matriculas` ja foi migrado para ler diretamente as tabelas publicas de 2025, mas a materializacao antiga foi mantida provisoriamente.
Status atual: as queries de VAAR `Previsto` leem `2023` e `2024` da tabela sandbox `fundeb_base_repasse_estimativa` e fazem `UNION ALL` com a base oficial para os anos posteriores.
Falta implementar: decidir se a tabela materializada de distribuicao continua existindo apenas como apoio operacional ou se pode ser descontinuada.

2. Consistencia editorial das paginas
Status atual: P02, P04 e P05 tiveram notas, titulos e referencias metodologicas atualizadas.
Falta implementar: manter a mesma disciplina editorial nas proximas paginas que receberem novos graficos ou mudancas metodologicas relevantes.
