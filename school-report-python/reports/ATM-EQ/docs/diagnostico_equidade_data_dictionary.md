# Dicionario Tecnico - Diagnostico de Equidade

Planilha de referencia:
- `school-report-python/reports/ATM-EQ/docs/Diagnostico_Equidade_ATM.xlsx`

Abas usadas:
- `Dicionario de Variáveis`
- `Respostas - Redes Municipais`
- `Respostas - Redes Estaduais`

## Objetivo

Consolidar o dicionario tecnico do questionario do Diagnostico de Equidade, cobrindo:
- codigo da pergunta
- texto da pergunta
- itens
- dominio de respostas
- indice associado

Este documento descreve a logica do instrumento, nao apenas a pagina P06.

## Convencoes gerais

### Granularidade das respostas

As respostas aparecem nas abas de fatos como colunas:
- `P1A ... P46A`
- alguns blocos possuem varios itens por pergunta, como:
  - `P1A ... P1E`
  - `P18A ... P18K`
  - `P19A ... P19K`
  - `P45A ... P45H`

### Dominios recorrentes

Alguns padroes de resposta se repetem:
- binario:
  - `0 = Não`
  - `1 = Sim`
- contagem em faixas:
  - `0 = Nenhum`
  - `1 = 1 a 5`
  - `2 = 6 a 10`
  - `3 = Mais de 10`
- concursos:
  - `0 ... 5`, representando quantidade de concursos ou processos
- aplicabilidade:
  - `999 = Não se aplica`

### Indices associados

Os campos do dicionario associam cada pergunta a um dos eixos:
- `Índice de Institucionalizacao - Erer`
- `Índice de Formação - Erer`
- `Índice de Gestao Escolar - Erer`
- `Índice de Material Didatico e Paradidatico - Erer`
- `Índice de Financiamento - Erer`
- `Índice de Avaliacao e Monitoramento - Erer`
- `Índice de Institucionalizacao - EEQ`
- `Índice de Formação - EEQ`
- `Índice de Gestao Escolar - EEQ`
- `Índice de Material Didatico e Paradidatico - EEQ`
- `Índice de Institucionalizacao - EEI`
- `Índice de Formação - EEI`
- `Índice de Gestao Escolar - EEI`
- `Índice de Material Didatico e Paradidatico - EEI`

## Variaveis de contexto

`POP_QUILOMBOLA`
- texto: existe populacao quilombola no municipio
- dominio:
  - `0 = Não`
  - `1 = Sim`
- indice: `-`

`ESCOLAS_QUILOMBOLAS`
- texto: existem escolas quilombolas
- dominio:
  - `0 = Não`
  - `1 = Sim`
- indice: `-`

`ESCOLAS_INDIGENAS`
- texto: existem escolas indígenas
- dominio:
  - `0 = Não`
  - `1 = Sim`
- indice: `-`

## Bloco 1 - Normativa e institucionalizacao ERER

`P1`
- pergunta:
  - `1.1. A Secretaria de Educação possui alguma normativa para a implementação da Lei nº 10.639/2003 e da Lei nº 11.645/2008 e de suas Diretrizes nas unidades escolares?`
- indice:
  - `Índice de Institucionalizacao - Erer`
- itens:
  - `A`: parecer
  - `B`: portaria
  - `C`: resolução
  - `D`: documento orientador
  - `E`: outros
- dominio por item:
  - `0 = Nenhum`
  - `1 = Sim, <tipo>`

## Bloco 2 - Formacao ERER

`P2`
- pergunta:
  - `2.1. Quantos cursos de 30h ou mais para professores foram ofertados desde a Lei 10.639/2003?`
- indice:
  - `Índice de Formação - Erer`
- item:
  - `A`
- dominio:
  - `0 = Nenhum`
  - `1 = 1 a 5 cursos`
  - `2 = 6 a 10 cursos`
  - `3 = Mais de 10 cursos`

