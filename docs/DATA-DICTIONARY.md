# Dicionário de dados

**Atualizado:** 2026-08-29
**Status:** auditoria estrutural e metodológica concluída para as duas planilhas finais. Campos que não puderam ser estabelecidos nas planilhas ou no apêndice permanecem como `PENDING`.

## Convenções gerais

- As duas planilhas finais são a referência numérica da atualização; o relatório de 2018 é referência conceitual, não meta de replicação ponto a ponto.
- Salvo indicação contrária, os valores monetários finais são reais de dezembro de 2025, corrigidos pelo IPCA. A PNAD Contínua usa o deflator CO2 para levar rendimentos a preços médios de 2025; a transformação adicional de média de 2025 para dezembro de 2025 é `PENDING`.
- `%_pib` e `part_pib_*` são pontos percentuais, calculados como `100 × valor monetário / PIB`.
- `PENDING` significa que a informação não foi estabelecida a partir dos arquivos disponíveis; não é uma imputação.
- As planilhas não contêm uma variável geral e legível por máquina que classifique cada observação como observada, revisada, provisória, interpolada, extrapolada ou modelada. Os status abaixo vêm do apêndice, de fórmulas e de comentários identificáveis.
- Integridade dos arquivos auditados: Brasil SHA-256 `E9824EF3E77E184EB7BC9850694169CD84CFB30BDD91DA238CB615E9FE5D135A`; UFs SHA-256 `4815CC84EFDDAD1274F358336622ACBE1D7861D3F778FADCE09D9D8B0135C8C`.

## Inventário das planilhas

As dimensões abaixo referem-se às observações com chave preenchida, não ao intervalo formatado do Excel.

| Arquivo | Aba | Unidade observacional e chave primária | Cobertura efetiva | Conteúdo e convenção |
|---|---|---|---|---|
| Brasil | `custo_total_violencia` | Brasil-ano; `ano` | 1996–2025; 30 anos | PIB, sete componentes, participações no PIB e total; valores reais de dez./2025 |
| Brasil | `seguranca_publica_br` | Brasil-ano; `ano` | 1996–2025; 30 anos | Despesa pública por esfera quando disponível e total real |
| Brasil | `seguranca_privada_br` | Brasil-ano; `ano` | 1996–2025; 30 anos | Postos, massas salariais e custos, com alternativas RAIS/PNAD |
| Brasil | `encarceramento_br` | Brasil-ano; `ano` | 1996–2025; 30 anos | Custódia/reintegração e auxílio-reclusão |
| Brasil | `seguros_&_danos_materiais_br` | Brasil-ano-cenário; `(ano, cerio)` | 1996–2025; 30 linhas; cenário `amplo` | Prêmios, perdas materiais e total |
| Brasil | `perdas_produtivas_br` | Brasil-ano; `ano` | 1996–2025; 30 anos | Homicídios e perda produtiva modelada |
| Brasil | `processos_judiciais_br` | Brasil-ano; `ano` | 1996–2025; 30 anos | Justiça Estadual: TJs, MPs e defesa |
| Brasil | `servicos_medicos_br` | Brasil-ano; `ano` | 1996–2025; 30 anos | Internações, custo SUS e total médico/produtivo temporário |
| UFs | `custo_total_violencia_ufs` | UF-ano; `(uf, ano)` | 2016 e 2025; 27 UFs em cada ano | Sete componentes; valores reais de dez./2025 |
| UFs | `graficos_ufs` | UF-ano; `(uf, ano)` | 2016 e 2025; 27 UFs em cada ano | PIB, população, PIB per capita, total e participações no PIB |
| UFs | `seguranca_publica_ufs` | UF-ano; `(uf, ano)` | 2016 e 2025; 27 UFs em cada ano | Quatro subfunções e total estadual real |
| UFs | `seguranca_privada_ufs` | UF-ano; `(uf, ano)` | 2016 e 2025; 27 UFs em cada ano | Postos, massas salariais e custo pela PNAD Contínua |
| UFs | `encarceramento_ufs` | UF-ano; `(uf, ano)` | 2016 e 2025; 27 UFs em cada ano | Presos, servidores, parâmetros mensais e gasto calculado; conceito incompatível com a série nacional |
| UFs | `seguros_&_danos_materiais_uf` | UF-ano; `(uf_sigla, ano)` | 2016 e 2025; 27 UFs em cada ano | Ocorrências, pesos de rateio e seis parcelas alocadas |
| UFs | `perdas_produtivas_ufs` | UF-ano; `(uf, ano)` | 2016 e 2025; 27 UFs em cada ano | Homicídios com/sem idade e perdas observada/imputada |
| UFs | `processos_judiciais_ufs` | UF-ano; `(uf, ano)` | 2016 e 2025; 27 UFs em cada ano | Justiça Estadual: TJ, MP e defesa |
| UFs | `servicos_medicos_ufs` | UF-ano; `(uf, ano)` | 2016 e 2025; 27 UFs em cada ano | Internações, dias, custo SUS e perda produtiva temporária |
| UFs | `dados_aux_graficos` | Duas séries auxiliares de UF, uma por ano; chave implícita `uf` em cada bloco | 27 UFs de 2016 e 27 de 2025, mais linhas de parâmetros | Transformação logarítmica e ajuste de gráfico; não é fonte econômica primária |
| UFs | `graficos_finais_ufs` | Não aplicável | Vazia | Sem observações ou variáveis |

