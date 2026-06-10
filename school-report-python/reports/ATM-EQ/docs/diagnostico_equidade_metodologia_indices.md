# Metodologia do Diagnostico de Equidade

Planilha de referencia:
- `school-report-python/reports/ATM-EQ/docs/Diagnostico_Equidade_ATM.xlsx`

Abas principais usadas para esta documentacao:
- `Dicionario de Variáveis`
- `Definicao - Índices - Erer`
- `Definicao - Índices - EEQ`
- `Definicao - Índices - EEI`
- `Respostas - Redes Municipais`
- `Respostas - Redes Estaduais`

## Objetivo

Documentar a logica do Diagnostico de Equidade como instrumento, para orientar:
- interpretacao dos resultados
- modelagem dos dados no BigQuery
- implementacao das paginas do ATM-EQ
- futuros graficos e tabelas dinamicas

## Visao geral do diagnostico

O diagnostico e um questionario estruturado aplicado a redes municipais e estaduais.

As respostas aparecem em duas abas de fatos:
- `Respostas - Redes Municipais`
- `Respostas - Redes Estaduais`

Cada linha traz:
- identificacao geografica da rede
- marcadores de contexto, como presenca de populacao quilombola e escolas quilombolas/indigenas
- respostas do questionario em colunas `P*`
- indices ja calculados em colunas `I_*`

O instrumento esta organizado em tres eixos de indice:
- `ERER`: Educacao para as Relacoes Etnico-Raciais
- `EEQ`: Educacao Escolar Quilombola
- `EEI`: Educacao Escolar Indigena

## Estrutura dos dados

### Respostas por rede

As abas de resposta armazenam:
- variaveis de identificacao geografica
- variaveis de contexto
- perguntas codificadas (`P1A ... P46A`, com blocos multi-itens)
- indices prontos

Os indices existentes na planilha incluem:
- `I_Erer_Institucionalizacao`
- `I_Erer_Formacao`
- `I_Erer_Gestao_Escolar`
- `I_Erer_Material_Didatico_Paradidatico`
- `I_Erer_Financiamento`
- `I_Erer_Avaliacao_Monitoramento`
- `I_Erer_Geral`
- `I_EEQ_Institucionalizacao`
- `I_EEQ_Formacao`
- `I_EEQ_Gestao_Escolar`
- `I_EEQ_Material_Didatico_Paradidatico`
- `I_Geral_EEQ`
- `I_EEI_Institucionalizacao`
- `I_EEI_Formacao`
- `I_EEI_Gestao_Escolar`
- `I_EEI_Material_Didatico_Paradidatico`
- `I_Geral_EEI`

Todos sao descritos no dicionario como pontuacoes de `0 a 100`.

### Dicionario de variaveis

A aba `Dicionario de Variáveis` explicita:
- codigo da pergunta
- texto da pergunta
- item da pergunta
- tipo da variavel
- codigo da resposta
- texto da resposta
- indice ao qual a pergunta pertence

Ela e a fonte oficial para interpretar:
- o que cada `P*` significa
- o dominio dos codigos de resposta
- o que significa `999`

### Sentinelas e aplicabilidade

Pelo dicionario, `999` significa:
- `Não se aplica`

Tambem aparecem situacoes textuais como:
- `Não respondeu ao questionário`

Implicacao metodologica:
- nem toda pergunta e aplicavel a toda rede
- especialmente nos eixos `EEQ` e `EEI`, parte relevante dos indices pode ser `não se aplica`

## Eixo ERER

### Definicao geral

A aba `Definicao - Índices - Erer` informa:
- o indice geral ERER e derivado de `6` indices especificos
- cada indice especifico vai de `0 a 100`
- o indice geral e uma media ponderada desses componentes

### Subindices ERER e pesos

Os pesos apresentados na planilha sao:
- `Institucionalização`: peso `1`
- `Formação`: peso `6`
- `Gestão Escolar`: peso `6`
- `Material Didático & Paradidático`: peso `1`
- `Financiamento`: peso `2`
- `Avaliação & Monitoramento`: peso `2`

Soma dos pesos:
- `18`

Participacao relativa no indice geral:
- `Institucionalização`: `5,56%`
- `Formação`: `33,33%`
- `Gestão Escolar`: `33,33%`
- `Material Didático & Paradidático`: `5,56%`
- `Financiamento`: `11,11%`
- `Avaliação & Monitoramento`: `11,11%`

### Logica substantiva do ERER

O eixo ERER mede, em linhas gerais:
- institucionalizacao da agenda de equidade racial
- oferta de formacao continuada
- incorporacao do tema na gestao escolar
- presenca de materiais e obras pedagogicas alinhadas ao tema
- existencia de mecanismos de financiamento
- capacidade de monitoramento e avaliacao