`P3`
- pergunta:
  - `2.2. Quantos cursos de 30h ou mais para diretores e coordenadores pedagógicos foram ofertados?`
- indice:
  - `Índice de Formação - Erer`
- item:
  - `A`
- dominio:
  - `0 = Nenhum`
  - `1 = 1 a 5 cursos`
  - `2 = 6 a 10 cursos`
  - `3 = Mais de 10 cursos`

`P4`
- pergunta:
  - `2.3. Quantos cursos para técnicos das secretarias sobre preenchimento do Censo Escolar foram ofertados?`
- indice:
  - `Índice de Formação - Erer`
- item:
  - `A`
- dominio:
  - `0 = Nenhum`
  - `1 = 1 a 5 cursos`
  - `2 = 6 a 10 cursos`
  - `3 = Mais de 10 cursos`

`P5`
- pergunta:
  - `2.4. Houve palestras, oficinas, seminários ou cursos de curta duração sobre equidade racial nos últimos doze meses?`
- indice:
  - `Índice de Formação - Erer`
- item:
  - `A`
- dominio:
  - `0 = Não`
  - `1 = Sim`

## Bloco 3 - Gestao escolar ERER

`P6`
- pergunta:
  - `3.1. A Secretaria possui estratégias de incentivo às escolas para implementação da Lei 10.639/2003 e 11.645/2008?`
- indice:
  - `Índice de Gestao Escolar - Erer`
- itens:
  - `A`: priorização em programa de reforma de infraestrutura
  - `B`: priorização em programa de formação
  - `C`: adicional financeiro nos moldes do PDDE
  - `D`: outros
- dominio:
  - `0 = Não`
  - `1 = Sim`

`P7`
- pergunta:
  - `3.2. A Secretaria possui estratégias de incentivo aos professores para promoção da equidade racial?`
- indice:
  - `Índice de Gestao Escolar - Erer`
- itens:
  - `A`: estratégia pedagógica
  - `B`: estratégia financeira
  - `C`: incentivo à qualificação profissional
  - `D`: outros
- dominio:
  - `0 = Não`
  - `1 = Sim`

`P8`
- pergunta:
  - `3.3. A implementação das diretrizes é considerada critério de avaliação de desempenho dos profissionais da rede?`
- indice:
  - `Índice de Gestao Escolar - Erer`
- item:
  - `A`
- dominio:
  - `0 = Não`
  - `1 = Sim`

`P9`
- pergunta:
  - `3.4. A Secretaria possui protocolo em casos de racismo ou injúria racial na rede?`
- indice:
  - `Índice de Gestao Escolar - Erer`
- item:
  - `A`
- dominio:
  - `0 = Não`
  - `1 = Sim`

`P10`
- pergunta:
  - `3.5. A Secretaria orienta as escolas a incluírem a implementação das leis nos PPPs?`
- indice:
  - `Índice de Gestao Escolar - Erer`
- item:
  - `A`
- dominio:
  - `0 = Não`
  - `1 = Sim`

`P11`
- pergunta:
  - `3.6. Os processos de escolha de diretor(a)/gestão escolar consideram conhecimentos sobre a Lei 10.639/2003 e 11.645/2008?`
- indice:
  - `Índice de Gestao Escolar - Erer`
- item:
  - `A`
- dominio:
  - `0 = Não`
  - `1 = Sim`

`P12`
- pergunta:
  - `3.7. Os processos de escolha de gestão escolar consideram conhecimentos sobre as diretrizes da ERER e povos indígenas?`
- indice:
  - `Índice de Gestao Escolar - Erer`
- item:
  - `A`
- dominio:
  - `0 = Não`
  - `1 = Sim`

`P13`
- pergunta:
  - `3.8. Quantos dos últimos cinco concursos/processos seletivos incluíram itens sobre as leis?`
- indice:
  - `Índice de Gestao Escolar - Erer`