Todas as chaves relevantes são únicas. As abas de UF cobrem os 26 estados e o Distrito Federal em ambos os anos. A ordenação das linhas varia entre abas e não deve ser usada como chave.

## Pipeline SIM–IBGE para as Figuras 3 e 4

### Definição epidemiológica

| Elemento | Definição aplicada |
|---|---|
| Base | Sistema de Informações sobre Mortalidade (SIM), bancos de disseminação de Declarações de Óbito (`DO_BDD`) do Ministério da Saúde |
| Variável de causa | `CAUSABAS`, causa básica do óbito, normalizada para CID-10 sem pontuação |
| Códigos de homicídio | X85–X99, Y00–Y09, Y35 e Y36 |
| Inclusões explícitas | Intervenções legais (Y35) e operações de guerra (Y36) |
| Exclusões explícitas | Eventos de intenção indeterminada (Y10–Y34) e quaisquer causas fora do conjunto acima |
| Tempo | Ano extraído de `DTOBITO`; os arquivos anuais finais reconciliam integralmente com esse ano |
| Geografia do óbito | Município de residência, `CODMUNRES`; não se usa o município de ocorrência |
| Idade | Todas as idades; idade ausente não exclui o registro |
| Circunstância | `CIRCOBITO` é apenas diagnóstico auxiliar e não filtra a amostra |
| Município ausente | Códigos `UF0000` informam a UF, mas não o município; são excluídos das agregações microrregionais e quantificados, sem rateio |

O apêndice é a autoridade para essa definição. O código legado filtrava `CIRCOBITO == 3` e idades codificadas entre 1 e 99 anos; esses filtros não foram reproduzidos porque conflitam com a metodologia atual documentada.

### Fontes, vintages e cobertura

| Bloco | Fonte retida | Cobertura/convenção |
|---|---|---|
| Mortalidade | OpenDataSUS/SIM, arquivos anuais finais; URLs, releases, tamanhos e SHA-256 em `data/raw/source_manifest.json` | 2015–2017 e 2022–2024. `ANO_FINAL_SIM = 2024`; 2025 é prévio e não entra nas figuras |
| População 2015–2017 e 2024 | IBGE, SIDRA 6579, variável 9324 | Estimativa municipal da população residente em 1º de julho |
| População 2022 | IBGE, Censo Demográfico 2022, SIDRA 4709, variável 93 | População residente em 1º de agosto de 2022 |
| População 2023 | Derivada, apenas para o diagnóstico suavizado | Interpolação linear, município a município, entre o Censo 2022 e a estimativa 2024; não entra nos pontos principais de 2016 ou 2024 |
| Correspondência territorial | API de Localidades do IBGE, campo de microrregião antiga | 5.570 municípios, 558 microrregiões e 27 UFs; chave municipal IBGE de 7 dígitos e chave SIM de 6 dígitos |
| Geometria | IBGE, Malha Municipal 2015, microrregiões e UFs, escala operacional 1:250.000, SIRGAS 2000 | Divisão territorial com referência em 1º/7/2015, mantida fixa em todos os anos |

Não houve instalação de novo município no intervalo principal 2016–2024; a composição municipal das microrregiões é mantida fixa mesmo diante de revisões posteriores de limites. Brasília é tratada como o município IBGE `5300108`, código SIM `530010`, pertencente à microrregião `53001` (Brasília). Boa Esperança do Norte (`5101837`) foi instalada em 2025, fora do período. A API atual a devolve sem microrregião antiga e o SIDRA registra `...`, não uma população numérica, nos anos utilizados. Sua exclusão do crosswalk fixo não remove população nem óbitos dos anos das figuras. A malha contém 562 registros geométricos para 558 códigos; `13012` e `13013` aparecem em três feições cada porque suas geometrias são multipartes. Todos os 558 códigos reconciliam com o crosswalk.

A rota oficial `DO23OPEN.csv` é usada em 2023. Uma conversão genérica posterior, `Mortalidade_Geral_2023_csv.zip`, foi retida apenas como diagnóstico e marcada como não utilizada no manifesto: ela contém 38.559 homicídios e não reconcilia com o total final de 45.747. O arquivo selecionado reconcilia, assim como 2024 (42.590).

### Arquivos derivados e variáveis

| Arquivo | Unidade/chave | Variáveis e construção |
|---|---|---|
| `data/interim/municipality_microrregion_crosswalk.csv` | Município; `municipality_code_7` | Código SIM de 6 dígitos, município, microrregião, mesorregião, UF e macrorregião |
| `data/interim/municipality_homicides_population.csv` | Município-ano; `(municipality_code_7, year)` | `homicide_count`, `population` e `population_status`; 33.420 linhas, sem duplicatas |
| `data/interim/microrregion_homicides.csv` | Microrregião-ano; `(microrregion_code, year)` | 3.348 linhas; `homicide_count`, `population`, `homicide_rate_per_100k`, `percentile_unweighted`, metadados geográficos e status |
| `data/figure_data/fig_03_microrregion_homicides.csv` | Microrregião em 2024 | Taxa, percentil e área da bolha; `bubble_area_points2 = population / 7.500`, portanto a área é exatamente proporcional à população |
| `data/figure_data/fig_04_microrregion_homicide_change.csv` | Microrregião; uma linha por código | Taxas e níveis de 2016 e 2024; `delta_rate_per_100k = rate_2024 - rate_2016`; médias agrupadas de 2015–2017 e 2022–2024 para diagnóstico; valor verdadeiro e valor visual limitado preservados separadamente |
| `data/figure_data/fig_05_microrregion_homicide_convergence.csv` | Microrregião; uma linha por código | Taxa de 2016, taxa de 2024, variação absoluta, populações e área da bolha; ajuste linear descritivo ponderado pela população de 2016 e diagnóstico com médias trienais |