### Exemplos de perguntas ERER por subindice

#### Institucionalizacao

Perguntas observadas na aba metodologica:
- `1.1`: normativa para implementacao da Lei `10.639/2003` e da Lei `11.645/2008`
- `5.1`: revisao curricular em cumprimento a essas leis
- `8.1`: participacao em colegiados ligados a diversidade etnico-racial
- `3.9`: existencia de equipe especifica de gestao da politica

#### Formacao

Perguntas observadas:
- `2.1`: cursos de 30h ou mais para professores
- `2.2`: cursos para diretores e coordenadores pedagogicos
- `2.3`: cursos para tecnicos de secretaria sobre preenchimento do censo
- `2.4`: palestras, oficinas e formacoes de curta duracao

Os escores crescem conforme a faixa de oferta de cursos:
- `Nenhum`
- `1 a 5 cursos`
- `6 a 10 cursos`
- `Mais de 10 cursos`

#### Gestao Escolar

Perguntas observadas:
- `3.1`: estrategias de incentivo as escolas
- `3.2`: estrategias de incentivo aos professores
- `3.3`: ERER como criterio de avaliacao de desempenho
- `3.4`: protocolo para casos de racismo ou injuria racial
- `3.5`: orientacao para incluir o tema no PPP
- `3.6` e `3.7`: conhecimentos sobre a agenda em processos de selecao de gestao escolar
- `3.8`: concursos com itens sobre as leis
- `3.10`: orientacao para inserir ERER nas disciplinas
- `3.11`: campanhas sobre autodeclaracao de raca/cor/etnia/povo

#### Material Didatico e Paradidatico

Perguntas observadas:
- `4.1`: orientacao para escolha de livros e materiais
- `4.2`: aquisicao de materiais didatico-pedagogicos por etapa/modalidade
- `4.3`: aquisicao de obras literarias relacionadas a diversidade etnico-racial

#### Financiamento

Perguntas observadas:
- `6.1`: transferencias de recursos considerando perfil socioeconomico dos estudantes
- `6.2`: reconhecimento de iniciativas por selos/premiacoes
- `6.3`: insercao da promocao da equidade racial em programas do PAR

#### Avaliacao e Monitoramento

Perguntas observadas na metodologia e no dicionario:
- `7.1`: existencia de indicadores de monitoramento
- `7.2`: realizacao de avaliacao da implementacao
- `7.6`: cadastro de demanda por vaga de creche com criterio socioeconomico
- `7.6.1`: priorizacao de vagas a partir desse criterio

## Eixo EEQ

### Definicao geral

A aba `Definicao - Índices - EEQ` informa:
- o indice geral EEQ e derivado de `4` indices especificos
- cada subindice vai de `0 a 100`
- o indice geral e uma media ponderada

### Subindices EEQ e pesos

Pesos observados:
- `Institucionalização`: peso `3`
- `Formação`: peso `4`
- `Gestão Escolar`: peso `4`
- `Material Didático & Paradidático`: peso `3`

Soma dos pesos:
- `14`

Participacao relativa:
- `Institucionalização`: `21,43%`
- `Formação`: `28,57%`
- `Gestão Escolar`: `28,57%`
- `Material Didático & Paradidático`: `21,43%`

### Logica substantiva do EEQ

O eixo EEQ mede a capacidade da rede de:
- estruturar a modalidade de educacao escolar quilombola
- formar profissionais para ela
- incorporar o tema em selecao e gestao
- oferecer materiais e insumos especificos para comunidades quilombolas

### Perguntas observadas no EEQ

#### Institucionalizacao
- `9.8`: participacao em colegiados relacionados a Educacao Escolar Quilombola
- `9.6`: existencia de equipe especifica responsavel pela modalidade

#### Formacao
- `9.1`: cursos para professores sobre as DCNs da Educacao Escolar Quilombola
- `9.2`: cursos para diretores e coordenadores

#### Gestao Escolar
- `9.3`: conhecimentos sobre a modalidade em processos de escolha da gestao
- `9.4`: concursos com itens relativos as diretrizes da modalidade
- `9.5`: acesso a recursos do PNAE para quilombolas

#### Material Didatico e Paradidatico
- `4.2`: item especifico para Educacao Escolar Quilombola
- `4.3`: item especifico para Educacao Escolar Quilombola
- `9.7`: producao e distribuicao de materiais didaticos especificos para comunidades quilombolas

### Aplicabilidade

O dicionario marca varios indicadores EEQ com:
- `999 = Não se aplica`

Isso sugere que o eixo EEQ so deve ser lido como comparavel quando a rede tem contexto ou responsabilidade pertinente a educacao escolar quilombola.

## Eixo EEI

### Definicao geral