- item:
  - `A`
- dominio:
  - `0 = Nenhum`
  - `1 = 1 concurso`
  - `2 = 2 concursos`
  - `3 = 3 concursos`
  - `4 = 4 concursos`
  - `5 = 5 concursos`

`P14`
- pergunta:
  - `3.9. Existe equipe específica responsável pela gestão das políticas de equidade racial na Secretaria?`
- indice:
  - `Índice de Institucionalizacao - Erer`
- itens:
  - `A`: superintendência
  - `B`: diretoria
  - `C`: gerência
  - `D`: coordenação
  - `E`: outros
  - `F`: quantidade de pessoas
- dominio:
  - itens `A-E`:
    - `0 = Não`
    - `1 = Sim`
  - item `F`:
    - `0 = Nenhuma`
    - `1 = 1 pessoa`
    - `2 = 2 pessoas`
    - `3 = 3 pessoas`
    - `4 = 4 ou mais pessoas`

`P15`
- pergunta:
  - `3.10. O planejamento pedagógico da Secretaria orienta as escolas a inserir a ERER nas disciplinas?`
- indice:
  - `Índice de Gestao Escolar - Erer`
- item:
  - `A`
- dominio:
  - `0 = Não`
  - `1 = Sim`

`P16`
- pergunta:
  - `3.11. A Secretaria promoveu campanhas sobre autodeclaração de raça/cor/etnia/povo e preenchimento do quesito na matrícula?`
- indice:
  - `Índice de Gestao Escolar - Erer`
- item:
  - `A`
- dominio:
  - `0 = Não`
  - `1 = Sim`

## Bloco 4 - Material didatico e paradidatico ERER

`P17`
- pergunta:
  - `4.1. A Secretaria orienta as escolas a incluir conteúdos de ERER e história/cultura afro-brasileira, africana e indígena na escolha dos materiais?`
- indice:
  - `Índice de Material Didatico e Paradidatico - Erer`
- item:
  - `A`
- dominio:
  - `0 = Não`
  - `1 = Sim`

`P18`
- pergunta:
  - `4.2. A Secretaria adquire materiais didático-pedagógicos que promovam a diversidade étnico-racial?`
- indice:
  - `Índice de Material Didatico e Paradidatico - Erer`
- itens:
  - `A`: educação infantil
  - `B`: ensino fundamental anos iniciais
  - `C`: ensino fundamental anos finais
  - `D`: ensino médio
  - `E`: EJA
  - `F`: EPT
  - `G`: educação especial
  - `H`: educação bilíngue de surdos
  - `I`: educação do campo
  - `J`: educação escolar quilombola
  - `K`: educação escolar indígena
- dominio:
  - `0 = Não`
  - `1 = Sim, <etapa/modalidade>`

`P19`
- pergunta:
  - `4.3. A Secretaria adquire obras literárias infantis/infantojuvenis relacionadas à diversidade étnico-racial?`
- indice:
  - `Índice de Material Didatico e Paradidatico - Erer`
- itens:
  - `A-K`, com a mesma estrutura de etapas/modalidades de `P18`
- dominio:
  - `0 = Não`
  - `1 = Sim, <etapa/modalidade>`

## Bloco 5 - Curriculo ERER

`P20`
- pergunta:
  - `5.1. A Secretaria realizou revisão curricular em cumprimento à Lei 10.639/2003 e à Lei 11.645/2008?`
- indice:
  - `Índice de Institucionalizacao - Erer`
- item:
  - `A`
- dominio:
  - `0 = Não`
  - `1 = Sim`

`P21`
- pergunta:
  - `5.2. A Secretaria instituiu o tema da educação para as relações étnico-raciais na matriz curricular?`
- indice:
  - `Índice de Institucionalizacao - Erer`
- item:
  - `A`
- dominio:
  - `0 = Não`
  - `1 = Sim`