Para cada microrregião-ano:

`homicide_rate_per_100k = 100000 × homicide_count / population`.

O percentil é a posição média do posto em caso de empates, dividida por 558 e multiplicada por 100. Trata-se de uma distribuição não ponderada; a população é codificada separadamente pela área das bolhas.

### Cobertura e perdas de geocodificação

| Ano | Homicídios SIM | Com município identificável | Cobertura | Excluídos (`UF0000`) |
|---:|---:|---:|---:|---:|
| 2015 | 59.080 | 58.278 | 98,6425% | 802 |
| 2016 | 62.517 | 61.531 | 98,4228% | 986 |
| 2017 | 65.602 | 64.660 | 98,5641% | 942 |
| 2022 | 46.409 | 45.819 | 98,7287% | 590 |
| 2023 | 45.747 | 45.210 | 98,8262% | 537 |
| 2024 | 42.590 | 42.132 | 98,9246% | 458 |

Não há óbitos homicidas excluídos por data ausente, ano divergente, idade ausente ou código municipal não reconhecido nesses arquivos. A única perda geográfica é `UF0000`; os totais nacionais brutos permanecem no arquivo de auditoria. O piso mecânico documentado para permitir agregação subestadual é 95%, e a cobertura efetiva o supera em todos os anos. Valores abaixo de 99% são mantidos como advertências, não erros.

## Variáveis nacionais

### Agregado, componentes e PIB

**Aba:** `custo_total_violencia`; **geografia:** Brasil; **período:** 1996–2025.

| Variável armazenada | Conceito e unidade | Construção, fonte e status |
|---|---|---|
| `ano` | Ano civil; índice | Chave única, inteiro |
| `pib_deflacionado` | PIB brasileiro em R$ de dez./2025 | Denominador de todas as participações. Fonte, release, vintage e transformação exata: `PENDING` |
| `seguranca_publica` | Despesa das três esferas, R$ de dez./2025; gasto público | Ligação a `seguranca_publica_br.gasto_total_deflaciodo` |
| `seguranca_privada` | Custo amplo do trabalho em segurança privada, R$ de dez./2025; despesa/custo de recurso privado | 1996–2011: massa formal PNAD anual × 1,86 + massa informal PNAD anual; 2012–2025: equivalente PNAD Contínua. A RAIS é robustez, não a série principal |
| `encarceramento` | Custódia/reintegração mais auxílio-reclusão, R$ de dez./2025 | `custodia_&_reintegracao_deflaciodo + auxilio_reclusao_deflaciodo`; mistura gasto público com transferência, que deve permanecer identificada |
| `seguros_&_danos_materiais` | Soma ampla de três prêmios e três perdas, R$ de dez./2025 | Soma das colunas C:H da aba de seguros; agrega fluxo de seguro e perda material, com possível sobreposição econômica |
| `processos_judiciais` | Recursos associados a matéria criminal na Justiça Estadual, R$ de dez./2025 | TJs + MPs + defesa; exclui Justiça e MP federais e sistema prisional |
| `perdas_produtivas` | Valor presente de renda esperada perdida por homicídios, R$ de dez./2025 | Série modelada a partir de SIM, PNAD Contínua 2025 e tábua de sobrevivência |
| `servicos_medicos` | Custo SUS hospitalar por agressão + perda produtiva temporária, R$ de dez./2025 | Liga a `servicos_medicos_br.gasto_total`; gasto hospitalar mais perda modelada |
| `part_pib_seg_pub`, `part_pib_seg_priv`, `part_pib_encar`, `part_pib_seguros`, `part_pib_justica`, `part_pib_perdas_prod`, `part_pib_serv_med` | Participação de cada componente no PIB, pontos percentuais | `100 × componente / pib_deflacionado`; identidades conferidas |
| `custo_total_violencia` | Total contábil dos sete componentes, R$ de dez./2025 | Após a reorganização da aba, a fórmula `SUM(B:H)` soma corretamente os sete componentes. A identidade do total e a ligação da perda produtiva de 2025 passam |

Não há participação de cada componente no total armazenada. Quando necessária, usar `100 × componente / soma dos sete componentes`; essas sete parcelas devem somar 100%.

### Segurança pública

**Aba:** `seguranca_publica_br`; **tipo:** gasto público; **período:** 1996–2025.

| Variáveis | Unidade e construção | Fonte, status e limitações |
|---|---|---|
| `uniao`, `ufs`, `municipios` | R$ na convenção da fonte; valores numéricos no arquivo atual em 2016–2025 e células vazias em 1996–2015 | A série total incorpora Ipea/STN, STN e FBSP ao longo do período, mas o arquivo final atual só expõe a decomposição por esfera em 2016–2025. Não imputar parcelas para anos anteriores. O código da Figura 6 detecta dinamicamente anos nos quais as três colunas estejam preenchidas |
| `gasto_total_deflaciodo` | Total das esferas convertido para R$ de dez./2025 pelo IPCA | Para 1996–2003, total Ipea a preços de 2005 atualizado a dez./2025; depois, soma anual das esferas e deflação. Série agregada principal |
| `fonte` | Texto | Referência anual; não é valor econômico |