A aba `Definicao - Índices - EEI` informa:
- o indice geral EEI e derivado de `4` indices especificos
- cada subindice vai de `0 a 100`
- o indice geral e uma media ponderada

### Subindices EEI e pesos

Pesos observados:
- `Institucionalização`: peso `3`
- `Formação`: peso `4`
- `Gestão Escolar`: peso `4`
- `Material Didático & Paradidático`: peso `3`

Soma dos pesos:
- `14`

Participacao relativa:
- `Institucionalização`: `21,43%`
- `Formação`: `28,57%`
- `Gestão Escolar`: `28,57%`
- `Material Didático & Paradidático`: `21,43%`

### Logica substantiva do EEI

O eixo EEI mede a capacidade da rede de:
- institucionalizar a modalidade de educacao escolar indigena
- ofertar formacao continuada associada a ela
- considerar a modalidade em selecao e gestao escolar
- produzir ou adquirir materiais especificos para povos indigenas

### Perguntas observadas no EEI

#### Institucionalizacao
- `10.8`: participacao em reunioes dos Territorios Etnoeducacionais Indigenas e colegiados da modalidade
- `10.6`: existencia de equipe especifica responsavel pela modalidade

#### Formacao
- `10.1`: cursos para professores
- `10.2`: cursos para diretores e coordenadores

#### Gestao Escolar
- `10.3`: consideracao das diretrizes da modalidade em selecao de gestao
- `10.4`: concursos com itens relativos a modalidade
- `10.5`: acesso a recursos do PNAE para indigenas

#### Material Didatico e Paradidatico
- `4.2`: item especifico para Educacao Escolar Indigena
- `4.3`: item especifico para Educacao Escolar Indigena
- `10.7`: producao e distribuicao de materiais especificos para povos indigenas

### Aplicabilidade

Assim como em EEQ, o dicionario marca varios indicadores EEI com:
- `999 = Não se aplica`

## O que a planilha nos permite afirmar sobre a logica do diagnostico

### 1. O diagnostico combina respostas brutas e indices calculados

A planilha ja entrega:
- respostas por pergunta
- indices parciais
- indices gerais

Isso significa que o diagnostico tem duas camadas:
- camada de questionario
- camada de consolidacao analitica

### 2. O instrumento nao mede apenas declaracoes formais

Os blocos de perguntas cobrem:
- normativa e institucionalizacao
- formacao
- gestao
- materiais
- financiamento
- monitoramento

Portanto, o diagnostico tenta captar capacidade de implementacao, nao apenas adesao formal.

### 3. ERER tem maior peso em formacao e gestao escolar

Pelos pesos, o ERER prioriza:
- formacao
- gestao escolar

Juntos, esses dois blocos respondem por:
- `66,67%` do indice geral ERER

### 4. EEQ e EEI sao eixos mais focalizados

Eles nao usam financiamento nem avaliacao/monitoramento como subindices autonomos.
Sua estrutura esta concentrada em:
- institucionalizacao
- formacao
- gestao
- materiais

### 5. A aplicabilidade importa tanto quanto a pontuacao

Como ha codigos de `não se aplica`, especialmente em EEQ e EEI, e metodologicamente incorreto:
- tratar `999` como zero
- comparar indiscriminadamente redes para esses eixos sem considerar contexto

## Implicacoes para o ATM-EQ

### 1. A P06 pode ser totalmente dinamizada

A planilha contem base suficiente para alimentar:
- cards superiores
- KPIs textuais
- mosaico dos 7 indices ERER
- comparativos EEQ e EEI

### 2. Os indices devem ser usados como indicadores derivados oficiais

Para o report, o melhor caminho e consumir:
- os `I_*` ja calculados

E nao recalcular a metodologia na query da pagina, a menos que haja necessidade de auditoria.

### 3. Perguntas `P*` continuam importantes

Elas sao necessarias quando a pagina quer mostrar:
- frases interpretativas
- respostas textuais resumidas
- status tipo `Realizou`, `Não realizou`, `Adota`, `Não adota`

## Pontos que ainda merecem refinamento

### 1. Consolidar a metodologia completa por pergunta

As abas de definicao trazem muitos pontos por resposta.
Ainda cabe um segundo documento mais detalhado com:
- todas as perguntas
- todas as respostas
- pontuacao no subindice
- pontuacao no indice geral

### 2. Definir regras de comparacao para P06

A planilha permite comparar:
- municipio com municipios da mesma UF
- municipio com rede estadual da UF
- possivelmente municipio com Brasil

Mas isso precisa de decisao funcional explicita.

### 3. Tratar `não respondeu` e `não se aplica` como conceitos distintos

Eles nao significam a mesma coisa:
- `não respondeu` aponta ausencia de informacao
- `não se aplica` aponta inaplicabilidade substantiva

Essa distincao deve aparecer nas futuras visualizacoes.