`P22`
- pergunta:
  - `5.3. A Secretaria incluiu o tema da educação para as relações étnico-raciais nos referenciais curriculares?`
- indice:
  - `Índice de Institucionalizacao - Erer`
- item:
  - `A`
- dominio:
  - `0 = Não`
  - `1 = Sim`

`P23`
- pergunta:
  - `5.4. A Secretaria incluiu o tema nos instrumentos de avaliação da aprendizagem?`
- indice:
  - `Índice de Institucionalizacao - Erer`
- item:
  - `A`
- dominio:
  - `0 = Não`
  - `1 = Sim`

## Bloco 6 - Financiamento ERER

`P24`
- pergunta:
  - `7.1. A Secretaria tem indicadores de monitoramento da implementação das leis?`
- indice:
  - `Índice de Avaliacao e Monitoramento - Erer`
- item:
  - `A`
- dominio:
  - `0 = Não`
  - `1 = Sim`

`P25`
- pergunta:
  - `7.2. A Secretaria realizou avaliação da implementação das leis?`
- indice:
  - `Índice de Avaliacao e Monitoramento - Erer`
- item:
  - `A`
- dominio:
  - `0 = Não`
  - `1 = Sim`

`P26`
- pergunta:
  - `7.3. A Secretaria considera os efeitos de fatores externos na aprendizagem dos estudantes?`
- indice:
  - `Índice de Avaliacao e Monitoramento - Erer`
- itens:
  - `A`: secas
  - `B`: enchentes
  - `C`: incêndios
  - `D`: falta de estrutura
  - `E`: violências
  - `F`: outros
- dominio:
  - `0 = Não`
  - `1 = Sim`

`P27`
- pergunta:
  - `7.4. A Secretaria adota protocolos de busca ativa para estudantes com trajetória escolar interrompida?`
- indice:
  - `Índice de Avaliacao e Monitoramento - Erer`
- item:
  - `A`
- dominio:
  - `0 = Não`
  - `1 = Sim`

`P28`
- pergunta:
  - `7.5. A Secretaria utiliza dados de raça/cor/etnia/povo para planejar ações de combate às desigualdades?`
- indice:
  - `Índice de Avaliacao e Monitoramento - Erer`
- item:
  - `A`
- dominio:
  - `0 = Não`
  - `1 = Sim`

`P29`
- pergunta:
  - `7.6. A Secretaria adota cadastro de demandas por vaga em creche que considere nível socioeconômico das famílias?`
- indice:
  - `Índice de Avaliacao e Monitoramento - Erer`
- itens:
  - `A`: existência de cadastro
  - `B`: uso de critério socioeconômico para priorização
- dominio:
  - item `A`:
    - `0 = Não`
    - `1 = Sim`
  - item `B`:
    - `0 = Não há cadastro`
    - `1 = Não`
    - `2 = Sim`

`P30`
- pergunta:
  - `7.7. A Secretaria monitora a frequência escolar com foco nas desigualdades raciais?`
- indice:
  - `Índice de Avaliacao e Monitoramento - Erer`
- item:
  - `A`
- dominio:
  - `0 = Não`
  - `1 = Sim`

## Bloco 7 - EEQ

`P31`
- pergunta:
  - `9.1. Quantos cursos de 30h ou mais para professores sobre Educação Escolar Quilombola foram ofertados desde 2012?`
- indice:
  - `Índice de Formação - EEQ`
- item:
  - `A`
- dominio:
  - `0 = Nenhum`
  - `1 = 1 a 5 cursos`
  - `2 = 6 a 10 cursos`
  - `3 = Mais de 10 cursos`

`P32`
- pergunta:
  - `9.2. Quantos cursos de 30h ou mais para diretores e coordenadores sobre Educação Escolar Quilombola foram ofertados desde 2012?`
- indice:
  - `Índice de Formação - EEQ`
- item:
  - `A`