A série inclui atividades registradas na função Segurança Pública e não constitui estimativa de bem-estar. O valor de UFs no arquivo nacional é uma esfera do agregado, não necessariamente o mesmo objeto que todo gasto público localizado numa UF.

### Segurança privada

**Aba:** `seguranca_privada_br`; **tipo:** despesa/custo de recurso privado; **período:** 1996–2025.

| Variáveis | Unidade | Definição e status |
|---|---|---|
| `postos_formais_rais`, `postos_formais_pnad_antiga`, `postos_formais_pnadc` | Número expandido de postos/pessoas ocupadas conforme a fonte | Ocupações de segurança. PNAD anual: trabalho principal, formal com carteira; PNAD Contínua: trabalho principal ou secundário, formal com carteira ou CNPJ. RAIS é cenário de robustez |
| `postos_informal_pnad_antiga`, `postos_informal_pnadc` | Número expandido | Ocupados selecionados sem o critério de formalidade correspondente |
| `massa_salarial_formal_deflacionada_rais`, `massa_salarial_formal_deflacionada_pnad_antiga`, `massa_salarial_formal_deflacionada_pnadc` | Massa anual, R$ de 2025 | Soma ponderada de rendimento mensal × 12. PNAD anual: IPCA a dez./2025; PNAD Contínua: CO2 a preços médios de 2025; passagem a dez./2025 `PENDING` |
| `massa_salarial_informal_deflacionada_pnad_antiga`, `massa_salarial_informal_deflacionada_pnadc` | Massa anual, mesma convenção | Mesma construção para informais |
| `multiplicador_encargos_trabalhistas` | Índice adimensional, 1,86 | Parâmetro Fenavist (2012) aplicado à massa formal; invariável |
| `custo_trabalho_formal_rais`, `custo_trabalho_formal_pnad_antiga`, `custo_trabalho_formal_pnadc` | R$ de 2025 | `massa formal × 1,86` |

Na PNAD anual, rendimentos ausentes são imputados pela média de célula ocupação × posição na ocupação. Em 2000 e 2010, sem PNAD anual, repetem-se nominalmente massa e postos do ano anterior antes da atualização monetária. Na PNAD Contínua usa-se a 1ª visita em 2012–2019 e 2022–2025 e a 5ª em 2020–2021, preservando o desenho amostral. Há quebra conceitual e de pesquisa em 2012.

### Encarceramento

**Aba:** `encarceramento_br`; **período:** 1996–2025.

| Variável | Tipo e unidade | Construção, cobertura e status |
|---|---|---|
| `custodia_&_reintegracao_deflaciodo` | Gasto público, R$ de dez./2025 | União líquida de transferências às UFs + despesas estaduais na subfunção 421. União: SIGA 2001–2025, BGU calibrado em 2000, retroprojeção 1996–1999. UFs: STN 2004–2013, Siconfi 2014–2025; 2004–2010 empenhado convertido a liquidado por 0,9638414359; 1996–2003 retroprojeção com população prisional e remuneração (`λ=0,492001932`) |
| `auxilio_reclusao_deflaciodo` | Transferência previdenciária, R$ de dez./2025 | Benefícios emitidos, AEPS 1996–2024 e soma de 12 BEPS em 2025; 2016 corrigido para o conceito emitido |
| `fonte_custodia_&_reintegracao`, `fonte_auxilio_reclusao` | Texto | Linhagem anual |

As modalidades 30 e 31 são retiradas da União para evitar dupla contagem com as UFs. Para a cobertura estadual, não há UFs imputadas em 2011–2013; em 2025 são imputadas CE, MG, PA, PI, RJ, RS e SE pela média simples das UFs que reportaram. O método nacional exclui uma estimativa separada de servidores porque a subfunção 421 já contém pessoal.

### Seguros e danos materiais

**Aba:** `seguros_&_danos_materiais_br`; **cenário principal:** `cerio = amplo`; **período:** 1996–2025; **preços:** R$ de dez./2025.

| Variável | Tipo | Definição, fonte e status |
|---|---|---|
| `seguro_automotivo_deflaciodo`, `seguro_patrimonial_deflaciodo`, `seguro_transporte_carga_deflaciodo` | Prêmio de seguro; fluxo relacionado a seguro | Prêmio direto da SES/Susep, ramos selecionados; observado 1996–2025 |
| `perda_patrimonial_deflaciodo`, `perda_transporte_carga_deflaciodo` | Perda material/medida de sinistros | Série híbrida Susep: sinistro direto até nov./2013 e sinistro ocorrido desde dez./2013; mudança de conceito intrassérie |
| `perda_automobilista_deflaciodo` | Perda material | `quantidade de roubos+furtos × preço de referência × 0,635`. Quantidade nacional observada no FBSP em 2013–2025; 1996–2012 imputada como `2,103443 × (SP+RJ)`. Preço: série real de 2010 em 1996–2009; AutoSeg em 2010–2019; composição 2020A e índices IPCA de subitens em 2021–2025. Recuperação fixa de 36,5% |
| `gasto_total` | Soma contábil, não um conceito homogêneo de bem-estar | Soma das seis parcelas; identidade conferida |
| `fonte_seguro` | Texto | URL da Susep |

Prêmios, sinistros e perdas materiais não são intercambiáveis. O cenário amplo preserva possível sobreposição entre prêmios e perdas/sinistros e deve ser descrito como convenção contábil.