- dominio:
  - `0 = Nenhum`
  - `1 = 1 a 5 cursos`
  - `2 = 6 a 10 cursos`
  - `3 = Mais de 10 cursos`

`P33`
- pergunta:
  - `9.3. Em relação às escolas quilombolas, os processos de escolha de gestão escolar consideram conhecimentos sobre as diretrizes da modalidade?`
- indice:
  - `Índice de Gestao Escolar - EEQ`
- item:
  - `A`
- dominio:
  - `0 = Não`
  - `1 = Sim`

`P34`
- pergunta:
  - `9.4. Quantos concursos/processos seletivos incluíram itens sobre as diretrizes da Educação Escolar Quilombola?`
- indice:
  - `Índice de Gestao Escolar - EEQ`
- item:
  - `A`
- dominio:
  - `0 ... 5`

`P35`
- pergunta:
  - `9.5. A Secretaria acessou recursos do PNAE para quilombolas?`
- indice:
  - `Índice de Gestao Escolar - EEQ`
- item:
  - `A`
- dominio:
  - `0 = Não`
  - `1 = Sim`

`P36`
- pergunta:
  - `9.6. Existe equipe específica responsável pela gestão da modalidade de Educação Escolar Quilombola na Secretaria?`
- indice:
  - `Índice de Institucionalizacao - EEQ`
- itens:
  - `A-E`: tipo de estrutura
  - `F`: quantidade de pessoas
- dominio:
  - itens `A-E`:
    - `0 = Não`
    - `1 = <estrutura>`
    - `999 = Não se aplica`
  - item `F`:
    - `0 = Não há equipe específica`
    - `1 = 1 pessoa`
    - `2 = 2 pessoas`
    - `3 = 3 pessoas`
    - `4 = 4 ou mais pessoas`
    - `999 = Não se aplica`

`P37`
- pergunta:
  - `9.7. A Secretaria promove produção e distribuição de materiais didáticos específicos para comunidades quilombolas?`
- indice:
  - `Índice de Material Didatico e Paradidatico - EEQ`
- itens:
  - `A-H`: etapas/modalidades
- dominio:
  - `0 = Não`
  - `1 = Sim, <etapa/modalidade>`
  - `999 = Não se aplica`

`P38`
- pergunta:
  - `9.8. A Secretaria participa de reuniões de colegiados relacionados à Educação Escolar Quilombola?`
- indice:
  - `Índice de Institucionalizacao - EEQ`
- item:
  - `A`
- dominio:
  - `0 = Não participa`
  - `1 = Sim, esporadicamente`
  - `2 = Sim, frequentemente`
  - `999 = Não se aplica`

## Bloco 8 - EEI

`P39`
- pergunta:
  - `10.1. Quantos cursos de 30h ou mais para professores sobre Educação Escolar Indígena foram ofertados desde 2012?`
- indice:
  - `Índice de Formação - EEI`
- item:
  - `A`
- dominio:
  - `0 = Nenhum`
  - `1 = 1 a 5 cursos`
  - `2 = 6 a 10 cursos`
  - `3 = Mais de 10 cursos`

`P40`
- pergunta:
  - `10.2. Quantos cursos de 30h ou mais para diretores e coordenadores sobre Educação Escolar Indígena foram ofertados desde 2012?`
- indice:
  - `Índice de Formação - EEI`
- item:
  - `A`
- dominio:
  - `0 = Nenhum`
  - `1 = 1 a 5 cursos`
  - `2 = 6 a 10 cursos`
  - `3 = Mais de 10 cursos`

`P41`
- pergunta:
  - `10.3. Em relação às escolas indígenas, os processos de escolha de gestão escolar consideram conhecimentos sobre as diretrizes da modalidade?`
- indice:
  - `Índice de Gestao Escolar - EEI`
- item:
  - `A`
- dominio:
  - `0 = Não`
  - `1 = Sim`
  - `999 = Não se aplica`