### Perdas de capacidade produtiva

**Aba:** `perdas_produtivas_br`; **tipo:** perda modelada de capacidade produtiva; **período armazenado:** 1996–2025.

| Variável | Unidade | Construção e status |
|---|---|---|
| `total_de_homicidios` | Número de óbitos | SIM/Datasus, causas CID-10 X85–X99, Y00–Y09, Y35 e Y36; idade desconhecida imputada dentro de ano × grande região |
| `renda_total_perdida` | Valor presente, R$ de dez./2025 | Para cada morte, soma de renda esperada por idade × probabilidade de sobrevivência; PNAD Contínua 2025 por idade × grande região, crescimento real de 2%, desconto de 3%, idades 14–90 e grupo 70+ agregado; soma das regiões |

A aba-fonte registra 40.775 homicídios em 2025 e calcula a perda como `perda de 2024 × 40.775 / 42.590`, totalizando R$ 29,17 bilhões. Ainda não há microdados de 2025 por idade e região: o perfil de perda por homicídio permanece baseado em 2024. A aba-resumo reproduz corretamente esse valor.

### Processos judiciais

**Aba:** `processos_judiciais_br`; **geografia conceitual:** Justiça Estadual; **período:** 1996–2025; **preços:** R$ de dez./2025.

| Variável | Tipo | Construção e status |
|---|---|---|
| `gastos_deflaciodos_tjs` | Despesa pública atribuída à matéria criminal | 2009–2025: despesa dos 27 TJs × participação de sentenças criminais, com peso fixo por UF; 1996–2002: extrapolação logarítmica do gasto real per capita; 2003–2008: dados CNJ e participação criminal fixa de 12,4057% |
| `gastos_deflaciodos_mps` | Despesa pública atribuída à matéria criminal | Âncoras 2007–2008; 1996–2006 pela razão MP/TJ de 0,3036929; 2009–2025 valores UF-ano observados com interpolação/extrapolação de células ausentes e participação criminal de 68,72% |
| `gastos_deflaciodos_defesa` | Serviço jurídico valorado; não necessariamente desembolso observado | 2009–2025: processos novos comuns e JECRIM × honorários de referência da OAB por UF; ausentes recebem média nacional por tipo. Valores de tabelas recentes, inclusive referências de 2026, são aplicados historicamente em R$ de dez./2025. 1996–2008: quantidades modeladas |

O total conceitual é a soma das três colunas. O apêndice afirma que, desde 2009, os totais nacionais são a soma das 27 UFs; a aba nacional não reconcilia com a aba UF no componente MP em 2016 nem em 2025.

### Serviços médicos e terapêuticos

**Aba:** `servicos_medicos_br`; **período:** 1996–2025.

| Variável | Unidade | Construção e status |
|---|---|---|
| `internacoes_agressao` | Número de AIHs por agressão | SIH/SUS, agressão em qualquer diagnóstico. As células nacionais de 1996–1997 armazenam `-`, embora o total tenha sido preenchido pelo procedimento descrito abaixo |
| `custo_SUS_deflacionado` | Gasto hospitalar, R$ de dez./2025 | Soma de `VAL_TOT` das AIHs selecionadas, corrigida pelo IPCA. Células nacionais de 1996–1997 armazenam `-` |
| `gasto_total` | Gasto SUS + perda produtiva temporária, R$ de dez./2025 | A perda não fatal usa dias efetivos de internação × renda diária esperada por idade × região, PNAD Contínua 2025. 1996–1997 copiam o resultado de 1998; lacunas UF-mês em RR (dez./1999 e jan.–mai./2000) e AP (out./2007) são interpoladas; set./2009 recebe a média dos outros meses de setembro |

Óbitos hospitalares não recebem perda temporária, reduzindo sobreposição direta com a perda produtiva por homicídio. A medida exclui atendimento ambulatorial, saúde privada e custos não registrados na AIH.

## Variáveis por UF

Todas as abas economicamente relevantes abaixo têm chave `(UF, ano)`, cobrem 2016 e 2025 e contêm 27 UFs por ano. Valores monetários finais são R$ de dez./2025, salvo indicação contrária.

### Componentes, PIB e população

| Aba e variáveis | Definição e fórmula | Metadados e validação |
|---|---|---|
| `custo_total_violencia_ufs`: `seguranca_publica`, `seguranca_privada`, `encarceramento`, `seguros_&_danos_materiais`, `processos_judiciais`, `perdas_produtivas`, `servicos_medicos` | Ligações ou somas das abas de componentes; preservam os tipos econômicos nacionais, exceto a diferença conceitual de encarceramento descrita abaixo | Chaves e números completos; a correção de anualização do encarceramento foi propagada e as ligações com `graficos_ufs` passam |
| `graficos_ufs.pib_estadual` | PIB da UF, R$ de dez./2025 | Fonte, release, vintage, deflator e eventual rateio de atividades extrarregionais: `PENDING`. A soma reconcilia com o PIB nacional a menos de R$ 1.025 em 2016 e R$ 0,02 em 2025 |
| `graficos_ufs.populacao` | Pessoas | Fonte, data de referência, release/vintage e status observado/estimado: `PENDING` |
| `graficos_ufs.pib_per_capita` | R$ de dez./2025 por pessoa | `pib_estadual / populacao`; identidade conferida considerando arredondamento armazenado |
| `graficos_ufs.custo_total_crime` | Soma dos sete componentes, R$ de dez./2025 | `SUM(C:I)` na aba de componentes; identidade conferida |
| `graficos_ufs.custo_total_%_pib` e sete `componente_%_pib` | Pontos percentuais | `100 × valor / pib_estadual`; identidades e limites conferidos |