`P42`
- pergunta:
  - `10.4. Quantos concursos/processos seletivos incluíram itens sobre as diretrizes da Educação Escolar Indígena?`
- indice:
  - `Índice de Gestao Escolar - EEI`
- item:
  - `A`
- dominio:
  - `0 ... 5`
  - `999 = Não se aplica`

`P43`
- pergunta:
  - `10.5. A Secretaria acessou recursos do PNAE para indígenas?`
- indice:
  - `Índice de Gestao Escolar - EEI`
- item:
  - `A`
- dominio:
  - `0 = Não`
  - `1 = Sim`
  - `999 = Não se aplica`

`P44`
- pergunta:
  - `10.6. Existe equipe específica responsável pela gestão da modalidade de Educação Escolar Indígena na Secretaria?`
- indice:
  - `Índice de Institucionalizacao - EEI`
- itens:
  - `A-E`: tipo de estrutura
  - `F`: quantidade de pessoas
- dominio:
  - itens `A-E`:
    - `0 = Não`
    - `1 = <estrutura>`
    - `999 = Não se aplica`
  - item `F`:
    - `0 = Não há equipe específica`
    - `1 = 1 pessoa`
    - `2 = 2 pessoas`
    - `3 = 3 pessoas`
    - `4 = 4 ou mais pessoas`
    - `999 = Não se aplica`

`P45`
- pergunta:
  - `10.7. A Secretaria promove produção e distribuição de materiais didáticos específicos para os povos indígenas?`
- indice:
  - `Índice de Material Didatico e Paradidatico - EEI`
- itens:
  - `A-H`: etapas/modalidades
- dominio:
  - `0 = Não`
  - `1 = Sim, <etapa/modalidade>`
  - `999 = Não se aplica`

`P46`
- pergunta:
  - `10.8. A Secretaria participa de reuniões dos Territórios Etnoeducacionais Indígenas e colegiados relacionados à modalidade?`
- indice:
  - `Índice de Institucionalizacao - EEI`
- item:
  - `A`
- dominio:
  - `0 = Não participa`
  - `1 = Sim, esporadicamente`
  - `2 = Sim, frequentemente`
  - `999 = Não se aplica`

## Campos de indice na planilha

Os indicadores finais identificados no dicionario sao:
- `I_Erer_Institucionalizacao`
- `I_Erer_Formacao`
- `I_Erer_Gestao_Escolar`
- `I_Erer_Material_Didatico_Paradidatico`
- `I_Erer_Financiamento`
- `I_Avaliacao_Monitoramento`
- `I_Geral`
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

Observacao importante:
- nas abas de resposta a convenção final usada e `I_Erer_Geral`, enquanto o dicionario tambem mostra formas resumidas como `I_Geral`
- para implementacao no BigQuery e no ATM-EQ, vale sempre seguir o cabecalho real das abas de resposta

## Observacoes metodologicas

### 1. Perguntas multi-item

Perguntas como `P1`, `P6`, `P18`, `P19`, `P36`, `P37`, `P44` e `P45` precisam ser lidas como conjuntos de itens, nao como uma unica resposta simples.

### 2. `999` nao e zero

Nos blocos `EEQ` e `EEI`, `999` significa:
- `Não se aplica`

Isso nao deve ser tratado como:
- ausencia de resposta
- resposta negativa
- nota zero

### 3. Existem perguntas usadas em mais de um eixo

Exemplos:
- `P18` e `P19` alimentam ERER e possuem itens especificos para EEQ e EEI
- isso mostra que o instrumento compartilha parte da infraestrutura conceitual entre os eixos

### 4. O dicionario serve como contrato da camada analitica

Para o ATM-EQ, esse dicionario permite:
- traduzir valores crus em textos legiveis
- montar KPIs textuais
- decidir corretamente o tratamento de `não respondeu` e `não se aplica`