### Segurança pública por UF

| Variáveis | Tipo/unidade | Construção e limitações |
|---|---|---|
| `policiamento`, `defesa_civil`, `informacao_&_inteligencia`, `demais_subfunções` | Gasto público estadual, R$ de dez./2025 | FBSP, Anuários correspondentes a 2016 e 2025; mesmas categorias gerais entre UFs dentro do ano |
| `total_deflaciodo` | Soma das subfunções disponíveis | Células vazias são tratadas por `SUM` como zero em 16 UF-anos, mas o significado de vazio não está documentado (`PENDING`) |
| `fonte` | Texto | Referência anual |

Os rótulos de quatro UFs estão truncados nesta aba (`Amazos`, `Mis Gerais`, `Permbuco`, `Santa Catari`). O validador aplica mapeamento explícito; a planilha deve ser corrigida a montante antes de joins por nome.

### Segurança privada por UF

| Variáveis | Unidade/construção | Fonte e status |
|---|---|---|
| `postos_formais_pnadc`, `postos_informal_pnadc` | Postos expandidos | PNAD Contínua, ocupações e formalidade da metodologia nacional; 2016 e 2025 |
| `massa_salarial_formal_deflacionada_pnadc`, `massa_salarial_informal_deflacionada_pnadc` | Massa anual, R$ de 2025 | Desenho amostral da PNAD Contínua e CO2; incerteza amostral não propagada para o total |
| `multiplicador_encargos_trabalhistas` | Índice 1,86 | Mesmo parâmetro nacional |
| `custo_trabalho_formal_rais` | `1,86 × massa formal`, R$ de 2025 | O nome menciona RAIS, mas a fórmula usa a massa PNAD Contínua da própria aba; rótulo inconsistente |

O componente UF é `custo_trabalho_formal_rais + massa informal`. Como as estimativas amostrais são produzidas separadamente por UF e Brasil, a soma das UFs difere do nacional em −0,0114% (2016) e +0,1687% (2025); isso é advertência plausível, não erro mecânico.

### Encarceramento por UF

| Variável | Unidade/fórmula armazenada | Status |
|---|---|---|
| `presos` | Pessoas privadas de liberdade | Fonte/vintage por UF: `PENDING` |
| `custo_mensal_preso` | R$ por preso por mês, segundo o cabeçalho | Fonte, ano-base e variação entre anos: `PENDING` |
| `servidores` | Número de servidores | Fonte/vintage: `PENDING` |
| `rem_media_executivo_estadual` | R$ por servidor por mês, segundo a fórmula | Fonte/vintage: `PENDING` |
| `gasto_anual_presos` | `12 × presos × custo_mensal_preso` | A anualização foi corrigida nas 54 linhas e a identidade passa na aba-fonte |
| `gasto_anual_servidores` | `12 × servidores × remuneração média` | Identidade conferida |
| `gasto_encarceramento` | Soma das duas parcelas | Identidade interna conferida, mas incorpora o erro anterior |

Esse método não está documentado no apêndice e difere da série nacional, que usa a subfunção 421 mais auxílio-reclusão e exclui pessoal separado para evitar dupla contagem. A correção mecânica foi propagada para `custo_total_violencia_ufs` e `graficos_ufs`; a diferença conceitual permanece como limitação a documentar e revisar antes da publicação.

### Seguros e danos materiais por UF

| Variáveis | Unidade e construção | Status/limitação |
|---|---|---|
| `roubo_automovel`, `roubo_carga`, `roubo_total` | Quantidades | Fonte e definição exata por UF: `PENDING` |
| `peso_roubo_automovel`, `peso_roubo_carga`, `peso_roubo_total` | Fração do total nacional no ano | Cada conjunto soma 1 em 2016 e 2025 |
| `gasto_seguro_automovel`, `gasto_seguro_patrimonio`, `gasto_seguro_carga` | Prêmios alocados, R$ de dez./2025 | Totais nacionais rateados pelos pesos correspondentes; fórmula exata peso–componente: conferida no arquivo, mas justificativa conceitual do rateio é `PENDING` |
| `gasto_perda_automovel`, `gasto_perda_patrimonio`, `gasto_perda_carga` | Perdas alocadas, R$ de dez./2025 | Mesmo procedimento; a soma das seis parcelas por UF produz o componente |
| `uf_sigla` | Código UF | Derivado do nome; usar como chave geográfica canônica |

As somas de UF reconciliam com as seis séries nacionais dentro de R$ 2. Os valores são alocações de um total nacional e não estimativas independentes de incidência monetária em cada UF.

### Perdas produtivas por UF

| Variável | Unidade/construção | Status |
|---|---|---|
| `homicidios_com_idade`, `homicidios_sem_idade`, `homicidios_totais` | Número de óbitos | SIM; `total = com idade + sem idade` |
| `perda_observada` | R$ de dez./2025 | Soma modelada para óbitos com idade identificada |
| `renda_media_imputacao_sem_idade` | R$ por homicídio sem idade | Média de perda usada no estrato ano × grande região |
| `perda_imputada` | R$ de dez./2025 | `homicídios sem idade × renda média de imputação` |
| `perda_total_com_imputacao` | R$ de dez./2025 | `perda_observada + perda_imputada`; identidade conferida |

Em 2016, as UFs e o nacional têm 62.517 homicídios e a diferença monetária é apenas R$ 8,2 milhões (0,0168%), classificada como revisão plausível. Em 2025, a soma das UFs permanece em 36.362 homicídios e R$ 25,31 bilhões, enquanto o nacional tem 40.775 e R$ 29,17 bilhões; diferenças de 4.413 homicídios e R$ 3,86 bilhões. O ano-fonte efetivo das UFs em 2025 é `PENDING`.

### Processos judiciais por UF

| Variável | Tipo/unidade | Construção |
|---|---|---|
| `gasto_justica_criminal_tj` | Despesa atribuída, R$ de dez./2025 | Despesa do TJ × participação criminal conforme sentenças e pesos da metodologia |
| `gasto_justica_criminal_mp` | Despesa atribuída, R$ de dez./2025 | Despesa MP UF-ano × 68,72%, após imputações descritas no apêndice |
| `gasto_justica_criminal_defesa` | Serviço jurídico valorado, R$ de dez./2025 | Processos comuns e JECRIM × honorários de referência da OAB |

TJs e defesa somam exatamente aos valores nacionais em 2016 e 2025. MPs excedem o nacional em R$ 959,1 milhões (5,96%) em 2016 e R$ 1,465 bilhão (6,44%) em 2025, contrariando a identidade declarada no apêndice.

### Serviços médicos por UF

| Variável | Unidade e fórmula | Tipo/status |
|---|---|---|
| `deflator_bc` | Índice, 1 em 2025 | Fator IPCA até dez./2025; fonte/vintage da série de índice: `PENDING` |
| `internacoes_agressao` | Número de AIHs | `internacoes_nao_fatais + obitos_hospitalares` |
| `internacoes_nao_fatais`, `internacoes_nao_fatais_com_idade`, `internacoes_nao_fatais_sem_idade`, `obitos_hospitalares` | Quantidades | Não fatais = com idade + sem idade; SIH/SUS |
| `dias_totais_internacao`, `dias_nao_fatais_com_idade` | Dias | `DIAS_PERM`; perda temporária aplica-se aos não fatais |
| `custo_SUS` | Gasto hospitalar, R$ de dez./2025 | Soma de AIHs corrigida pelo IPCA |
| `perda_produtiva_observada`, `perda_produtiva_imputada`, `perda_produtiva_temporaria` | Perda modelada, R$ de 2025 | Dias × renda diária esperada; temporária = observada + imputada |
| `renda_diaria_media_imputacao` | R$ por dia | Doador para internações sem idade, por região |
| `custo_medico_total` | R$ de dez./2025 | `custo_SUS + perda_produtiva_temporaria`; identidade conferida |

As somas das UFs reconciliam com o nacional dentro de R$ 2 em 2016 e 2025.

## Painéis externos das Figuras 1 e 2

### Sinesp VDE e população das UFs

**Insumos:** arquivos anuais oficiais `bancovde-2015.xlsx`–`bancovde-2025.xlsx`, retidos
em `data/raw/sinesp/`, e Projeções da População do IBGE, Revisão 2024. A unidade bruta
é UF × mês × evento; a pipeline seleciona `abrangencia = Estadual`, soma linhas repetidas
do mesmo indicador/mês conforme a nota do Sinesp e jamais converte ausência de reporte em zero.

| Variável derivada | Unidade/construção | Cobertura e interpretação |
|---|---|---|
| `count` | Soma anual de `total_vitima` para homicídio doloso, latrocínio, tentativa de homicídio, estupro, estupro de vulnerável e feminicídio | Vítimas registradas; 27 UFs, 12 meses e 2016–2025 nas Figuras 2A–2B. Estupro e estupro de vulnerável são indicadores separados e não são somados |
| `count` | Soma anual de `total` para furto de veículo, roubo de veículo, roubo de carga e roubo a instituição financeira | Ocorrências registradas; painel balanceado específico por indicador em 2016–2025 nas Figuras 2C–2D, não total nacional |
| `population` | Soma da população das UFs da amostra, em 1º de julho | IBGE, Revisão 2024, ambos os sexos e todas as idades; a mesma amostra geográfica do numerador |
| `rate_per_100k` | `100000 × count / population` | Vítimas ou ocorrências por 100 mil habitantes, conforme o indicador |
| `reporting_status` | `FULL_12_MONTHS`, `PARTIAL_MONTHS` ou `NOT_REPORTED` | Flag explícita por UF–ano–crime em `sinesp_category_coverage.csv` |

A amostra é fixa no tempo, mas específica por indicador. Furto e roubo de veículo usam 22 UFs
(excluem AC, ES, GO, PR e RO) e cobrem 87,8% da população brasileira em 2025. Roubo de carga
usa 20 UFs (exclui AC, ES, GO, MS, PR, RO e SE) e cobre 85,3%; roubo a instituição financeira
usa 20 UFs (exclui AC, AP, ES, GO, MS, PR e RO) e cobre 86,0%. Tráfico de drogas foi retido no
diagnóstico, mas não plotado porque varia com a atividade policial; armas de fogo apreendidas medem
objetos apreendidos e tampouco são uma série de ocorrências ou vítimas. Feminicídio é mantido com alerta de consolidação da
classificação legal.

### UNODC — homicídio intencional

**Insumo:** `data_cts_intentional_homicide_2026-07.xlsx`, versão oficial de julho de 2026.
A unidade analítica inicial é unidade de reporte país/território × ano. O seletor é `Indicator = Victims of intentional
homicide`, `Dimension = Category = Sex = Age = Total` e `Unit of measurement = Rate per 100,000
population`. A definição segue ICCS 0101: morte ilegal infligida intencionalmente a uma pessoa
por outra pessoa. Não se misturam contagens e taxas, não se interpola e unidades subnacionais
com identificador não ISO-3 são excluídas.

O campo oficial `Country` inclui algumas unidades territoriais com ISO-3 (Bermuda, Hong Kong,
Macau e Porto Rico) e elas permanecem no universo do UNODC. Unidades explicitamente subnacionais
com identificadores compostos, como Inglaterra e Gales, Escócia e regiões do Iraque, são
excluídas. A figura deve, portanto, ser interpretada como distribuição entre unidades oficiais de
reporte país/território, não como uma lista estrita de Estados soberanos.

| Variável | Unidade/construção | Cobertura |
|---|---|---|
| `homicide_rate_per_100k` | Taxa anual oficial do UNODC por 100 mil habitantes | 2003–2024 no arquivo processado; a Figura 1 usa 2016 e 2024 sem interpolação; a cobertura anual chega a 95 unidades em 2024 |
| `included_common_sample` | Indicador de inclusão | Mesmas 87 unidades de reporte, observadas em 2016 e 2024 |
| `percentile_unweighted` | `100 × (posto médio−1)/(N−1)` | Distribuição não ponderada entre as 87 unidades; empates recebem posto médio |

Os arquivos derivados são `data/interim/unodc_homicide_country_year.csv`, com a série anual
selecionada, `data/interim/unodc_homicide_country_comparison.csv`, com o universo e as flags de
inclusão nas duas datas, e `data/figure_data/fig_01_distribuicao_mundial_homicidios.csv`, que contém
exatamente as 87 observações plotadas em cada painel.

O UNODC informa que as taxas usam população das World Population Prospects 2024. O Brasil
é mantido exclusivamente na série do próprio UNODC, sem emenda com fonte nacional.

## Cobertura terminal

| Série principal | Última linha armazenada | Interpretação de 2025 |
|---|---:|---|
| Segurança pública nacional | 2025 | Disponível; valores anuais do FBSP |
| Segurança privada nacional | 2025 | Disponível; PNAD Contínua, 1ª visita |
| Encarceramento nacional | 2025 | Disponível, mas sete UFs foram imputadas no agregado estadual; auxílio é soma de BEPS mensais |
| Seguros e danos materiais nacional | 2025 | Disponível; alguns insumos/preços são construídos conforme a metodologia |
| Processos judiciais nacional | 2025 | Disponível, com imputações/modelagem; conflito de MP com a aba UF |
| Serviços médicos nacional | 2025 | Disponível no SIH e no modelo de renda |
| Perdas produtivas nacional | 2025 | Usa 40.775 homicídios agregados de 2025 e reaproveita o perfil/valor por homicídio de 2024; propagada corretamente à aba-resumo |
| Blocos por UF | 2025 | 27 UFs armazenadas, mas encarceramento e perdas produtivas não são comparáveis/consistentes com o nacional |

Assim, 2025 não é um ano terminal comum plenamente comparável para o total por UF. A perda produtiva deve ser rotulada como estimativa baseada no total agregado de 2025 e no perfil de 2024.

## Identidades e tolerâncias de validação

O comando `python -m src.validation.validate_data` implementa os testes. As tolerâncias não são escolhidas para aproximar o relatório de 2018:

- moeda: R$ 2 de tolerância absoluta para resultados de fórmulas em cache/arredondados; a estrutura das fórmulas é testada separadamente;
- PIB nacional versus soma das UFs: tolerância relativa de `1e-9`, além de R$ 2 absolutos;
- participações: `1e-8` ponto percentual;
- pesos de rateio: `1e-9`;
- movimentos anuais acima de 40% são apenas um filtro de advertência, não erro.

Identidades que passam: ligações entre componentes e agregados; participações no PIB; soma das seis parcelas de seguros; totais e participações por UF; pesos de rateio; PIB per capita; identidades internas de perdas produtivas e saúde; segurança pública UF; segurança pública, seguros, saúde e PIB na reconciliação apropriada Brasil–UF.

Não restam erros mecânicos bloqueantes. Em AC–2025, `homicidios_com_idade` foi corrigido de 191 para 181, de modo que `181 + 1 = 182`. O bloco agregado UF de perdas produtivas em 2025 e a diferença nacional–UF dos MPs permanecem como advertências não bloqueantes, com atualização dos dados estaduais e nova verificação obrigatórias antes da publicação.

## Metadados ainda `PENDING`

1. fonte, release/vintage e transformação do PIB nacional;
2. fonte, release/vintage, data de referência e transformação de PIB e população das UFs;
3. ajuste exato entre preços médios de 2025 (CO2) e dezembro de 2025;
4. significado de células vazias nas subfunções de segurança pública por UF;
5. fonte e justificativa de todos os parâmetros do encarceramento por UF;
6. fonte exata e justificativa dos pesos de rateio de seguros/danos por UF;
7. ano-fonte e tratamento metodológico do bloco 2025 de perdas produtivas por UF;
8. status provisional/revised de entradas de 2025 que não está codificado nas planilhas;
9. vintage da população empregada nas extrapolações da Justiça.
