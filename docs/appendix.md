# Apêndice metodológico

Este apêndice documenta as fontes, as definições, as fórmulas e os tratamentos empregados na construção das séries atualizadas.

## Gastos com segurança pública

### 1. Objetivo e delimitação da estimação

Os gastos com segurança pública correspondem aos recursos orçamentários mobilizados pela União, pelos estados e pelo Distrito Federal e pelos municípios para financiar atividades de policiamento, defesa civil, informação e inteligência e outras ações classificadas na função Segurança Pública. Esses dispêndios representam um custo de prevenção, controle e resposta à criminalidade: em um cenário contrafactual sem crime e violência, ao menos parte dos recursos poderia ser destinada a outras finalidades.

A estimativa foi construída como uma série anual nacional, de 1996 a 2025, mediante a harmonização de três conjuntos de informações. O resultado principal de cada ano é o gasto total das três esferas de governo, sem adição de componentes externos à função orçamentária, evitando dupla contagem.

### 2. Fontes de dados e cobertura temporal

A cobertura de quase três décadas exigiu a combinação de fontes com formatos e referências monetárias distintos. Seguiu-se o protocolo de priorizar registros primários e oficiais; quando a classificação histórica não permitia isolar de forma comparável a função Segurança Pública, recorreu-se a uma reconstrução publicada pelo Instituto de Pesquisa Econômica Aplicada (Ipea), baseada nos registros da Secretaria do Tesouro Nacional (STN).

| **Período** | **Fonte** | **Tratamento** | **Status** |
| --- | --- | --- | --- |
| 1996–2003 | Ipea, com dados brutos da STN | Valores publicados em R$ milhões, a preços constantes de 2005 | Reconstrução oficial |
| 2004–2011 | STN — Consolidação das Contas Públicas | Despesa anual consolidada das três esferas | Fonte primária |
| 2012–2025 | Anuário Brasileiro de Segurança Pública | Valores anuais harmonizados conforme a edição de referência | Publicação sistematizada |

#### 2.1. Período 1996–2003: reconstrução do Ipea

Para 1996–2003, utilizaram-se os valores da Tabela 3.1, “Despesas em segurança pública por esfera de governo – 1995 a 2005”, do estudo Análise dos custos e consequências da violência no Brasil, de Daniel R. C. Cerqueira, Alexandre X. Y. Carvalho, Waldir J. A. Lobão e Rute I. Rodrigues. A tabela apresenta separadamente as despesas de municípios, estados e União e informa como fonte dos dados brutos a STN.

A adoção dessa reconstrução resolve uma limitação dos arquivos históricos: antes da aplicação uniforme da classificação funcional estabelecida pela Portaria MOG nº 42/1999, parte dos entes registrava os dispêndios na rubrica conjunta “Defesa Nacional e Segurança Pública”. Por isso, os valores isolados sob a rubrica Segurança Pública em 2000 e 2001 não representam o total nacional e não foram utilizados. A série do Ipea permite manter a cobertura das três esferas sem atribuir integralmente à segurança pública os gastos da categoria conjunta.

Os valores publicados pelo Ipea estão em milhões de reais, a preços constantes de 2005, corrigidos originalmente pelo IGP-DI. Na base final, foram convertidos para reais pela multiplicação por um milhão. Como já se encontravam expressos em preços de 2005, não foram tratados como valores nominais dos anos de ocorrência.

#### 2.2. Período 2004–2011: Consolidação das Contas Públicas

Para 2004–2011, utilizaram-se os registros da publicação Consolidação das Contas Públicas – Séries Temporais, da STN. A planilha reúne as contas da União, dos estados e do Distrito Federal e dos municípios e disponibiliza uma aba consolidada nacional. O valor anual foi extraído da função Segurança Pública na consolidação das três esferas.

A série começa em 2004 nesta etapa de harmonização porque, a partir desse exercício, a classificação separada de Segurança Pública apresenta cobertura nacional adequada e abertura por subfunções. Os valores correspondem ao próprio exercício financeiro e foram tratados como valores nominais do ano. A composição inclui Policiamento, Defesa Civil, Informação e Inteligência e Demais Subfunções. Quando a abertura por subfunção não está disponível, o total da função é preservado sem interpretar campos vazios ou zerados como ausência efetiva de gasto.

#### 2.3. Período 2012–2025: Anuários Brasileiros de Segurança Pública

Para 2012–2025, os valores foram obtidos nas edições anuais do Anuário Brasileiro de Segurança Pública, produzido pelo Fórum Brasileiro de Segurança Pública. Os anuários sistematizam as despesas de União, estados e Distrito Federal e municípios nas mesmas categorias gerais da função Segurança Pública. Para os anos em que a desagregação por esfera estava disponível na base de trabalho, o gasto nacional foi calculado pela soma dos três componentes; nos demais, foi utilizado o total nacional publicado.

As edições do Anuário podem apresentar o ano do gasto e o ano monetário de referência de forma distinta. Por isso, a base mantém separadamente as variáveis ano e ano_base_preco. O primeiro identifica o exercício ao qual o gasto se refere; o segundo determina o fator empregado na atualização monetária. Essa distinção impede que um valor já expresso nos preços da edição seja corrigido novamente a partir do ano incorreto.

### 3. Harmonização e construção do gasto total

A série final foi formada por encadeamento das fontes nos limites temporais definidos: Ipea até 2003, STN de 2004 a 2011 e Anuário de 2012 a 2025. Nos períodos de sobreposição, as fontes foram utilizadas para verificar ordem de grandeza e continuidade, mas não foram somadas entre si. Para cada ano t, o gasto nacional é definido por:

$$
GSP_t = G_t^{U} + G_t^{E} + G_t^{M},
$$

em que $GSP_{t}$ representa o gasto total com segurança pública; $G^{U}_{t}$, a despesa da União; $G^{E}_{t}$, a despesa dos estados e do Distrito Federal; e $G^{M}_{t}$, a despesa dos municípios. Quando a fonte disponibiliza apenas o total consolidado, $GSP_{t}$ é utilizado diretamente. A ausência de decomposição por esfera ou subfunção em alguns anos não foi preenchida por imputação, pois o objetivo principal é estimar o total anual nacional.

### 4. Atualização monetária

Todos os resultados foram convertidos para preços constantes de dezembro de 2025 pelo Índice Nacional de Preços ao Consumidor Amplo (IPCA). A atualização utiliza o ano-base dos preços do valor de origem, e não necessariamente o ano do gasto. Formalmente:

$$
GSP_t^{\mathrm{dez.\,2025}} = GSP_t^{\mathrm{origem}} \times I(b_t \rightarrow \text{dez. 2025}),
$$

em que $b_{t}$ é o ano-base dos preços e I($b_{t}$ → dez. 2025) é o fator acumulado do IPCA entre essa referência e dezembro de 2025. Para 1996–2003, $b_{t}$ = 2005, pois todos os valores do Ipea já estão a preços constantes de 2005. Para 2004–2011, $b_{t}$ corresponde ao próprio exercício. Para 2012–2025, utiliza-se o ano de referência monetária registrado para a edição do Anuário. Esse procedimento torna comparáveis valores originalmente publicados sob diferentes referências de preços.

### 5. Diferenças em relação ao estudo original

A atualização amplia substancialmente a cobertura temporal do estudo original e substitui a aplicação de uma única fonte a toda a série por um encadeamento transparente de fontes compatíveis com cada período. A revisão também distingue explicitamente o ano do gasto do ano-base dos preços, preserva o total consolidado quando a decomposição não está disponível e documenta a quebra classificatória que impede o uso direto dos valores parciais da STN em 2000 e 2001.

Não foram realizadas imputações para completar esferas de governo ou subfunções.

### 6. Limitações

A principal limitação decorre da combinação de fontes e regimes de classificação ao longo do tempo. Embora todas as parcelas busquem medir a despesa pública na função Segurança Pública, mudanças contábeis, revisões das edições e diferenças de cobertura podem afetar a comparabilidade fina entre anos. A série de 1996–2003 depende de valores arredondados em milhões de reais e de uma reconstrução secundária oficial; já as séries posteriores preservam maior detalhe numérico.

Além disso, a classificação funcional registra a finalidade orçamentária declarada, não permitindo afirmar que cada despesa decorre exclusivamente da criminalidade. Atividades de defesa civil, inteligência e outras ações públicas podem responder também a riscos e funções institucionais mais amplas. Por essa razão, os resultados devem ser interpretados como uma medida abrangente do gasto público classificado em Segurança Pública, e não como uma estimativa causal da parcela que desapareceria integralmente na ausência de crime.

### 7. Fontes

[Cerqueira et al. — Análise dos custos e consequências da violência no Brasil (Tabela 3.1)](https://repositorio.ipea.gov.br/server/api/core/bitstreams/8a55de3f-48a0-42a4-98e8-a2d13dfa66bd/content)

[STN — Consolidação das Contas Públicas: Séries Temporais](https://www.tesourotransparente.gov.br/publicacoes/consolidacao-das-contas-publicas-series-temporais/2012/114)

[Fórum Brasileiro de Segurança Pública — Anuário Brasileiro de Segurança Pública](https://forumseguranca.org.br/publicacoes/anuario-brasileiro-de-seguranca-publica/)

## Gastos com segurança privada

### 1. Objetivo e delimitação da estimação

Os gastos com segurança privada foram estimados pelo custo anual do trabalho associado a ocupações de vigilância, guarda e proteção privada no Brasil. A medida reúne a massa de rendimentos dos postos formais e informais e acrescenta, apenas à parcela formal, os custos trabalhistas e benefícios suportados pelo empregador. Não são incorporados gastos das famílias e empresas com equipamentos, sistemas eletrônicos, seguros ou outros serviços que não apareçam como remuneração ou custo do trabalho.

A série principal cobre 1996–2025. Para 1996–2011, utiliza a antiga Pesquisa Nacional por Amostra de Domicílios (PNAD anual); para 2012–2025, utiliza a PNAD Contínua. A Relação Anual de Informações Sociais (RAIS) foi processada como fonte auxiliar de validação da parcela formal, mas não foi encadeada nem somada à série principal. Todos os resultados nacionais são apresentados em preços constantes de dezembro de 2025.

### 2. Fontes de dados e cobertura temporal

A cobertura de três décadas exigiu combinar duas pesquisas domiciliares com classificações ocupacionais, instrumentos e desenhos amostrais distintos. O quadro resume o papel de cada fonte. A estimativa final emprega exclusivamente as duas PNADs, enquanto RAIS e o estudo setorial da Federação Nacional das Empresas de Segurança e Transporte de Valores (Fenavist) cumprem funções auxiliares específicas.

| **Período** | **Fonte** | **Uso na estimação** | **Status** |
| --- | --- | --- | --- |
| 1996–2011 | PNAD anual/IBGE | Postos, formalidade operacional e rendimento do trabalho principal | Série principal |
| 2012–2025 | PNAD Contínua/IBGE | Postos e rendimentos dos trabalhos principal e secundário | Série principal |
| 1996–2025 | RAIS/MTE | Comparação do emprego e da massa salarial formais | Robustez |
| Base 2012 | III ESSEG/Fenavist | Construção do multiplicador de custo do trabalho formal | Parâmetro |

### 3. Recorte ocupacional e cenário adotado

As três classificações vigentes ao longo da série não possuem uma correspondência perfeita. Por isso, foram construídos dois cenários em cada período: um estrito, concentrado nas categorias mais diretamente identificadas com vigilância e guarda de segurança, e um ampliado, que acrescenta categorias limítrofes. O cenário ampliado foi adotado como estimativa principal; o estrito foi mantido apenas para análise de sensibilidade.

| **Período** | **Classificação** | **Cenário estrito** | **Cenário ampliado adotado** |
| --- | --- | --- | --- |
| 1996–2001 | Classificação de ocupações usada pela PNAD/Censo 1991 | 843 (vigias) e 869 (vigilantes/guardas particulares) | 841 (porteiros), 843 e 869 |
| 2002–2011 | CBO-Domiciliar | 5173 (vigilantes e guardas de segurança) | 5173 e 5174 (guardas e vigias) |
| 2012–2025 | COD 2010 | 5414 (guardas de segurança) | 5414 e 5419 (trabalhadores dos serviços de proteção e segurança não classificados anteriormente) |

A mudança dos códigos entre 2001/2002 e 2011/2012 é tratada como uma harmonização conceitual, não como equivalência individual entre ocupações. Os códigos mais amplos 841, 5174 e 5419 aumentam a cobertura, mas também podem incluir atividades de portaria, vigia ou proteção que não correspondem ao núcleo regulamentado da segurança privada. Essa é uma das razões para preservar o cenário estrito como referência de sensibilidade.

### 4. PNAD anual, 1996–2011

#### 4.1. Microdados, variáveis e população analisada

Foram utilizados os arquivos de pessoas e os dicionários ou programas de leitura oficiais de cada edição. Entre 1996 e 2001, as posições dos campos variam entre os leiautes e foram parametrizadas ano a ano. Entre 2002 e 2009, as posições e larguras foram extraídas dos programas SAS oficiais; em 2011, utilizou-se o dicionário oficial dicPNAD2011.

| **Variável/campo** | **Conteúdo** | **Função no cálculo** |
| --- | --- | --- |
| V9906 / campo de ocupação | Ocupação no trabalho principal | Aplicar os códigos do cenário estrito ou ampliado |
| V4704 / condição | Condição de atividade/ocupação | Manter registros com código 1 no recorte adotado |
| V4706 / posição | Posição na ocupação no trabalho principal | Separar carteira assinada e demais posições privadas |
| V4718 / rendimento | Rendimento mensal do trabalho principal | Calcular rendimento médio e massa mensal |
| V4729 / peso | Peso da pessoa | Expandir a amostra para o total populacional |
| V9907 | Atividade do trabalho principal | Importada para auditoria; não integra o filtro final |

A população-alvo é formada por pessoas ocupadas no trabalho principal nas ocupações selecionadas e nas posições 01 (empregado com carteira), 04 (outro empregado sem carteira), 09 (conta própria) e 10 (empregador). Militares, funcionários públicos estatutários e as demais posições não entram no recorte, reduzindo a sobreposição direta com o eixo de segurança pública.

#### 4.2. Formalidade e rendimento

A classificação de formalidade da PNAD anual é operacional. A posição 01 é tratada como trabalho formal com carteira; as posições 04, 09 e 10 são agregadas como informais ou “demais posições”. Essa regra não equivale a uma definição jurídica completa de informalidade: em especial, empregadores e trabalhadores por conta própria podem possuir registro empresarial.

O rendimento utilizado é o mensal do trabalho principal. Valores vazios, não numéricos, negativos e o código 999999999999, correspondente a rendimento sem declaração, são tratados como ausentes. Em cada ano, a renda ausente é imputada pela média ponderada dos declarantes da mesma célula ocupação × posição. O processamento é interrompido se uma célula que necessita de imputação não possuir doador, evitando substituições silenciosas por médias mais agregadas.

#### 4.3. Estimação e anualização

O número de trabalhadores corresponde à soma dos pesos das pessoas no recorte. A renda média mensal é a média ponderada do rendimento observado ou imputado. A massa mensal é a soma do produto entre rendimento e peso; a massa anual é obtida pela multiplicação por 12. Antes da atualização pelo IPCA, os valores são nominais do respectivo ano e não incluem encargos ou benefícios patronais.

$$
M_{g,t} = 12 \times \sum_{i \in g} w_i y_i,
$$

em que M g,t é a massa anual do grupo g (formal ou informal) no ano t; w i é o peso da pessoa; e y i é o rendimento mensal final. Como a antiga PNAD considera apenas o trabalho principal, cada pessoa pode contribuir com no máximo um posto de segurança privada por ano.

#### 4.4. Anos sem PNAD: 2000 e 2010

A antiga PNAD não foi realizada em 2000 e 2010 em razão dos Censos Demográficos. Para preencher essas lacunas, o número de trabalhadores foi copiado do ano imediatamente anterior: 1999 para 2000 e 2009 para 2010. O mesmo procedimento foi aplicado à massa salarial nominal. Em seguida, o valor copiado foi atualizado para preços de dezembro de 2025 utilizando o fator de IPCA correspondente ao ano imputado, isto é, 2000 ou 2010.

Esse tratamento equivale a manter constante o valor nominal, não o poder de compra, entre os dois anos. Consequentemente, a série a preços constantes registra uma variação mecânica nesses pontos. Os valores de 2000 e 2010 devem ser identificados como imputados e não possuem incerteza amostral própria.

### 5. PNAD Contínua, 2012–2025

#### 5.1. Microdados e desenho amostral

Os microdados anuais foram obtidos com o pacote PNADcIBGE, que faz a leitura dos arquivos oficiais do IBGE e constrói o objeto de desenho amostral utilizado pelo pacote survey. O processamento emprega labels = FALSE, deflator = TRUE e design = TRUE. Foi usada a primeira entrevista nos anos de 2012–2019 e 2022–2025 e a quinta entrevista em 2020 e 2021, conforme recomendação do próprio IBGE.

As estimativas pontuais e os intervalos de confiança de 95% são obtidos com svytotal, preservando estratos, conglomerados e pesos do desenho. A base de resultados mantém os intervalos para auditoria, embora a série consolidada utilize as estimativas pontuais.

#### 5.2. Variáveis e justificativas

| **Variável** | **Conteúdo** | **Por que é utilizada** |
| --- | --- | --- |
| V4010 | Código da ocupação no trabalho principal | Identificar 5414 e 5419 no trabalho principal |
| V4041 | Código da ocupação no trabalho secundário | Incluir um segundo posto de segurança da mesma pessoa |
| V4029 | Carteira assinada no trabalho principal | Classificar como formal o emprego com carteira |
| V4019 | Registro do negócio principal no CNPJ | Classificar como formal empregadores e conta própria registrados |
| V4048 | Carteira assinada no trabalho secundário | Aplicar a mesma regra ao trabalho secundário |
| V4046 | Registro do negócio secundário no CNPJ | Aplicar a mesma regra ao trabalho secundário |
| V403312 | Rendimento bruto/retirada mensal habitual do trabalho principal, em dinheiro | Calcular a massa do trabalho principal |
| V405012 | Rendimento mensal habitual do trabalho secundário, em dinheiro | Calcular a massa do trabalho secundário |
| CO2 | Deflator para rendimento habitual a preços médios do último ano | Harmonizar rendimentos para preços médios de 2025 |

#### 5.3. Postos, formalidade e massa salarial

No cenário ampliado, cria-se um indicador para cada trabalho cujo código seja 5414 ou 5419. Os indicadores dos trabalhos principal e secundário são somados; portanto, a unidade estimada é o posto de trabalho, e uma pessoa pode contribuir com dois postos quando exerce segurança privada em ambos os trabalhos.

Um posto é classificado como formal quando há carteira assinada ou registro do negócio no CNPJ. As perguntas são aplicáveis a posições distintas: carteira para empregados e CNPJ para empregadores ou conta própria. É informal o posto com resposta negativa à variável aplicável. Para cada trabalho, o rendimento somente é somado ao grupo ocupacional e de formalidade correspondente.

Os totais são estimados separadamente para postos formais, informais e totais, bem como para suas massas mensais. Os valores mensais são anualizados por 12.

#### 5.4. Correção monetária e revisão do deflator

A documentação do IBGE distingue os deflatores por finalidade. CO2 é o deflator apropriado aos rendimentos habituais quando se deseja expressá-los a preços médios do último ano do arquivo de deflatores; CO3 é específico para indicadores associados à linha internacional de pobreza do ODS 1.

### 6. Conversão da massa formal em custo do trabalho

A massa salarial formal mede remunerações recebidas pelos trabalhadores, mas não todo o dispêndio do empregador. Para aproximar o custo amplo do trabalho formal, aplicou-se um multiplicador de 1,86, construído a partir do III Estudo do Setor de Segurança Privada (III ESSEG), da Fenavist, com base em 2012.

O estudo estima uma massa salarial entre R$ 12,7 bilhões e R$ 13,3 bilhões, cujo ponto médio é aproximadamente R$ 13,0 bilhões. Somando os pontos médios informados para FGTS, contribuições patronais ao INSS e Sistema S, indenizações, outros encargos sociais, alimentação, vale-transporte, uniformes, treinamento, assistência médica e seguro de vida, obtém-se aproximadamente R$ 24,1 bilhões. Assim, 24,1 ÷ 13,0 ≈ 1,86.

O parâmetro representa um conceito amplo de custo do trabalho, não apenas encargos patronais estritos. Ele é aplicado somente à massa formal.

$$
GSP_t = 1{,}86 \times M_{F,t} + M_{I,t},
$$

em que GSP t é o gasto anual com segurança privada; M F,t é a massa salarial anual formal; e M I,t é a massa salarial anual informal, todas na mesma referência de preços. A aplicação de um parâmetro fixo a toda a série supõe que a razão entre custo total e salário permaneceu constante desde 1996, hipótese documentada como limitação.

### 7. Estimativas auxiliares com a RAIS

Também foram produzidas estimativas com os microdados da RAIS, do Ministério do Trabalho e Emprego, para comparar o número de vínculos formais e a massa salarial formal com os resultados das pesquisas domiciliares. A RAIS é um registro administrativo anual e cobre apenas relações formais declaradas pelos estabelecimentos; não permite estimar a parcela informal que integra o conceito principal deste eixo.

Os resultados da RAIS e das PNADs apresentam a mesma ordem de grandeza e convergem especialmente nos anos mais recentes, embora não coincidam. As diferenças são esperadas: RAIS mede vínculos formais administrativos, enquanto as pesquisas domiciliares estimam postos ou pessoas ocupadas e incluem emprego em empresas de qualquer atividade quando a ocupação é de segurança. Por essas razões, a RAIS foi usada como teste de robustez e plausibilidade, sem substituir, completar ou ser somada aos valores da PNAD anual e da PNAD Contínua.

### 8. Atualização monetária e construção da série final

As massas nominais da PNAD anual são atualizadas diretamente para dezembro de 2025 pelo IPCA. Na PNAD Contínua, os rendimentos habituais são convertidos para preços médios de 2025 com CO2. O multiplicador 1,86 é adimensional e pode ser aplicado antes ou depois da atualização monetária, desde que massa formal e informal estejam na mesma referência de preços.

A série final encadeia a PNAD anual até 2011 e a PNAD Contínua a partir de 2012. As fontes não são somadas nos anos de sobreposição. Para cada ano, seleciona-se o cenário ampliado, calcula-se o custo formal com o multiplicador e adiciona-se a massa informal.

### 9. Validações e controles de qualidade

Os scripts verificam a existência e unicidade dos arquivos e leiautes, a presença das variáveis necessárias, a validade dos pesos, a existência de doadores para a imputação da PNAD anual e a ausência de rendimentos finais inválidos. Também conferem que o cenário ampliado nunca tenha menos observações, trabalhadores ou massa do que o estrito e que as agregações por ocupação e formalidade reproduzam os totais anuais.

As saídas preservam diagnósticos de imputação, metadados dos arquivos, leiautes utilizados, totais por cenário e decomposições por formalidade. Na PNAD Contínua, são armazenados os intervalos de confiança de 95%. A RAIS oferece uma verificação externa adicional da trajetória do componente formal.

### 10. Limitações

A principal limitação é a mudança de pesquisa e de classificação ocupacional. A PNAD anual contabiliza pessoas no trabalho principal; a PNAD Contínua contabiliza postos nos trabalhos principal e secundário. Além disso, os códigos ampliados incluem ocupações limítrofes cuja vinculação à segurança privada pode variar. Assim, a variação entre 2011 e 2012 não deve ser interpretada exclusivamente como mudança econômica do setor.

As definições de formalidade também diferem. Na PNAD anual, somente a posição com carteira é formal e conta própria são agregados às demais posições. Na PNAD Contínua, carteira ou CNPJ definem formalidade.

Os anos 2000 e 2010 são imputados pela cópia dos valores nominais anteriores e, portanto, apresentam movimentos reais mecânicos após a deflação. O multiplicador 1,86 deriva da estrutura de custos observada em 2012 e é mantido constante em todo o período, sem captar mudanças tributárias, salariais ou nos benefícios. Finalmente, a medida cobre o custo do trabalho das ocupações selecionadas; não representa o faturamento integral do setor nem todos os gastos privados de prevenção e proteção.

### 11. Fontes

[IBGE — PNAD anual: microdados, dicionários e documentação](https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_anual/)

[IBGE — PNAD Contínua: página oficial da pesquisa](https://www.ibge.gov.br/estatisticas/sociais/trabalho/17270-pnad-continua.html)

[IBGE — PNAD Contínua anual por visita: microdados e documentação](https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Anual/Microdados/Visita/)

[IBGE — Documentação do deflacionamento anual da PNAD Contínua](https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Anual/Microdados/Visita/Documentacao_Geral/deflacionamento_PNADC_anual_visita.txt)

[IBGE — Classificação de Ocupações para Pesquisas Domiciliares (COD 2010)](https://ftp.ibge.gov.br/Censos/Censo_Demografico_2010/metodologia/anexos/anexo_7_ocupacao_cod.pdf)

[IBGE/Concla — Estrutura da CBO-Domiciliar](https://cnae.ibge.gov.br/images/concla/estrutura/CBODomicilar.xls)

[PNADcIBGE — documentação do pacote no CRAN](https://cran.r-project.org/web/packages/PNADcIBGE/refman/PNADcIBGE.html)

[MTE — Microdados da RAIS e do Caged](https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/acoes-e-programas/programas-projetos-acoes-obras-e-atividades/estatisticas-trabalho/microdados-rais-e-caged)

[Fenavist — III Estudo do Setor de Segurança Privada (III ESSEG)](https://fenavist.org.br/wp-content/uploads/2019/05/III_ESSEG.pdf)

[IBGE — Índice Nacional de Preços ao Consumidor Amplo (IPCA)](https://www.ibge.gov.br/estatisticas/economicas/precos-e-custos/9256-indice-nacional-de-precos-ao-consumidor-amplo.html)

## Gastos com encarceramento

### 1. Objetivo e delimitação da estimação

Este eixo estima, para o Brasil e para cada ano de 1996 a 2025, o dispêndio público associado ao encarceramento. A medida final reúne dois componentes: (i) o valor anual dos benefícios de auxílio-reclusão emitidos pelo Regime Geral de Previdência Social; e (ii) as despesas da União e das Unidades da Federação (UFs) classificadas na subfunção 421 — Custódia e Reintegração Social. Os valores são apresentados em reais constantes de dezembro de 2025.

A unidade temporal é o exercício financeiro. A unidade espacial do resultado principal é o Brasil; contudo, a parcela estadual foi construída a partir dos registros das 27 UFs, o que permitiu identificar separadamente lacunas de cobertura geográfica. A versão final não adiciona uma estimativa autônoma de gasto com pessoal, decisão detalhada na Seção 4.

A subfunção 421 foi instituída na classificação funcional estabelecida pela Portaria MOG nº 42, de 14 de abril de 1999. A transição da classificação anterior para essa estrutura dificulta a comparação direta de registros do fim dos anos 1990 com os registros posteriores. Por essa razão, bases históricas que não representavam o mesmo conceito foram rejeitadas como observações diretas; para 1996–2003, adotaram-se os procedimentos de reconstrução descritos nas Seções 6 a 8, preservando o Balanço Geral da União (BGU) de 2000 como âncora parcial.

### 2. Componentes, fontes e cobertura temporal

| **Componente** | **Período** | **Fonte principal** | **Tratamento** |
| --- | --- | --- | --- |
| Auxílio-reclusão | 1996–2025 | AEPS; Suplemento Histórico do AEPS; Base Estatística da Previdência Social; BEPS | Observado em todos os anos |
| União — subfunção 421 | 2001–2025 | SIGA Brasil | Liquidado observado; transferências às UFs retiradas |
| União — âncora | 2000 | BGU 2000 | Empenhado observado; liquidação e retirada de transferências calibradas |
| UFs — subfunção 421 | 2004–2013 | Execução Orçamentária de Estados/FINBRA-STN | Empenhado em 2004–2010; liquidado em 2011–2013 |
| UFs — subfunção 421 | 2014–2025 | Siconfi/FINBRA — DCA, Anexo I-E | Liquidado; cobertura incompleta em parte dos anos |
| População prisional | 1995–2007 | Infopen 2016 | Variável auxiliar da retroprojeção |
| Remuneração estadual | 1995–2007 | Atlas do Estado Brasileiro/Ipea | Variável auxiliar da retroprojeção |
| Quantitativo de pessoal | 2014–2025 | Infopen/SISDEPEN | Apenas indicador auxiliar; excluído do total |

#### 2.1. Auxílio-reclusão

O conceito escolhido é o valor anual de benefícios emitidos, somando clientelas urbana e rural. Esse fluxo representa o dispêndio realizado ao longo do ano e não deve ser confundido com o valor dos benefícios concedidos no exercício, que capta somente novas concessões. A opção por benefícios emitidos mantém a mesma grandeza econômica ao longo da série.

Para 1996–1998, foram usados os valores acumulados até dezembro da Tabela 7.12 do Suplemento Histórico do AEPS 2017. Para 1999–2013, foram usados os valores de benefícios emitidos, acumulados no ano, da Tabela 1.12 do mesmo suplemento. Os anos de 2014 e 2015 foram extraídos da Tabela B.3 do AEPS 2015. Para 2016, a Tabela B.3 do AEPS 2016 substituiu o dado preliminar baseado em benefícios concedidos; por isso, a planilha de origem registra esse ano como “observado corrigido”, enquanto a série final o classifica como observado no conceito definitivo. Para 2017–2024, foram utilizados os valores da Base Estatística da Previdência Social.

O valor de 2025 foi calculado pela soma dos 12 Boletins Estatísticos da Previdência Social (BEPS) mensais. O resultado é R$ 269.295.737,80. Não houve imputação no subeixo de auxílio-reclusão.

#### 2.2. Despesas da União com custódia e reintegração

A fonte definitiva para 2001–2025 é o SIGA Brasil, do Senado Federal. Foram selecionadas as despesas liquidadas da subfunção 421 — Custódia e Reintegração Social. O Portal da Transparência foi utilizado em uma etapa preliminar de reconstrução e como verificação auxiliar, sobretudo para 2014–2015, mas não foi mantido como fonte da série padronizada, que adota o SIGA Brasil em todo o período disponível.

Para impedir dupla contagem federativa, o gasto da União foi reduzido das transferências destinadas a estados e ao Distrito Federal. Na variável de modalidade de aplicação, foram excluídos os códigos 30 — transferências a estados e ao Distrito Federal — e 31 — transferências fundo a fundo a estados e ao Distrito Federal. Foram preservadas as modalidades 40 e 41 (municípios), 50 (instituições privadas sem fins lucrativos), 72 (consórcios públicos), 80 (exterior), 90 (aplicações diretas) e 91 (aplicação direta intraorçamentária), porque a parcela estadual da série não incorpora despesas municipais nem permite atribuir automaticamente as demais modalidades a uma UF específica.

$$
\text{União líquida}_t = \text{União liquidada bruta}_t - \text{transferências às UFs nas modalidades 30 e 31}_t
$$

#### 2.3. Despesas das UFs com custódia e reintegração

Para 2004–2013, foi utilizada a publicação Execução Orçamentária de Estados [1995–2013], do Tesouro Nacional/FINBRA. A disponibilidade contábil varia dentro desse arquivo: em 2004–2010, a série recuperada corresponde à despesa empenhada; em 2011–2013, à despesa liquidada. Para 2014–2025, foram consultadas as contas anuais do Siconfi/FINBRA, DCA — Anexo I-E, linha 14.421 — Custódia e Reintegração Social, na coluna Despesas Liquidadas. A extração foi realizada pela consulta pública e pela API do Tesouro Nacional.

A publicação histórica contém dados desde 1995, e também foi examinada uma base de execução orçamentária estadual referente a 1986–1995. Esses registros não foram empregados como observações do eixo porque a classificação anterior à Portaria MOG nº 42/1999 não identifica, com equivalência suficiente, a subfunção 421 adotada na série final. A cobertura direta das UFs começa, portanto, em 2004.

#### 2.4. Variáveis auxiliares

A população prisional histórica foi obtida no relatório Infopen 2016. A remuneração real mensal dos vínculos do Poder Executivo estadual foi obtida no Atlas do Estado Brasileiro, do Ipea, e agregada por média simples das 27 UFs. Essas duas séries são usadas apenas na retroprojeção das despesas estaduais; a população prisional também determina a retroprojeção federal. Os quantitativos de trabalhadores do sistema prisional foram extraídos das bases Infopen/SISDEPEN de 2014 a 2025 e são mantidos em aba auxiliar para análise de tendência e verificação de consistência, sem entrar no total de gastos.

### 3. Estágios da despesa e padrão contábil

A série distingue empenho, liquidação e pagamento. O empenho reserva dotação e constitui obrigação orçamentária sujeita ao implemento de condição. A liquidação verifica, com base nos documentos comprobatórios, o direito adquirido pelo credor. O pagamento é a saída financeira posterior à liquidação. Restos a pagar não processados são despesas empenhadas que ainda não foram liquidadas ao final do exercício; restos a pagar processados já foram liquidados, mas ainda não pagos. Esses estágios não são parcelas somáveis de uma mesma despesa.

O padrão analítico escolhido para custódia e reintegração é a despesa liquidada. Esse estágio aproxima o valor de bens e serviços cuja entrega ou execução já foi reconhecida e reduz a variação gerada por empenhos que podem ser cancelados ou inscritos para execução futura. Assim, a União é observada no liquidado em 2001–2025; as UFs são observadas no liquidado em 2011–2025; e os valores estaduais de 2004–2010 são harmonizados de empenhado para liquidado. O ano federal de 2000 recebe conversão específica baseada no BGU.

**Nota: **A padronização não transforma os registros originais em microdados liquidados. Ela aplica razões observadas a agregados. Por isso, a série distingue explicitamente o status “harmonizado” do status “observado”.

### 4. Exclusão da estimativa autônoma de gastos com pessoal

A subfunção 421 é uma classificação funcional da despesa pública e pode registrar despesas com pessoal e encargos, custeio, serviços, investimentos e outras naturezas destinadas à custódia e à reintegração social. O componente de pessoal já pode, portanto, estar incluído nos valores do SIGA Brasil, do FINBRA e do Siconfi. Como as bases disponíveis não permitem separar, para todos os anos e entes, qual parcela da folha já está dentro da subfunção 421, somar novamente “quantidade de servidores × remuneração média” introduziria uma sobreposição de magnitude desconhecida e viés de alta no total.

A decisão final foi excluir o gasto estimado com pessoal do indicador monetário.

### 5. Cobertura geográfica das UFs

A ausência de informação para uma ou mais UFs foi tratada separadamente do estágio contábil do agregado estadual. Em cada ano com cobertura incompleta, o valor da UF ausente foi imputado pela média aritmética simples das UFs que reportaram naquele mesmo ano. Em 2004–2010, a média foi calculada sobre o estágio empenhado e a soma completada foi posteriormente harmonizada para liquidado. Em 2014–2025, a média foi calculada diretamente sobre despesas liquidadas. O agregado nacional estadual corresponde à soma das UFs observadas e imputadas.

$$
\text{UF ausente}_{i,t} = \text{média simples dos valores reportados pelas UFs no ano }t
$$

| **Ano** | **UFs sem informação direta** |
| --- | --- |
| 2004 | AC, ES, MG, RO, RS, SC e TO |
| 2005 | AC, AL, ES, MG, MT, PA, RO, RS, SC e TO |
| 2006 | AC, ES, MG, MT, PA, RO, RS, SC e TO |
| 2007 | AC, ES, MT, PA, RO, RS, SC e TO |
| 2008 | AC, MG, MT, PA, RJ, RO, RS e TO |
| 2009 | AC, MG, MT, PA, PE, RJ, RO, RS e TO |
| 2010 | AC, MA, MT, PA, RJ, RO, RS e TO |
| 2011–2013 | Nenhuma UF imputada |
| 2014 | DF, PA, PR, RJ, RO e RS |
| 2015 | PA, RJ, RO e RS |
| 2016 | MG, PA, RJ, RO, RS, SP e TO |
| 2017 | AL, MG, PA, RJ, RO, RR e RS |
| 2018 | AL, MG, PA, RJ, RO e RS |
| 2019 | ES, MG, PA, RJ, RO e RS |
| 2020 | CE, MG, PA, RJ e RS |
| 2021 | CE, MG, PA, RJ e RS |
| 2022 | CE, MG, PA, RJ e RS |
| 2023 | CE, MG, PA, RJ e RS |
| 2024 | MG, PA, PI, RJ, RS e SE |
| 2025 | CE, MG, PA, PI, RJ, RS e SE |

**Nota: **Nos anos de 1996–2003, toda a parcela estadual é reconstruída por retroprojeção; por isso, o status de cobertura das UFs é imputado, embora o modelo produza apenas o agregado nacional estadual.

### 6. Harmonização das UFs de empenhado para liquidado

Para preservar a maior quantidade possível de informação e, ao mesmo tempo, reduzir a quebra contábil, os agregados empenhados de 2004–2010 foram convertidos para uma aproximação do liquidado. A razão de conversão foi estimada no triênio 2014–2016, período em que foi possível comparar, sob a mesma subfunção, os agregados empenhados e liquidados das UFs presentes na base. A razão agrupada - soma do liquidado dividida pela soma do empenhado - foi de 0,9638414359 (96,38%).

$$
\rho = \frac{\sum \text{UFs liquidadas}_{2014\text{--}2016}}{\sum \text{UFs empenhadas}_{2014\text{--}2016}} = 0{,}9638414359
$$

$$
\text{UFs liquidadas estimadas}_t = \rho \times \text{UFs empenhadas}_t, \quad t=2004,\ldots,2010
$$

Os anos de 2004–2010 recebem status de valor “harmonizado”, e não “imputado”, porque a informação fiscal original existe e apenas seu estágio foi ajustado por uma regra determinística comum. O agregado harmonizado de 2004, usado como âncora da retroprojeção, é R$ 1.917.921.263,53 em preços de dezembro de 2025.

### 7. Imputação da parcela estadual em 1996–2003

Não foi encontrada fonte primária ou secundária com cobertura nacional e equivalência conceitual suficiente para a subfunção 421 em 1996–2003. A parcela estadual foi, então, retroprojetada a partir do valor harmonizado de 2004. O modelo combina dois direcionadores reais de custo: a população prisional nacional e a remuneração média real dos vínculos do Poder Executivo estadual. Ambos são expressos como índices relativos ao ano-âncora de 2004.

$$
\mathrm{UFs}_t = \mathrm{UFs}_{2004}\left[\lambda\frac{P_t}{P_{2004}} + (1-\lambda)\frac{W_t}{W_{2004}}\right]
$$

Nessa expressão, $P_{t}$ é a população prisional e $W_{t}$ é a média simples, entre as 27 UFs, da remuneração mensal real dos vínculos do Executivo estadual. O peso $\lambda$ foi calibrado por mínimos quadrados, sem intercepto e com normalização em 2004. Foram comparadas, para 2005–2007, as razões efetivamente observadas na série estadual já completada e harmonizada com as razões previstas pela combinação de população e remuneração. O problema de calibração foi:

$$
\widehat{\lambda}=\operatorname*{arg\,min}_{\lambda}\sum_{t=2005}^{2007}\left[\frac{Y_t}{Y_{2004}}-\lambda\frac{P_t}{P_{2004}}-(1-\lambda)\frac{W_t}{W_{2004}}\right]^2
$$

O resultado foi $\lambda$ = 0,492001932. Assim, 49,2002% da variação estrutural é associada à população prisional e 50,7998% à remuneração real estadual. A âncora populacional é $P_{2004}$ = 336.358 pessoas, e a remuneração média real de referência é $W_{2004}$ = R$ 3.968,0625. Todos os valores estaduais de 1996–2003 recebem status “imputado”.

### 8. Imputação da parcela federal em 1996–2000

#### 8.1. Calibração do ano 2000 com o BGU

O BGU 2000 informa R$ 142.590.083,93 de despesa realizada na subfunção 421 e R$ 40.104.307,75 de restos a pagar não processados. A diferença aproxima a despesa liquidada bruta, pois os restos a pagar não processados correspondem à parcela empenhada ainda não liquidada ao final do exercício:

$$
\text{União liquidada bruta}_{2000}=142{.}590{.}083{,}93-40{.}104{.}307{,}75=\text{R\$ }102{.}485{.}776{,}18
$$

O BGU não permite retirar diretamente, com o mesmo detalhamento da série moderna, as transferências às UFs. Para estimar a parcela federal líquida, calculou-se no SIGA Brasil a razão agrupada entre o gasto federal liquidado depois da exclusão das modalidades 30 e 31 e o gasto liquidado bruto em 2001–2003. A parcela retida foi de 0,0560114542, ou 5,6011%.

$$
\theta=\frac{\sum \text{União líquida}_{2001\text{--}2003}}{\sum \text{União bruta}_{2001\text{--}2003}}=0{,}0560114542
$$

$$
\text{União líquida}_{2000}=\text{R\$ }102{.}485{.}776{,}18\times\theta=\text{R\$ }5{.}740{.}377{,}36
$$

Após a atualização monetária, o valor federal de 2000 é R$ 25.393.340,51 em preços de dezembro de 2025. Embora o BGU seja observado, o resultado final de 2000 recebe status “imputado”, porque tanto a conversão para liquidado quanto a retirada das transferências dependem de calibração.

#### 8.2. Retroprojeção de 1996–1999

A parcela federal de 1996–1999 foi retroprojetada do valor líquido real de 2000 em proporção à população prisional. Esse direcionador foi escolhido por representar diretamente a escala do sistema de custódia e por estar disponível na série histórica do Infopen.

$$
\text{União}_t=\text{União}_{2000}\times\frac{P_t}{P_{2000}},\quad t=1996,\ldots,1999
$$

A população de referência é $P_{2000}$ = 232.755. Como o Infopen não informa os anos de 1996 e 1998 na sequência utilizada, esses dois pontos foram interpolados geometricamente entre os anos adjacentes, preservando uma trajetória multiplicativa:

$$
P_{1996}=\sqrt{P_{1995}\times P_{1997}}=159{.}307{,}1044
$$

$$
P_{1998}=\sqrt{P_{1997}\times P_{1999}}=181{.}959{,}9202
$$

Os valores federais de 1996–1999 e as populações interpoladas de 1996 e 1998 recebem status “imputado”. Os valores federais de 2001–2003 são observados diretamente no SIGA Brasil e não são afetados pela retroprojeção estadual.

### 9. Sistema de status da série

| **Status** | **Definição operacional** |
| --- | --- |
| observado | Valor obtido diretamente de fonte oficial no conceito e no estágio contábil adotados para a série. Uma subtração identificável de transferências não altera esse status. |
| harmonizado | Valor fiscal observado, ajustado de modo determinístico para o padrão da série. Aplica-se às UFs de 2004–2010, convertidas de empenhado para liquidado. |
| imputado | Valor ausente ou incomparável reconstruído por média transversal, interpolação, retroprojeção estrutural ou calibração com âncora parcial. |

| **Período** | **Auxílio** | **União** | **UFs — valor** | **UFs — cobertura** |
| --- | --- | --- | --- | --- |
| 1996–2000 | observado | imputado | imputado | imputado |
| 2001–2003 | observado | observado | imputado | imputado |
| 2004–2010 | observado | observado | harmonizado | imputado |
| 2011–2013 | observado | observado | observado | observado |
| 2014–2025 | observado | observado | observado | imputado |

### 10. Atualização monetária

Todos os valores monetários foram convertidos para reais de dezembro de 2025 pelo IPCA. A base contém, para cada exercício, o fator acumulado de correção registrado na coluna deflator_bc_dez_25. A atualização foi aplicada de forma multiplicativa:

$$
\text{Valor em dezembro de 2025}_t=\text{Valor nominal}_t\times\text{fator IPCA}_{t\rightarrow\mathrm{dez./2025}}
$$

Na série, a referência anual é dezembro de cada exercício. Os modelos de retroprojeção estadual e federal foram estimados em preços constantes.

### 11. Controles de consistência e decisões de validação

- Conferência da identidade: custódia total = União líquida de transferências + UFs; encarceramento total = custódia total + auxílio-reclusão.

- Verificação de que as modalidades 30 e 31 foram retiradas da União antes da soma com as UFs.

- Separação entre status do valor estadual e status de cobertura, com identificação anual das UFs imputadas.

- Manutenção dos parâmetros, âncoras e covariáveis em bloco de auditoria da planilha de trabalho: $\rho$, $\lambda$, $\theta$, BGU 2000, população prisional e remuneração real estadual.

- Correção do auxílio-reclusão de 2016 para o conceito de benefícios emitidos e cálculo de 2025 pela soma dos 12 BEPS.

- Exclusão do componente autônomo de pessoal e verificação de que a aba quantitativo_pessoal não alimenta a fórmula do total.

### 12. Limitações

A subfunção 421 não é uma contabilidade de custo por pessoa presa. Ela registra a finalidade orçamentária e pode incluir diferentes naturezas de despesa; também depende da qualidade de classificação de cada ente. A exclusão das transferências evita a principal dupla contagem federativa identificável, mas não permite rastrear integralmente repasses indiretos por municípios, consórcios ou instituições privadas.

A média anual usada para UFs ausentes supõe que as unidades não respondentes sejam semelhantes às respondentes no mesmo exercício. A razão empenhado/liquidado supõe estabilidade suficiente entre o período de calibração e 2004–2010. As retroprojeções de 1996–2003 impõem relações estruturais simples e não captam mudanças institucionais específicas de cada UF. Por isso, os valores imputados devem ser interpretados como estimativas e não como execução orçamentária observada.

A remuneração do Executivo estadual é um indicador agregado de custo do trabalho público, não uma remuneração específica do sistema penitenciário.

### 14. Fontes e referências

1. Ministério do Planejamento. Portaria MOG nº 42, de 14 de abril de 1999. [Acesso à fonte](https://www.gov.br/planejamento/pt-br/assuntos/orcamento/legislacao-sobre-orcamento/arquivos/2012/portaria-mog-no-42-de-14-de-abril-de-1999-atualizado-23-07-2012). Classificação funcional e subfunção 421.

2. Brasil. Lei nº 4.320, de 17 de março de 1964. [Acesso à fonte](https://www.planalto.gov.br/ccivil_03/leis/l4320.htm). Conceitos de empenho, liquidação, pagamento e restos a pagar.

3. Secretaria do Tesouro Nacional. Manual de Contabilidade Aplicada ao Setor Público — 11ª edição. [Acesso à fonte](https://www.tesourotransparente.gov.br/publicacoes/manual-de-contabilidade-aplicada-ao-setor-publico-mcasp/2025/26). Referência contábil complementar.

4. Ministério da Previdência Social. Suplemento Histórico do AEPS 2017. [Acesso à fonte](https://www.gov.br/previdencia/pt-br/outros/imagens/2019/04/aeps2017suphist.pdf). Tabelas 7.12 e 1.12; auxílio-reclusão de 1996–2013.

5. Ministério da Previdência Social. Anuários Estatísticos da Previdência Social. [Acesso à fonte](https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/Dados-estatisticos-previdencia-social-e-inss/anuarios-da-previdencia-social). AEPS 2015 e 2016; Tabela B.3.

6. Ministério da Previdência Social. Boletins Estatísticos da Previdência Social. [Acesso à fonte](https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/Dados-estatisticos-previdencia-social-e-inss/boletins-da-previdencia-social). BEPS e edições anteriores; cálculo de 2025.

7. Senado Federal. SIGA Brasil. [Acesso à fonte](https://www12.senado.leg.br/orcamento/sigabrasil). Despesa federal liquidada na subfunção 421 e modalidades de aplicação.

8. Controladoria-Geral da União. Portal da Transparência. [Acesso à fonte](https://portaldatransparencia.gov.br/). Fonte auxiliar de verificação; não utilizada na série federal final.

9. Tesouro Nacional. Execução Orçamentária de Estados [1995–2013]. [Acesso à fonte](https://www.tesourotransparente.gov.br/publicacoes/relatorio-de-execucao-orcamentaria/2013/26). Despesa estadual na subfunção 421 em 2004–2013.

10. Tesouro Nacional. Siconfi/FINBRA — Contas Anuais. [Acesso à fonte](https://siconfi.tesouro.gov.br/siconfi/pages/public/consulta_finbra/finbra_list.jsf). DCA, Anexo I-E, 2014–2025.

11. Tesouro Nacional. API Siconfi — DCA. [Acesso à fonte](https://apidatalake.tesouro.gov.br/ords/cdwhprd/siconfi/tt/dca). Extração programática das contas anuais.

12. Controladoria-Geral da União. Prestação de Contas do Presidente da República — exercício de 2000. [Acesso à fonte](https://www.gov.br/cgu/pt-br/assuntos/auditoria-e-fiscalizacao/avaliacao-da-gestao-dos-administradores/prestacao-de-contas-do-presidente-da-republica/exercicios-anteriores/2000). BGU 2000; âncora federal.

13. Secretaria Nacional de Políticas Penais. Levantamento Nacional de Informações Penitenciárias — Infopen 2016. [Acesso à fonte](https://www.gov.br/senappen/pt-br/assuntos/noticias/infopen-levantamento-nacional-de-informacoes-penitenciarias-2016/relatorio_2016_22111.pdf). População prisional histórica.

14. Secretaria Nacional de Políticas Penais. Bases de Dados do SISDEPEN. [Acesso à fonte](https://www.gov.br/senappen/pt-br/servicos/sisdepen/bases-de-dados). Quantitativo auxiliar de pessoal, 2014–2025.

15. Instituto de Pesquisa Econômica Aplicada. Atlas do Estado Brasileiro. [Acesso à fonte](https://www.ipea.gov.br/atlasestado/). Remuneração real dos vínculos do Poder Executivo estadual.

16. Banco Central do Brasil. Calculadora do Cidadão — correção de valores. [Acesso à fonte](https://www3.bcb.gov.br/CALCIDADAO/jsp/index.jsp). Metodologia de acumulação de índices de preços.

17. Instituto Brasileiro de Geografia e Estatística. Índice Nacional de Preços ao Consumidor Amplo — IPCA. [Acesso à fonte](https://www.ibge.gov.br/estatisticas/economicas/precos-e-custos/9256-indice-nacional-de-precos-ao-consumidor-amplo.html). Índice de atualização monetária.

18. Secretaria Especial de Assuntos Estratégicos. Custos Econômicos da Criminalidade no Brasil. [Acesso à fonte](https://www.gov.br/secretariageral/pt-br/noticias/2018/setembro/sae-apresenta-estudo-sobre-criminalidade-em-forum-nacional-de-juizes). Estudo metodológico de referência e base para a comparação de decisões.

## Gastos com seguros e perdas materiais

### 1. Objetivo e delimitação da estimação

Este eixo estima, para o Brasil e para cada ano entre 1996 e 2025, dois fluxos econômicos distintos associados à violência patrimonial. O primeiro é o gasto preventivo com seguros, representado pelos prêmios diretos pagos para a proteção de veículos, patrimônio e cargas. O segundo é a perda material realizada, composta por sinistros patrimoniais e de transporte de carga e por uma estimativa independente do valor dos veículos roubados ou furtados que não foram recuperados.

Prêmios e perdas foram mantidos separados durante todo o cálculo. O prêmio remunera a transferência de risco e constitui gasto de proteção; o sinistro representa o custo reconhecido de um evento coberto. Por essa razão, prêmios não foram tratados como perdas, e sinistros não foram tratados como gastos preventivos. A separação também evita que os sinistros automotivos das seguradoras sejam somados à estimativa independente de veículos subtraídos.

A série final é anual, nacional e apresentada em valores reais constantes de dezembro de 2025. O cenário amplo foi adotado em todas as estimativas principais porque oferece a representação mais abrangente dos gastos e perdas com componente criminal relevante. O cenário conservador, mais restritivo, foi calculado e preservado exclusivamente como teste de sensibilidade e como controle contra sobreinclusão.

**Quadro 1 — Componentes do eixo e medida principal**

| **Componente** | **Medida** | **Fonte principal** | **Cobertura final** |
| --- | --- | --- | --- |
| Gasto com seguro automotivo | Prêmio direto | SES/Susep | 1996–2025 |
| Gasto com seguro patrimonial | Prêmio direto | SES/Susep | 1996–2025 |
| Gasto com seguro de carga | Prêmio direto | SES/Susep | 1996–2025 |
| Perda patrimonial | Sinistro híbrido | SES/Susep | 1996–2025 |
| Perda de carga | Sinistro híbrido | SES/Susep | 1996–2025 |
| Perda automotiva | Quantidade × preço × parcela não recuperada | FBSP, SSP-SP, ISP-RJ, AutoSeg/Susep e IBGE | 1996–2025 |

### 2. Fontes de dados e critérios de admissibilidade

#### 2.1. Sistema de Estatísticas da Susep

Para gastos com seguros e para perdas patrimoniais e de carga, foram usadas as bases operacionais do Sistema de Estatísticas da Superintendência de Seguros Privados (SES/Susep), especialmente os arquivos Ses_seguros.csv e Ses_ramos.csv. A primeira base contém registros mensais por empresa e ramo, com variáveis de prêmios e sinistros; a segunda identifica os códigos e as denominações oficiais dos ramos securitários. Os registros foram agregados primeiro no nível mensal e, depois, no nível anual.

A seleção de ramos não foi inferida apenas pela presença de palavras-chave. Cada código e nome oficial foi lido individualmente e classificado segundo quatro perguntas: existência de relação com a criminalidade; possibilidade de identificar a parcela criminal; natureza do bem ou risco protegido; e abrangência da cobertura. Ramos sem relação direta, com vínculo meramente incidental ou cuja parcela criminal não pudesse ser separada de forma defensável foram excluídos.

#### 2.2. Ocorrências de roubos e furtos de veículos

A série nacional observada de roubos e furtos de veículos foi obtida nos Anuários Brasileiros de Segurança Pública do Fórum Brasileiro de Segurança Pública (FBSP). Foram utilizadas as versões revisadas mais recentes disponíveis para cada ano. O conceito adotado é a soma de roubos e furtos de veículos registrados pelas fontes de segurança pública, e não apenas roubos.

A revisão de fontes estabeleceu 2013 como o primeiro ano da série nacional pública, completa e comparável no conceito roubos mais furtos. Edições anteriores do Anuário divulgavam apenas roubos ou informações parciais.

Para 1996–2012, as séries estaduais de São Paulo e do Rio de Janeiro foram usadas como doadoras. A SSP-SP disponibiliza ocorrências de roubo e furto de veículos, e o ISP-RJ mantém série histórica mensal estadual desde 1991. A composição de doadores foi mantida fixa em todo o período para evitar uma quebra artificial decorrente da entrada ou saída de unidades da Federação.

#### 2.3. Valores de referência dos veículos

Os valores de referência foram construídos a partir do Sistema AutoSeg da Susep e dos subitens nacionais do IPCA publicados pelo IBGE na Tabela 7060 do SIDRA. No AutoSeg, a variável de base é a importância segurada média, que representa o valor médio segurado das apólices, ponderado pela exposição. Esse valor é uma aproximação do valor econômico do veículo segurado e não uma cotação individual de mercado.

### 3. Gastos com seguros

#### 3.1. Medida de gasto e agregação

A medida principal é o prêmio direto. Ele corresponde ao valor bruto emitido nas operações contratadas diretamente com os segurados, antes dos mecanismos de resseguro e redistribuição de risco. Entre as variáveis disponíveis, é a que mais se aproxima do desembolso feito por famílias e empresas para adquirir proteção. Prêmio ganho e prêmio retido foram examinados apenas como medidas auxiliares de consistência e não integram o resultado final.

Para cada cenário s e ano t, o gasto foi obtido pela soma dos prêmios diretos dos ramos r classificados no respectivo cenário:

$$
\text{Gasto com seguros}_{s,t}=\sum_r \text{Prêmio direto}_{r,t},\quad \forall r\in s.
$$

A agregação foi feita separadamente para os grupos automotivo, patrimonial e de transporte de carga. A soma dos três grupos forma o gasto total com seguros do eixo. Valores mensais negativos ou ajustes contábeis eventualmente presentes foram mantidos, de modo a preservar o fluxo líquido informado à Susep.

#### 3.2. Cenários e classificação dos ramos

O cenário amplo incorpora ramos com componente criminal relevante, mesmo quando a mesma cobertura também abrange eventos não criminais. O cenário conservador restringe a seleção aos ramos com vínculo mais direto ou maior aderência à finalidade do eixo. As coberturas multirriscos permanecem uma fonte de incerteza, pois o SES não permite decompor o prêmio conforme o evento que motivou a contratação. A existência do cenário conservador torna essa incerteza observável, mas a série principal usa o cenário amplo.

**Quadro 2 — Ramos incluídos no cenário amplo dos gastos com seguros; a última coluna identifica o subconjunto conservador**

| **Código** | **Grupo** | **Ramo oficial** | **Conservador** |
| --- | --- | --- | --- |
| 0111 | Patrimonial | Incêndio Tradicional (run-off) | Não |
| 0114 | Patrimonial | Compreensivo Residencial | Sim |
| 0115 | Patrimonial | Roubo (run-off) | Sim |
| 0116 | Patrimonial | Compreensivo Condomínio | Sim |
| 0117 | Patrimonial | Tumultos | Não |
| 0118 | Patrimonial | Compreensivo Empresarial | Sim |
| 0141 | Patrimonial | Lucros Cessantes | Não |
| 0142 | Patrimonial | Lucros Cessantes — Cobertura Simples | Não |
| 0143 | Patrimonial | Fidelidade | Sim |
| 0167 | Patrimonial | Riscos de Engenharia | Não |
| 0171 | Patrimonial | Riscos Diversos | Não |
| 0173 | Patrimonial | Global de Bancos | Sim |
| 0176 | Patrimonial | Riscos Diversos — Planos Conjugados | Não |
| 0196 | Patrimonial | Riscos Nomeados e Operacionais | Não |
| 0526 | Automóvel | Seguro Popular de Automóvel Usado (run-off) | Não |
| 0531 | Automóvel | Automóvel — Casco | Sim |
| 0621 | Carga | Transporte Nacional | Sim |
| 0622 | Carga | Transporte Internacional | Sim |
| 0627 | Carga | Responsabilidade Civil do Transportador Intermodal (run-off) | Não |
| 0632 | Carga | RCTR-VI-C | Não |
| 0638 | Carga | RCTF-C | Não |
| 0652 | Carga | RCTA-C | Não |
| 0654 | Carga | RCTR-C | Não |
| 0655 | Carga | Responsabilidade Civil por Desaparecimento de Carga (RC-DC) | Sim |
| 0656 | Carga | RCA-C | Não |
| 0658 | Carga | RCOTM-C | Não |

O cenário amplo de gastos contém 26 ramos: 14 patrimoniais, dez de transporte de carga e dois automotivos. O cenário conservador contém dez ramos: seis patrimoniais, três de carga e um automotivo. A nomenclatura preserva as denominações do cadastro da Susep, inclusive indicações de run-off.

#### 3.3. Harmonização dos códigos históricos, 1996–2000

A série histórica exigiu uma harmonização específica porque a codificação dos ramos mudou em setembro de 2000. Até agosto de 2000, o campo de ramo continha identificadores de dois algarismos; a partir de setembro, o código passou a incorporar o grupo e o identificador, conforme a nomenclatura oficial. A transição foi confirmada na base mensal: oito meses no regime antigo e quatro meses no regime novo em 2000.

A igualdade entre o código antigo e os dois últimos dígitos do código novo foi tratada apenas como hipótese candidata. Ela não foi aplicada automaticamente, pois podem existir colisões; o identificador antigo 27, por exemplo, é compatível com mais de um código novo. Cada equivalência precisou combinar presença efetiva no período antigo, identidade do ramo, regra documental e decisão única, sem replicar o mesmo código antigo em duas categorias.

Foram aceitas 17 equivalências efetivamente observadas entre janeiro de 1996 e agosto de 2000. Candidatos que não apareciam no regime antigo ou apresentavam ambiguidade não foram usados no cálculo histórico. A cobertura mensal também foi auditada: um total anual só foi aceito quando os 12 meses estavam representados; ausência de registro não foi convertida automaticamente em zero.

**Quadro 3 — Equivalências validadas para o regime antigo da Susep**

| **Código antigo** | **Equivalência no regime novo** |
| --- | --- |
| 11 | 0111 — Incêndio Tradicional |
| 15 | 0115 — Roubo |
| 17 | 0117 — Tumultos |
| 21 | 0621 — Transporte Nacional |
| 22 | 0622 — Transporte Internacional |
| 31 | 0531 — Automóvel — Casco |
| 41 | 0141 — Lucros Cessantes |
| 42 | 0142 — Lucros Cessantes — Cobertura Simples |
| 43 | 0143 — Fidelidade |
| 52 | 0652 — RCTA-C |
| 54 | 0654 — RCTR-C |
| 55 | 0655 — RC-DC |
| 56 | 0656 — RCA-C |
| 67 | 0167 — Riscos de Engenharia |
| 71 | 0171 — Riscos Diversos |
| 73 | 0173 — Global de Bancos |
| 76 | 0176 — Riscos Diversos — Planos Conjugados |

### 4. Perdas patrimoniais e de carga

#### 4.1. Decomposição e definição dos sinistros

As perdas materiais foram divididas em três componentes: perdas patrimoniais, perdas de carga e perdas automotivas. Os dois primeiros foram estimados com registros de sinistros da Susep. O componente automotivo foi calculado por método independente, combinando a quantidade de veículos roubados ou furtados com um valor médio de referência e uma taxa de recuperação.

Para este eixo, sinistro é o evento coberto pelo contrato de seguro que gera aviso, reconhecimento ou pagamento de indenização pela seguradora. A classificação indica a natureza do bem atingido; ela não implica que todos os eventos cobertos por um ramo decorram de crime. Essa limitação é tratada pela leitura individual dos ramos e pela comparação entre cenários.

Sinistros patrimoniais correspondem a perdas ou danos em imóveis, instalações, equipamentos, estoques e outros ativos de residências, condomínios e empresas. Conforme o ramo, podem incluir roubo e furto, incêndio, tumultos e outros riscos. Sinistros de transporte de carga correspondem a perdas ou danos sofridos pelas mercadorias durante operações nacionais ou internacionais, inclusive desaparecimento, roubo ou furto quando cobertos pela apólice. Algumas modalidades também cobrem acidentes e eventos não criminais.

Sinistros automotivos da Susep podem incluir roubo ou furto, colisão, incêndio, assistência e responsabilidade civil. Como o SES não permite isolar de maneira uniforme a parcela criminal, esses registros foram excluídos das perdas automotivas. A decisão evita tanto a incorporação de eventos alheios à criminalidade quanto a dupla contagem com a estimativa independente de veículos subtraídos.

#### 4.2. Seleção independente dos ramos de perdas

A classificação de perdas foi refeita de forma independente da classificação dos gastos com seguros. O cenário amplo contém 21 ramos: 11 patrimoniais e dez de transporte de carga. O cenário conservador contém sete ramos: quatro patrimoniais e três de carga. Lucros cessantes foram excluídos porque representam perda de rendimento, e não dano material; fidelidade foi excluída porque representa predominantemente perda financeira; riscos cibernéticos permaneceram fora do conceito material.

**Quadro 4 — Ramos incluídos no cenário amplo das perdas patrimoniais e de carga; a última coluna identifica o subconjunto conservador**

| **Código** | **Grupo** | **Ramo oficial** | **Conservador** |
| --- | --- | --- | --- |
| 0111 | Patrimonial | Incêndio Tradicional (run-off) | Não |
| 0114 | Patrimonial | Compreensivo Residencial | Sim |
| 0115 | Patrimonial | Roubo (run-off) | Sim |
| 0116 | Patrimonial | Compreensivo Condomínio | Sim |
| 0117 | Patrimonial | Tumultos | Não |
| 0118 | Patrimonial | Compreensivo Empresarial | Sim |
| 0167 | Patrimonial | Riscos de Engenharia | Não |
| 0171 | Patrimonial | Riscos Diversos | Não |
| 0173 | Patrimonial | Global de Bancos | Não |
| 0176 | Patrimonial | Riscos Diversos — Planos Conjugados | Não |
| 0196 | Patrimonial | Riscos Nomeados e Operacionais | Não |
| 0621 | Carga | Transporte Nacional | Sim |
| 0622 | Carga | Transporte Internacional | Sim |
| 0627 | Carga | Responsabilidade Civil do Transportador Intermodal (run-off) | Não |
| 0632 | Carga | RCTR-VI-C | Não |
| 0638 | Carga | RCTF-C | Não |
| 0652 | Carga | RCTA-C | Não |
| 0654 | Carga | RCTR-C | Não |
| 0655 | Carga | Responsabilidade Civil por Desaparecimento de Carga (RC-DC) | Sim |
| 0656 | Carga | RCA-C | Não |
| 0658 | Carga | RCOTM-C | Não |

#### 4.3. Auditoria das variáveis contábeis e série híbrida

As variáveis sinistro_direto, sinistro_retido e sinistro_ocorrido possuem significados distintos. Sinistro direto é o valor bruto reconhecido nas operações contratadas diretamente com os segurados. Sinistro retido é a parcela que permanece sob responsabilidade da seguradora após cessões e resseguro. Sinistro ocorrido é a medida contábil do custo atribuível ao período, com os ajustes próprios do regime de registro.

A comparação mensal, com atenção especial a 2012–2014, identificou mudança de preenchimento em dezembro de 2013, e não uma quebra anual entre 2013 e 2014. De janeiro de 2010 a novembro de 2013, sinistro_direto e sinistro_retido têm registros, enquanto sinistro_ocorrido permanece zerado. Em dezembro de 2013, as duas primeiras variáveis passam a zero e sinistro_ocorrido começa a ser preenchido, permanecendo como a medida disponível desde então.

Para o período anterior à mudança, escolheu-se sinistro_direto, e não sinistro_retido. A escolha preserva a medida bruta das perdas nas operações diretas e apresentou maior continuidade empírica com sinistro_ocorrido na transição entre regimes. A variável final foi definida no nível mensal como:

$$
\text{Sinistro híbrido}_m=\begin{cases}\text{sinistro direto}_m,&\text{se damesano}\leq 201311,\\\text{sinistro ocorrido}_m,&\text{se damesano}\geq 201312.\end{cases}
$$

As perdas anuais correspondem à soma mensal do sinistro híbrido nos ramos de cada categoria e cenário. Lançamentos negativos foram preservados, pois podem representar estornos, recuperações, salvados ou outros ajustes contábeis e integram o fluxo líquido registrado pela Susep. Depois da aplicação da regra, não foram encontrados valores ausentes na variável híbrida.

### 5. Perdas automotivas

#### 5.1. Série nacional observada e revisão de 2010–2012

A quantidade nacional $Q_{t}$ corresponde ao total anual de veículos roubados ou furtados. Os valores de 2013–2025 foram tratados como observados e extraídos das edições revisadas do Anuário Brasileiro de Segurança Pública. Para 2025, o 20º Anuário registra 104.491 roubos e 203.949 furtos, totalizando 308.440 ocorrências; a edição também revisa 2024 para 345.503.

Os números anteriormente disponíveis para 2010–2012 não foram considerados totais nacionais comparáveis. O valor de 2010, 382.694, resultava da duplicação do total de janeiro a junho, 191.347. Os valores de 2011, 237.546, e de 2012, 233.159, cobriam apenas janeiro a novembro. Como anualização mecânica e totais parciais não equivalem a uma observação anual, os três anos foram substituídos pela mesma regra de imputação aplicada a 1996–2009.

#### 5.2. Modelo de imputação da quantidade, 1996–2012

Definiu-se $D_{t}$ como a soma anual de roubos e furtos de veículos em São Paulo e no Rio de Janeiro. Na janela nacional observada de 2013–2025, estimou-se um modelo logarítmico com elasticidade fixada em um:

$$
\ln(Q_t)=\alpha+\ln(D_t)+\varepsilon_t\quad\Longleftrightarrow\quad\widehat{Q}_t=\exp(\widehat{\alpha})\times D_t.
$$

A calibração com 13 observações produziu $\widehat{\alpha}$ = 0,7435755 e exp($\widehat{\alpha}$) = 2,103443. Portanto, a estimativa central para cada ano ausente é 2,103443 vezes a soma SP+RJ. Por exemplo, em 2010, $D_{t}$ = 169.382 + 38.804 = 208.186, o que resulta em $\widehat{Q}_{2010}$ = 437.907 veículos após arredondamento.

A transformação logarítmica garante previsões positivas e faz a calibração operar em erros relativos. O modelo pressupõe que a participação conjunta de São Paulo e Rio de Janeiro no total brasileiro permaneça suficientemente estável fora da janela observada. Essa hipótese é a principal condição da retroprojeção e exige que os resultados de 1996–2012 sejam identificados como estimativas, nunca como registros observados.

A incerteza estatística foi registrada por um intervalo de predição de 95%. Com desvio-padrão residual de 0,083515 em log e 12 graus de liberdade, os limites equivalem a 0,827925 e 1,207839 vezes a estimativa central. O intervalo é condicional à estabilidade da relação SP+RJ/Brasil e não incorpora erros de mensuração das estatísticas policiais.

#### 5.3. Comparação de modelos e critérios de seleção

A especificação selecionada foi comparada com uma regressão logarítmica com elasticidade livre e controle pela frota nacional. O modelo alternativo produziu $\widehat{\beta}$ = 0,925168 e erro percentual absoluto médio de 9,69% no teste de retrodição; o multiplicador constante obteve 9,56%. Na validação leave-one-out do modelo principal, o erro percentual absoluto médio foi 7,02%. A especificação com $\beta$ = 1 foi mantida por combinar erro ligeiramente menor, interpretação direta e maior parcimônia.

Imputação múltipla não foi executada porque somente São Paulo e Rio de Janeiro forneceram séries públicas contínuas e comparáveis desde 1996 no conceito necessário. Adicionar unidades da Federação apenas nos anos mais recentes criaria mudança de composição. Uma especificação baseada em homicídios e frota foi rejeitada para o resultado central porque homicídio mede fenômeno criminal diferente. A frota nacional foi preservada apenas no modelo alternativo e como controle.

**Quadro 5 — Diagnósticos do modelo de quantidade**

| **Diagnóstico** | **Resultado** |
| --- | --- |
| Janela de calibração | 2013–2025; 13 observações |
| Multiplicador selecionado | 2,103443 × (SP+RJ) |
| MAPE — retrodição | 9,56% |
| MAPE — leave-one-out | 7,02% |
| MAPE — modelo alternativo | 9,69% |
| Fatores do intervalo de 95% | 0,827925 e 1,207839 |

#### 5.4. Construção do valor médio de referência

O preço de referência $V_{t}$ é nominal e representa um valor médio segurado, não o preço de um modelo específico. Para 2010–2019, o valor anual foi calculado a partir dos dois semestres do AutoSeg. O preço semestral foi ponderado pela frequência de sinistros de roubo e furto registrada em FREQ_SIN1:

$$
V_t=\frac{\sum_h V_{t,h}\times \mathrm{FREQ\_SIN1}_{t,h}}{\sum_h \mathrm{FREQ\_SIN1}_{t,h}},\quad\text{em que }h\text{ identifica o semestre}.
$$

Para 2020, foi adotado o preço do primeiro semestre, R$ 41.636,61. O segundo semestre foi excluído porque FREQ_SIN1 aumentou de 40.430 para 280.908 na base bruta sem variação compatível da exposição ou das indenizações, caracterizando ruptura não explicada do ponderador.

Para 2021–2025, manteve-se fixa a composição observada em 2020A: 96,0206% para automóveis, caminhões e demais veículos e 3,9794% para motocicletas. Cada parcela foi atualizada pelos subitens nacionais Automóvel usado e Motocicleta do IPCA, Tabela 7060 do SIDRA. Se $F^{a}_{t}$ e $F^{m}_{t}$ são os fatores acumulados de cada subitem em relação a 2020A, o fator composto é:

$$
F_t=0{,}960206\times F_t^a+0{,}039794\times F_t^m;\qquad V_t=\text{R\$ }41{.}636{,}61\times F_t.
$$

Em 2025, $F_{t}$ = 1,148827 e $V_{2025}$ = R$ 47.833,28. Assim foi preenchido o preço de referência que faltava na versão anterior da série. A atualização capta a evolução dos preços, mas mantém fixa a composição dos veículos roubados ou furtados de 2020A.

Para 1996–2009, a série final mantém o preço real de 2010, R$ 69.822,22 a preços de dezembro de 2025, e o reconverte para valores nominais de cada ano pelo deflator do projeto. Embora o AutoSeg permita calcular valores para 2008–2009, esses cálculos não entram na série final; todo o bloco 1996–2009 segue a mesma regra de retroprojeção de preço.

**Quadro 6 — Tratamento da quantidade e do preço de referência por período**

| **Período** | **Quantidade de veículos** | **Preço de referência** |
| --- | --- | --- |
| 1996–2009 | Imputada pelo modelo SP+RJ | Imputado: preço real de 2010 constante |
| 2010–2012 | Imputada pelo modelo SP+RJ | Observado no AutoSeg |
| 2013–2019 | Observada no FBSP | Observado no AutoSeg |
| 2020 | Observada no FBSP | AutoSeg 2020A; 2020B excluído |
| 2021–2025 | Observada no FBSP | Atualização determinística por IPCA específico |

#### 5.5. Taxa de recuperação e cálculo da perda

Adotou-se taxa uniforme de recuperação r = 36,5% para todo o período. O parâmetro substitui a hipótese anterior de 50% e se baseia em estimativa divulgada por especialistas associados ao Fórum Brasileiro de Segurança Pública, segundo a qual aproximadamente um em cada três veículos subtraídos é recuperado. A mesma fonte relaciona a queda histórica da recuperação ao desmonte ilegal para o mercado de autopeças.

Como não foi localizada uma série anual nacional de recuperação compatível com 1996–2025, o parâmetro foi mantido constante. Ele deve ser interpretado como hipótese externa, não como observação anual. A parcela não recuperada é 1 − 0,365 = 0,635, e a perda automotiva nominal foi calculada por:

$$
\text{Perda automotiva}_t=Q_t\times V_t\times(1-r)=Q_t\times V_t\times0{,}635.
$$

Em 2025, o cálculo reproduz 308.440 × R$ 47.833,28 × 0,635 = R$ 9.368.597.521, com o preço de referência arredondado a centavos. Como dezembro de 2025 é a base monetária, o valor nominal e o valor a preços de dezembro de 2025 coincidem nesse ano. A relação é linear: qualquer revisão futura da taxa de recuperação pode ser incorporada substituindo r na fórmula.

### 6. Consolidação, atualização monetária e status da série

#### 6.1. Fórmulas de consolidação

Para o cenário principal amplo, as perdas materiais anuais são a soma das três categorias:

$$
\text{Perdas materiais}_t=\text{Perda patrimonial}_t+\text{Perda de carga}_t+\text{Perda automotiva}_t.
$$

O total anual do eixo soma gastos preventivos e perdas, sem fundir seus conceitos:

$$
\begin{aligned}\text{Total do eixo}_t={}&\text{Seguros automotivos}_t+\text{Seguros patrimoniais}_t+\text{Seguros de carga}_t\\&+\text{Perdas patrimoniais}_t+\text{Perdas de carga}_t+\text{Perdas automotivas}_t.\end{aligned}
$$

#### 6.2. Atualização monetária

Todos os componentes foram calculados primeiro em valores nominais. Em seguida, cada valor anual foi multiplicado pelo fator de correção por IPCA adotado no projeto, com dezembro de 2025 igual a um. A metodologia é equivalente ao encadeamento dos índices mensais descrito pela Calculadora do Cidadão do Banco Central:

$$
\text{Valor em dez./2025}_t=\text{Valor nominal}_t\times\text{Deflator IPCA}_{t\rightarrow\mathrm{dez./2025}}.
$$

A conversão foi realizada antes da soma dos componentes, garantindo que todos estejam expressos na mesma unidade monetária. Os subitens Automóvel usado e Motocicleta empregados para projetar o preço de referência em 2021–2025 não substituem o IPCA geral usado para converter o valor total da perda para reais de dezembro de 2025; são etapas distintas.

#### 6.3. Identificação dos anos imputados

Na tabela final resumida, valores em preto indicam anos sem imputação estatística de subeixos; valores em vermelho indicam que pelo menos um componente do total contém imputação. Sob essa regra, 1996–2012 são marcados em vermelho porque a quantidade nacional de veículos foi imputada; em 1996–2009, também foi imputado o preço de referência. Os anos 2013–2025 são marcados em preto porque a quantidade nacional é observada no FBSP e os demais componentes provêm das bases da Susep. A atualização determinística do preço por IPCA em 2021–2025 é documentada separadamente e não foi classificada como imputação estatística.

A rastreabilidade exige que uma revisão da série nacional do FBSP leve à recalibração conjunta do multiplicador e dos intervalos, e não apenas à substituição de um ano isolado. Da mesma forma, um novo doador só pode ser incorporado se sua série completa desde 1996 for reconstruída e todo o exercício de validação for repetido com composição fixa.

### 7. Controles de qualidade, robustez e limitações

Os principais controles foram: leitura e decisão ramo a ramo; dois cenários de abrangência; auditoria mensal da mudança de regime de sinistros; verificação dos 12 meses de cada agregado anual; preservação de ajustes negativos; harmonização documentada dos códigos antigos; exclusão dos sinistros automotivos da Susep; comparação entre modelos de imputação; validação por retrodição e leave-one-out; registro de intervalos de predição; e separação entre valores observados, transformações determinísticas e imputações.

Persistem quatro limitações centrais. Primeiro, coberturas multirriscos não permitem isolar integralmente a parcela criminal dos prêmios e sinistros. Segundo, sinistros contábeis podem incorporar estornos, salvados e recuperações e não equivalem a uma mensuração física de todos os danos. Terceiro, a retroprojeção automotiva depende da estabilidade histórica da relação SP+RJ/Brasil. Quarto, o preço de referência e a taxa fixa de recuperação não captam mudanças anuais na composição dos veículos subtraídos nem na eficiência de recuperação.

O cenário conservador, os modelos alternativos e os intervalos de predição não foram somados à estimativa principal; eles foram mantidos como instrumentos de diagnóstico. O cenário amplo continua sendo o resultado oficial do eixo, porque a exclusão de modalidades com componente criminal relevante poderia produzir subestimação mais severa do que a incerteza gerada pelas coberturas multirriscos.

Em relação ao estudo metodológico anterior, a atualização amplia o período para 1996–2025, torna explícita a seleção ramo a ramo, substitui uma série histórica nacional não reproduzível por imputação auditável com doadores públicos, trata 2010–2012 como anos incompletos, identifica a mudança mensal de preenchimento da Susep, constrói uma série de preços até 2025 e reduz a hipótese de recuperação de 50% para 36,5%.

### 8. Fontes e referências

1. Superintendência de Seguros Privados. Sistema de Estatísticas da Susep — SES. [Acesso à fonte](https://www2.susep.gov.br/menuestatistica/ses/principal.aspx). Bases Ses_seguros.csv e Ses_ramos.csv; prêmios, sinistros, códigos e nomes dos ramos.

2. Superintendência de Seguros Privados. Circular Susep nº 395/2009. [Acesso à fonte](https://www2.susep.gov.br/safe/scripts/bnweb/bnmapi.exe?router=upload%2F8548). Nomenclatura e estrutura dos códigos de ramos; apoio à harmonização histórica.

3. Superintendência de Seguros Privados. Seguro Compreensivo. [Acesso à fonte](https://www.gov.br/susep/pt-br/copy_of_planos-e-produtos/seguros/seguro-compreensivo). Definições temáticas usadas na classificação de coberturas patrimoniais multirriscos.

4. Superintendência de Seguros Privados. Seguro Residencial. [Acesso à fonte](https://www.gov.br/susep/pt-br/assuntos/meu-futuro-seguro/seguros-previdencia-e-capitalizacao/seguros/seguro-residencial). Apoio à classificação do ramo compreensivo residencial.

5. Superintendência de Seguros Privados. Seguro de Transportes. [Acesso à fonte](https://www.gov.br/susep/pt-br/copy_of_planos-e-produtos/seguros/seguro-de-transportes). Apoio à classificação dos ramos de transporte e responsabilidade civil de carga.

6. Superintendência de Seguros Privados. Sistema AutoSeg. [Acesso à fonte](https://www2.susep.gov.br/menuestatistica/autoseg/principal.aspx). Importância segurada média e frequência de sinistros para a série de preços de referência.

7. Superintendência de Seguros Privados. Definições do Sistema AutoSeg. [Acesso à fonte](https://www2.susep.gov.br/menuestatistica/autoseg/DEFINICOES_AUTOSEG.pdf). Definições de importância segurada média, exposição, frequência e indenização.

8. Fórum Brasileiro de Segurança Pública. Arquivo do Anuário Brasileiro de Segurança Pública. [Acesso à fonte](https://forumseguranca.org.br/publicacoes/anuario-brasileiro-de-seguranca-publica/). Série nacional observada e revisões de roubos e furtos de veículos.

9. Fórum Brasileiro de Segurança Pública. 20º Anuário Brasileiro de Segurança Pública — 2026. [Acesso à fonte](https://forumseguranca.org.br/wp-content/uploads/2026/07/anuario-2026.pdf). Valores nacionais observados de 2024–2025; 308.440 ocorrências em 2025.

10. Secretaria da Segurança Pública do Estado de São Paulo. Dados mensais. [Acesso à fonte](https://www.ssp.sp.gov.br/estatistica/dados-mensais). Série doadora de roubos e furtos de veículos de São Paulo.

11. Instituto de Segurança Pública do Rio de Janeiro. Estatísticas de Segurança Pública. [Acesso à fonte](https://www.ispdados.rj.gov.br/estatistica.html). Série mensal estadual desde 1991; doadora para a imputação.

12. Instituto de Pesquisa Econômica Aplicada. IpeaData/Denatran — frota nacional de veículos. [Acesso à fonte](http://www.ipeadata.gov.br/api/odata4/Metadados('AETT_RODVEICAUT')/Valores). Controle de exposição e modelo alternativo, não selecionado.

13. Instituto Brasileiro de Geografia e Estatística. SIDRA, Tabela 7060 — IPCA. [Acesso à fonte](https://sidra.ibge.gov.br/tabela/7060). Subitens nacionais Automóvel usado e Motocicleta para 2021–2025.

14. Instituto Brasileiro de Geografia e Estatística. Índice Nacional de Preços ao Consumidor Amplo — IPCA. [Acesso à fonte](https://www.ibge.gov.br/estatisticas/economicas/precos-e-custos/9256-indice-nacional-de-precos-ao-consumidor-amplo.html). Índice geral de atualização monetária.

15. Banco Central do Brasil. Calculadora do Cidadão — correção de valores. [Acesso à fonte](https://www3.bcb.gov.br/CALCIDADAO/publico/exibirFormCorrecaoValores.do?method=exibirFormCorrecaoValores). Metodologia de acumulação de índices mensais.

16. O Globo. Queda no percentual de carros recuperados pode indicar desmanche de veículos. [Acesso à fonte](https://oglobo.globo.com/rio/noticia/2024/05/17/queda-no-percentual-de-carros-recuperados-pode-indicar-que-veiculos-roubados-estao-sendo-desmanchados-diz-especialista.ghtml). Fonte secundária da estimativa de recuperação de 36,5%, atribuída a especialistas associados ao FBSP.

17. Honaker, J.; King, G. What to Do about Missing Values in Time-Series Cross-Section Data. [Acesso à fonte](https://doi.org/10.1111/j.1540-5907.2010.00447.x). Referência metodológica sobre dependência temporal, informação auxiliar e incerteza em imputações.

18. InfoMoney. Roubos e furtos de carros crescem no segundo trimestre. [Acesso à fonte](https://www.infomoney.com.br/minhas-financas/roubos-e-furtos-de-carros-crescem-10-no-segundo-trimestre/). Validação auxiliar do total parcial de janeiro a junho de 2010; não usado como total anual.

19. Portal do Trânsito. Veículos mais roubados em 2012. [Acesso à fonte](https://www.portaldotransito.com.br/noticias/as-sete-motos-e-os-sete-carros-mais-roubados-em-2012/). Validação auxiliar dos totais parciais de janeiro a novembro de 2011–2012.

20. Fórum Brasileiro de Segurança Pública. 10º Anuário Brasileiro de Segurança Pública — 2016. [Acesso à fonte](https://www.minaspelapaz.org.br/wp-content/uploads/2016/11/10_Anu%C3%A1rio-Brasileiro-de-Seguran%C3%A7a-P%C3%BAblica.pdf). Verificação de revisão histórica do total nacional de 2014.

21. Secretaria Especial de Assuntos Estratégicos. Custos Econômicos da Criminalidade no Brasil. [Acesso à fonte](https://www.gov.br/secretariageral/pt-br/noticias/2018/setembro/sae-apresenta-estudo-sobre-criminalidade-em-forum-nacional-de-juizes). Estudo metodológico anterior usado como referência comparativa; dados não reproduzíveis não foram transcritos.

22. Superintendência de Seguros Privados. Seguro de Automóveis. [Acesso à fonte](https://www.gov.br/susep/pt-br/assuntos/meu-futuro-seguro/seguros-previdencia-e-capitalizacao/seguros/seguro-de-automoveis). Coberturas automotivas combinadas e distinção entre roubo/furto, colisão, incêndio, assistência e responsabilidade civil.

23. Superintendência de Seguros Privados. Seguro de Responsabilidade Civil. [Acesso à fonte](https://www.gov.br/susep/pt-br/assuntos/meu-futuro-seguro/seguros-previdencia-e-capitalizacao/seguros/seguro-responsabilidade-civil). Apoio à avaliação e à exclusão de ramos sem parcela criminal material separável.

24. Superintendência de Seguros Privados. Seguro Rural. [Acesso à fonte](https://www.gov.br/susep/pt-br/copy_of_planos-e-produtos/seguros/seguro-rural). Apoio à exclusão de ramos rurais com vínculo criminal apenas incidental.

25. Superintendência de Seguros Privados. Seguro Garantia. [Acesso à fonte](https://www.gov.br/susep/pt-br/copy_of_planos-e-produtos/seguros/seguro-garantia-2/seguro-garantia). Apoio à exclusão de garantias e obrigações financeiras fora do conceito material.

26. Superintendência de Seguros Privados. Seguro de Vida e Acidentes Pessoais. [Acesso à fonte](https://www.gov.br/susep/pt-br/assuntos/meu-futuro-seguro/seguros-previdencia-e-capitalizacao/seguros/seguro-de-vida-e-acidentes-pessoais). Apoio à exclusão de seguros de pessoas do eixo patrimonial.

27. Superintendência de Seguros Privados. Seguro de Garantia Estendida. [Acesso à fonte](https://www.gov.br/susep/pt-br/assuntos/meu-futuro-seguro/seguros-previdencia-e-capitalizacao/seguros/seguro-de-garantia-estendida). Apoio à exclusão de cobertura de defeitos e funcionamento sem relação direta com criminalidade.

28. Superintendência de Seguros Privados. Seguro Habitacional. [Acesso à fonte](https://www.gov.br/susep/pt-br/assuntos/meu-futuro-seguro/seguros-previdencia-e-capitalizacao/seguros/seguro-habitacional). Apoio à distinção entre cobertura habitacional e perda material criminal.

29. Superintendência de Seguros Privados. Seguro Carta Verde. [Acesso à fonte](https://www.gov.br/susep/pt-br/assuntos/meu-futuro-seguro/seguros-previdencia-e-capitalizacao/seguros/seguro-carta-verde). Apoio à exclusão de responsabilidade civil internacional de veículos.

30. Agência Nacional de Transportes Terrestres. Seguros obrigatórios para transportadores de cargas. [Acesso à fonte](https://www.gov.br/antt/pt-br/assuntos/ultimas-noticias/antt-reforca-exigencia-de-seguros-obrigatorios-para-transportadores-de-cargas-e-garante-mais-seguranca-nas-estradas). Fonte temática complementar para o enquadramento dos ramos de responsabilidade civil de carga.

## Gastos com perdas produtivas

### 1. Objetivo e delimitação da estimação

As perdas produtivas decorrentes de homicídios representam o valor presente da renda do trabalho que as vítimas poderiam gerar ao longo do restante da vida produtiva caso não tivessem morrido prematuramente. A medida não atribui valor monetário à vida, ao sofrimento ou às consequências sociais da violência; ela se restringe à produção econômica futura que deixa de ser realizada em razão da redução permanente da força de trabalho.

O eixo abrange exclusivamente mortes identificadas como homicídios no Sistema de Informações sobre Mortalidade (SIM/DATASUS). Não são incluídas perdas temporárias associadas a internações, afastamentos ou incapacidade, nem trabalho doméstico não remunerado, custos intangíveis ou despesas contabilizadas nos demais eixos do estudo. A série nacional cobre 1996–2025, com aplicação do mesmo procedimento de cálculo em todos os anos.

> **Nota sobre 2025.** Na ausência de microdados regionais completos do SIM para 2025, a estimativa nacional utiliza o total agregado de homicídios de 2025 e a distribuição por idade e grande região observada em 2024, último perfil completo disponível.

### 2. Fontes de dados e cobertura

#### 2.1. PNAD Contínua: rendimentos e ocupação

As trajetórias de rendimento e de ocupação foram estimadas com os microdados anuais da primeira visita da Pesquisa Nacional por Amostra de Domicílios Contínua (PNAD Contínua) de 2025. Foram preservados os pesos amostrais e o desenho complexo da pesquisa, de modo que médias, proporções e totais reproduzissem a estrutura de inferência definida pelo Instituto Brasileiro de Geografia e Estatística (IBGE).

A idade foi obtida pela variável V2009, a condição de ocupação pela variável derivada VD4002 e o rendimento mensal habitual do trabalho principal pela variável VD4019. A correção monetária do rendimento foi realizada com o deflator CO2.

#### 2.2. SIM/DATASUS: homicídios

As mortes foram obtidas nos registros individuais do Sistema de Informações sobre Mortalidade. Para 1996–2000, foram utilizados os arquivos de óbitos por causas externas disponibilizados na modalidade SIM-DOEXT; de 2001 em diante, foram utilizados os arquivos SIM-DO. A seleção dos casos, a construção do ano, a decodificação da idade e a região de residência foram realizadas de forma uniforme, preservadas as diferenças de organização dos arquivos entre os períodos.

#### 2.3. Tábua de mortalidade

As probabilidades de sobrevivência foram construídas a partir da Tábua Completa de Mortalidade do IBGE de 2024, que informa o número de sobreviventes em cada idade exata. A mesma tábua nacional foi aplicada a todas as regiões; portanto, a diferenciação regional do modelo decorre do mercado de trabalho, e não de hipóteses regionais de mortalidade.

### 3. Construção da renda esperada do trabalho

#### 3.1. Rendimento médio e probabilidade de ocupação

Para cada idade i e grande região r, estimou-se primeiro o rendimento mensal médio entre pessoas ocupadas com rendimento válido:

$$
w(i,r)=\mathbb{E}\!\left[Y(i,r)\mid\mathrm{ocupado}\right]
$$

Em seguida, calculou-se a probabilidade de ocupação na população da mesma idade e região. A variável VD4002 identifica diretamente a condição de ocupação; pessoas não ocupadas, inclusive as que estavam fora da força de trabalho, receberam indicador igual a zero para essa etapa:

$$
\gamma(i,r)=\Pr\!\left[\mathrm{ocupado}(i,r)=1\right]
$$

A renda mensal esperada do trabalho corresponde ao produto entre o rendimento condicional dos ocupados e a probabilidade de ocupação:

$$
RE(i,r)=w(i,r)\times\gamma(i,r)
$$

Essa decomposição evita atribuir a todas as vítimas um salário integral. Em vez disso, pondera o rendimento dos ocupados pela probabilidade de uma pessoa da mesma idade e região estar ocupada.

#### 3.2. Grupos etários, regiões e base monetária

As estimativas foram construídas separadamente para Norte, Nordeste, Sudeste, Sul e Centro-Oeste. A regionalização é uma etapa intermediária do cálculo: ela permite que o valor presente reflita diferenças de rendimento e ocupação.

As idades de 14 a 69 anos foram tratadas individualmente. Para reduzir a instabilidade decorrente de células amostrais pequenas em idades avançadas, as pessoas com 70 anos ou mais formaram um único grupo na PNAD Contínua. A renda esperada desse grupo foi aplicada às idades futuras de 70 a 90 anos.

### 4. Identificação e preparação dos homicídios

#### 4.1. Critério de seleção pela causa básica

O critério principal de identificação utiliza a causa básica do óbito registrada em CAUSABAS. Após padronização do código, foram selecionadas as categorias da CID-10 X85–X99, Y00–Y09, Y35 e Y36.

O ano foi extraído da data do óbito. A região corresponde à região da unidade da Federação do município de residência informado em CODMUNRES. Os registros foram então agregados por ano, idade e região, mantendo contagens separadas para os casos sem idade utilizável.

#### 4.2. Decodificação da idade

O campo IDADE do SIM combina unidade e quantidade. Os códigos com unidade 0, 1, 2 ou 3 representam, respectivamente, minutos, horas, dias ou meses e foram convertidos para idade zero em anos; a unidade 4 informa anos completos; e a unidade 5 representa idades de 100 anos ou mais. Os códigos completos 000 e 999 foram tratados como idade não registrada.

Essa distinção é necessária porque códigos válidos de idade em minutos também começam pelo algarismo 0. Assim, um registro como 010 representa dez minutos e pertence à idade zero, enquanto 000 permanece classificado como idade ignorada. Nenhum caso foi descartado apenas por ausência de idade.

### 5. Valor presente da perda por homicídio

#### 5.1. Probabilidade de sobrevivência

Para uma vítima de idade i e uma idade futura j, a probabilidade condicional de sobrevivência foi calculada por:

$$
S(i,j)=\frac{l(j)}{l(i)}
$$

em que l(i) e l(j) são os sobreviventes nas idades i e j na tábua do IBGE. Esse componente reduz cada fluxo futuro pela probabilidade de a pessoa alcançar a idade correspondente na ausência do homicídio.

#### 5.2. Horizonte, crescimento e desconto

O fluxo produtivo começa na primeira idade futura após o óbito, respeitada a idade mínima de 14 anos, e termina aos 90 anos. Para uma vítima de idade i na região r, o valor presente é:

$$
VP(i,r)=\sum_{j=\max(i+1,14)}^{90}12\times RE(j,r)\times\frac{l(j)}{l(i)}\times\frac{(1+g)^{j-i}}{(1+d)^{j-i}}
$$

O fator 12 converte a renda mensal em anual. Adotaram-se taxa anual de crescimento da produtividade g = 2% e taxa anual de desconto d = 3%. Esses valores correspondem aos parâmetros centrais do estudo de referência.

#### 5.3. Regras de fronteira etária

Para vítimas com menos de 14 anos, não se atribui renda antes da idade mínima de entrada no fluxo produtivo; o primeiro rendimento potencial ocorre aos 14 anos e é descontado pelo número de anos transcorridos desde a idade da vítima. Para idades futuras entre 70 e 90 anos, utiliza-se a renda esperada do grupo 70+ da região correspondente. Aos 90 anos não existe fluxo posterior, e vítimas com idade superior a 90 anos recebem valor presente igual a zero.

### 6. Tratamento dos registros sem idade

Os homicídios sem idade utilizável foram preservados. Como a região de residência estava informada para esses casos, a imputação foi realizada no nível ano × região, sem recorrer a médias nacionais ou a valores de outros períodos.

Para cada ano t e região r, calculou-se a perda observada entre vítimas com idade conhecida:

$$
\text{Perda observada}(t,r)=\sum_i H(i,t,r)\times VP(i,r)
$$

Em seguida, obteve-se o valor presente médio dos homicídios com idade conhecida na mesma célula:

$$
\text{VP médio observado}(t,r)=\frac{\text{Perda observada}(t,r)}{\text{Homicídios com idade conhecida}(t,r)}
$$

A perda imputada foi definida como:

$$
\text{Perda imputada}(t,r)=\text{Homicídios sem idade}(t,r)\times\text{VP médio observado}(t,r)
$$

Por fim:

$$
\text{Perda total}(t,r)=\text{Perda observada}(t,r)+\text{Perda imputada}(t,r)
$$

Essa regra atribui aos registros sem idade a composição etária média das vítimas com informação completa no mesmo ano e região. Desse modo, todos os homicídios identificados pelo critério da causa básica permanecem no cálculo.

### 7. Agregação nacional e validações

O resultado foi obtido pela soma das perdas totais das cinco grandes regiões em cada ano:

$$
\text{Perda produtiva Brasil}(t)=\sum_r\text{Perda total}(t,r)
$$

As regiões funcionam apenas como estratos intermediários para a associação entre idade, renda esperada e homicídios.

O processamento incluiu testes automáticos de fechamento. Foram conferidos: a decomposição dos homicídios entre idade conhecida e idade não registrada; a correspondência entre a soma das células ano × região e o total anual do SIM; a equivalência entre a soma regional e o resultado nacional; a cobertura das idades de referência; a inexistência de valores presentes ausentes, infinitos ou negativos; e a incorporação integral da parcela imputada. Para 1996–2000, os totais anuais e os casos sem idade também foram comparados com controles previamente consolidados.

O campo CIRCOBITO foi mantido como verificação auxiliar da seleção por CAUSABAS. Diferenças entre os dois campos não alteram a amostra, pois a causa básica, com as categorias da CID-10 explicitadas acima, é o critério operacional do estudo.

### 8. Interpretação e limitações

O resultado deve ser interpretado como perda de renda do trabalho esperada, e não como valoração completa da vida ou do bem-estar. Não são mensurados trabalho não remunerado, produção doméstica, efeitos sobre familiares e comunidades, dor e sofrimento, nem custos médicos, policiais, judiciais, prisionais ou patrimoniais.

A estimativa utiliza perfis médios de ocupação e rendimento observados em 2025 e pressupõe que eles representem a trajetória econômica contrafactual das vítimas, ajustada apenas pelo crescimento real de 2% ao ano. Características individuais como escolaridade, sexo, raça ou ocupação não são incorporadas. A tábua de sobrevivência é nacional e não captura diferenças regionais de mortalidade. O agrupamento 70+ estabiliza a estimação, mas reduz a variação de renda nas idades avançadas.

Como em qualquer exercício de valor presente, os resultados são sensíveis ao horizonte produtivo, à taxa de crescimento e à taxa de desconto. Além disso, dependem da qualidade do preenchimento da causa básica, da idade e do município de residência no SIM e da precisão amostral da PNAD Contínua. As regras de validação e imputação reduzem perdas de informação e tornam essas escolhas auditáveis, mas não eliminam tais fontes de incerteza.

### 10. Fontes e referências

[IBGE — Pesquisa Nacional por Amostra de Domicílios Contínua](https://www.ibge.gov.br/estatisticas/sociais/trabalho/17270-pnad-continua.html)

[IBGE — Microdados e documentação da PNAD Contínua anual](https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Anual/Microdados/Visita/Visita_1/Documentacao/)

[IBGE — Tábuas Completas de Mortalidade](https://www.ibge.gov.br/estatisticas/sociais/populacao/9126-tabuas-completas-de-mortalidade.html)

[Ministério da Saúde/DATASUS — Informações de Saúde (TABNET)](https://datasus.saude.gov.br/informacoes-de-saude-tabnet/)

[Ministério da Saúde/DATASUS — Transferência de Arquivos](https://datasus.saude.gov.br/transferencia-de-arquivos/)

## Gastos com processos judiciais

### 1. Objetivo e delimitação da estimação

O eixo de gastos com processos judiciais estima, para 1996–2025, os recursos associados ao processamento de matéria criminal na Justiça Estadual brasileira. O resultado principal reúne três componentes: a parcela criminal das despesas dos Tribunais de Justiça (TJs); a parcela criminal das despesas dos Ministérios Públicos estaduais e do Ministério Público do Distrito Federal e Territórios (MPDFT); e o valor de referência dos serviços de defesa em processos criminais de primeiro grau e dos Juizados Especiais Criminais (JECRIM).

O recorte é nacional e estadual. Não integram o cenário principal a Justiça Federal, o Ministério Público Federal, os tribunais superiores nem a defesa em processos federais. O orçamento das Defensorias Públicas também não é somado separadamente, pois o componente de defesa valora o serviço jurídico demandado pelos processos, independentemente de ele ter sido prestado por advocacia particular, advocacia dativa ou Defensoria Pública. Essa decisão evita potencial dupla contagem.

### 2. Fontes de dados e cobertura temporal

#### 2.1. Tribunais de Justiça

As despesas totais da Justiça Estadual foram obtidas no Justiça em Números, do Conselho Nacional de Justiça (CNJ). Para 2003, utilizou-se a soma das 27 unidades apresentadas na primeira edição do relatório. Para 2004–2008, foram empregados os totais nacionais da série histórica revisada, publicados a preços de dezembro de 2008. Para 2009–2025, utilizaram-se os registros dos 27 TJs preservados na base do projeto; a observação nacional agregada identificada como “TJ” foi excluída para impedir dupla contagem.

A distribuição das despesas entre matéria criminal e não criminal utiliza as quantidades de sentenças criminais (sentcrim) e não criminais (sentncrim) e os respectivos tempos médios de tramitação. Os tempos foram obtidos por 54 consultas ao painel do CNJ — 27 para a classe criminal e 27 para a não criminal — e mantidos fixos por UF ao longo da série, enquanto a composição das sentenças varia por ano.

#### 2.2. Ministérios Públicos

As âncoras históricas são as despesas executadas informadas pelo Conselho Nacional do Ministério Público (CNMP) para 2007 e 2008. A partir de 2009, foram preservados todos os valores oficialmente observados na base consolidada do projeto e imputadas apenas as células UF–ano ausentes. O Ministério Público Federal foi excluído; no Distrito Federal, a unidade considerada é o MPDFT.

A participação criminal foi calculada com os registros de Atuação Funcional do CNMP. Nos questionários de 2011–2017, classificaram-se como criminais os grupos “Inquérito Policial e Auto de Prisão”, “Termos Circunstanciados”, “Processo Criminal” e “Execução Penal”. Os demais grupos foram classificados como não criminais. Para evitar múltipla contagem de indicadores referentes à mesma atividade, utilizou-se somente a medida agregada Estatística/Quantidade de cada questionário.

#### 2.3. Serviços de defesa

Para 2009–2025, as quantidades de processos foram extraídas do Sistema de Estatísticas do Poder Judiciário do CNJ. O cenário principal utiliza casos novos de conhecimento no primeiro grau criminal (cnccrim1) e casos novos de conhecimento nos Juizados Especiais Criminais (cnccrimje). Registros “nd” foram tratados como ausentes, e a linha agregada “TJ” foi excluída.

Os preços de referência provêm das tabelas de honorários das seccionais da Ordem dos Advogados do Brasil (OAB) disponíveis no encerramento da coleta. Para processos comuns, selecionou-se a defesa integral no procedimento criminal comum ou ordinário, da denúncia ou acusação até a sentença. Para o JECRIM, selecionou-se a defesa integral no procedimento sumaríssimo ou perante o Juizado Especial Criminal até a sentença. Consultas, pareceres, acompanhamento policial, atos isolados, cautelares, recursos, execução penal, revisão criminal e atuação em instâncias superiores foram excluídos do cenário principal. Quando a defesa integral aparecia dividida em componentes complementares, os valores foram somados.

### 3. Gastos criminais dos Tribunais de Justiça

#### 3.1. Distribuição das despesas em 2009–2025

Para cada UF e ano, a participação criminal foi definida pela razão entre as sentenças criminais ponderadas pelo tempo médio criminal e o total de sentenças ponderadas pelos respectivos tempos:

$$
P_{\mathrm{crim}}^{TJ}(u,t)=\frac{\mathrm{SentCrim}(u,t)\times\mathrm{TempoCrim}(u)}{\mathrm{SentCrim}(u,t)\times\mathrm{TempoCrim}(u)+\mathrm{SentNCrim}(u,t)\times\mathrm{TempoNCrim}(u)}.
$$

A participação não criminal é o complemento dessa medida. A despesa total atualizada de cada tribunal foi então distribuída da seguinte forma:

$$
G_{\mathrm{crim}}^{TJ}(u,t)=DPJ_{\mathrm{real}}(u,t)\times P_{\mathrm{crim}}^{TJ}(u,t).
$$

$$
G_{\mathrm{não\_crim}}^{TJ}(u,t)=DPJ_{\mathrm{real}}(u,t)\times\left[1-P_{\mathrm{crim}}^{TJ}(u,t)\right].
$$

A soma das duas parcelas reproduz a despesa total do tribunal. Apenas a parcela criminal integra o custo da criminalidade; a parcela não criminal foi preservada como variável auxiliar e controle de consistência.

#### 3.2. Reconstrução de 1996–2008

Há despesas oficiais para 2003–2008. O valor de 2003 foi atualizado a partir de reais nominais daquele ano. Os valores de 2004–2008 já estavam expressos a preços de dezembro de 2008 e, por isso, receberam um único fator de conversão de dezembro de 2008 para dezembro de 2025, sem nova deflação ano a ano.

Para 1996–2002, a despesa real foi retroprojetada por uma regressão log-linear da despesa real per capita, estimada sobre os seis anos oficiais de 2003–2008:

$$
\ln\!\left(\frac{DPJ_{\mathrm{real}}(t)}{\mathrm{Pop}(t)}\right)=\alpha+\beta t+\varepsilon(t),
$$

em que t é o ano-calendário, $\alpha$ = −107,1190267 e $\beta$ = 0,0561072. A despesa imputada foi obtida pela exponenciação do valor previsto e sua multiplicação pela população do respectivo ano. O erro percentual absoluto médio dentro da amostra de calibração foi de 1,56%.

Como as sentenças por classe passaram a estar disponíveis a partir de 2009, aplicou-se a 1996–2008 uma participação criminal nacional fixa de 12,4057%. Essa proporção corresponde à média ponderada pela despesa no período 2009–2013, calculada pela razão entre a soma dos gastos criminais dos TJs e a soma das despesas totais reais no mesmo período. A escolha de uma razão agregada, em vez da média simples das UFs, preserva o peso relativo dos tribunais de maior porte.

### 4. Gastos criminais dos Ministérios Públicos

#### 4.1. Participação criminal

A classificação da atuação funcional resultou em participação criminal de 68,72%:

$$
P_{\mathrm{crim}}^{MP}=\frac{\text{Volume criminal}}{\text{Volume criminal}+\text{Volume não criminal}}=0{,}6872.
$$

Essa proporção foi aplicada à despesa real de cada unidade:

$$
G_{\mathrm{crim}}^{MP}(u,t)=\mathrm{Despesa}_{\mathrm{real}}^{MP}(u,t)\times0{,}6872.
$$

O percentual de 68,72% é o parâmetro definitivo utilizado nos resultados finais; percentuais registrados em versões anteriores do texto foram substituídos por este valor.

#### 4.2. Despesas oficiais e imputações residuais

Para 2007, utilizou-se a despesa executada nacional publicada pelo CNMP. Em 2008, o total foi recomposto a partir das 27 unidades após incorporar a correção textual do valor de São Paulo indicada no próprio relatório: o valor impresso na tabela como R$ 1.208.281 foi interpretado, conforme a nota explicativa do documento, como R$ 1.208.281.000. O total corrigido de 2008 é R$ 6.347.139.586 em valores nominais.

Para 1996–2006, anos sem série nacional padronizada equivalente, a despesa real dos MPs foi imputada pela relação média entre despesa real dos MPs e despesa real dos TJs observada nas âncoras corrigidas de 2007 e 2008:

$$
\mathrm{Despesa}_{\mathrm{real}}^{MP}(t)=DPJ_{\mathrm{real}}(t)\times0{,}3036929.
$$

Para 2009–2025, a reconstrução foi realizada no nível UF–ano, preservando integralmente cada valor oficial. Para as unidades com observação em 2008 e uma primeira observação oficial posterior, as lacunas intermediárias foram preenchidas por interpolação log-linear entre as duas âncoras:

$$
\ln MP(u,t)=\ln MP(u,a)+\frac{t-a}{b-a}\left[\ln MP(u,b)-\ln MP(u,a)\right],
$$

em que a e b são, respectivamente, os anos-âncora à esquerda e à direita. Para AP, MT, PI e SE, que não possuíam âncora posterior válida, a despesa foi projetada pela evolução da despesa real do TJ da mesma UF:

$$
MP(u,t)=MP(u,2008)\times\frac{DPJ_{\mathrm{real}}(u,t)}{DPJ_{\mathrm{real}}(u,2008)}.
$$

Depois da imputação, as 27 unidades foram somadas e a participação criminal de 68,72% foi aplicada. Essa estratégia substitui a imputação anterior por um valor uniforme entre UFs, que não preservava a forte heterogeneidade de porte dos MPs. Como controle, nenhum valor oficial foi alterado, e a variação do gasto criminal nacional entre 2008 e 2009 passou a ser de 2,27%, eliminando a quebra artificial observada na série anterior.

### 5. Gastos com serviços de defesa

#### 5.1. Quantidades e fórmula de cálculo em 2009–2025

Cada caso novo criminal foi tratado como uma unidade de serviço de defesa completa. Os componentes foram calculados separadamente:

$$
G_{\mathrm{defesa\_comum}}(u,t)=CnCCrim1(u,t)\times H_{\mathrm{comum}}(u).
$$

$$
G_{\mathrm{defesa\_JECRIM}}(u,t)=CnCCrimJE(u,t)\times H_{\mathrm{JECRIM}}(u).
$$

$$
G_{\mathrm{defesa}}(u,t)=G_{\mathrm{defesa\_comum}}(u,t)+G_{\mathrm{defesa\_JECRIM}}(u,t).
$$

O uso de casos novos, e não de processos baixados, é a especificação principal incorporada à tabela final. Processos baixados foram mantidos somente como teste de sensibilidade.

#### 5.2. Harmonização dos honorários da OAB

Foi construída uma base com um honorário para processo comum e outro para JECRIM em cada UF. Obtiveram-se valores observados para 24 UFs no procedimento comum e para 15 UFs no JECRIM; neste último grupo, um valor foi derivado da soma de componentes complementares. As referências correspondem às tabelas mais recentes localizadas até o encerramento da coleta, inclusive tabelas publicadas em 2026. Por funcionarem como preços normativos de referência, foram aplicadas a toda a série. Valores de tabelas anteriores foram atualizados para dezembro de 2025; referências de 2026 foram mantidas pelo valor nominal registrado na base como aproximação mais próxima disponível.

Nas UFs sem item comparável, imputou-se, separadamente por tipo de processo, a média nacional dos valores válidos observados, já harmonizados na mesma base monetária:

$$
H_{\mathrm{médio\_comum}}=\text{R\$ }14{.}150{,}49.
$$

$$
H_{\mathrm{médio\_JECRIM}}=\text{R\$ }6{.}212{,}02.
$$

Como parâmetros de sensibilidade, foram calculadas as medianas de R$ 12.116,77 e R$ 5.493,61, respectivamente. O cenário principal utiliza as médias. A imputação por tipo evita transferir diretamente ao JECRIM o preço de procedimentos comuns, cujas descrições e exigências de atuação são distintas.

#### 5.3. Reconstrução de 1996–2008

Para 2003–2008, o CNJ fornece casos novos totais no primeiro grau (Cn1) e nos Juizados Especiais (CnJE), mas não separa a matéria criminal. Em 2003, a observação ausente do Rio Grande do Norte foi estimada a partir do valor de 2004 e da variação nacional 2003–2004 calculada sem essa UF. Para 1996–2002, Cn1 e CnJE foram retroprojetados separadamente por modelos log-lineares per capita estimados em 2003–2008. Os erros percentuais absolutos médios na amostra de calibração foram de 4,29% para Cn1 e 3,21% para CnJE.

Os totais históricos foram convertidos em volumes criminais com as participações nacionais observadas em 2009–2013:

$$
CnCCrim1(t)=Cn1(t)\times0{,}1243312.
$$

$$
CnCCrimJE(t)=CnJE(t)\times0{,}2289453.
$$

Para manter a composição estadual dos preços de referência, foram utilizados honorários efetivos nacionais ponderados pelos volumes de casos em 2009–2013: R$ 14.802,28 para processos comuns e R$ 6.749,46 para JECRIM. Assim, o custo histórico foi obtido separadamente para os dois tipos de procedimento e depois somado.

### 6. Agregação nacional e atualização monetária

O resultado anual do eixo é a soma dos três componentes:

$$
G_{\mathrm{justiça\_criminal}}(t)=G_{\mathrm{crim}}^{TJ}(t)+G_{\mathrm{crim}}^{MP}(t)+G_{\mathrm{defesa}}(t).
$$

Para 2009–2025, os totais nacionais resultam da soma das 27 unidades da Federação depois do cálculo de cada componente por UF. Para 1996–2008, as séries históricas nacionais foram construídas a partir das fontes e dos modelos descritos acima. Em nenhum caso se somaram linhas nacionais agregadas às 27 unidades.

As despesas institucionais nominais foram convertidas para reais de dezembro de 2025 pelos fatores de atualização monetária adotados no projeto, baseados no IPCA e preservados na planilha consolidada. No componente de defesa, os honorários já foram harmonizados nessa referência antes da multiplicação pelos volumes processuais; portanto, não houve uma segunda atualização do custo derivado. A soma anual dos três componentes reproduz exatamente a série “Gastos com Justiça” utilizada na tabela final do custo econômico da criminalidade no Brasil.

### 7. Validação e análises de sensibilidade

Foram aplicados quatro controles principais. Primeiro, nos TJs, a soma das parcelas criminal e não criminal reproduz a despesa total. Segundo, nos MPs, todas as células oficiais mantêm diferença zero em relação à base de origem; apenas as ausentes foram imputadas. Terceiro, os modelos históricos foram avaliados dentro das janelas de calibração por erro percentual absoluto médio. Quarto, os totais anuais dos três componentes foram reconciliados com a tabela final nacional.

As especificações alternativas — peso criminal dos TJs em janela mais longa, medianas de honorários e processos baixados na defesa — foram preservadas como análises de sensibilidade, mas não integram o cenário principal apresentado ao público.

### 8. Limitações metodológicas

A repartição das despesas dos TJs pressupõe que sentenças ponderadas pelo tempo de tramitação representem adequadamente a utilização de recursos. A participação criminal histórica de 1996–2008 é fixa e transfere para o passado a composição observada em 2009–2013. Além disso, as mudanças contábeis e de cobertura do Justiça em Números recomendam cautela na comparação direta entre os períodos anterior e posterior a 2009.

Nos MPs, a proporção de 68,72% é uma aproximação baseada na composição da atuação funcional, e não na alocação direta de horas de trabalho ou de rubricas orçamentárias. Parte das despesas foi imputada, especialmente nos primeiros anos da série, embora os valores oficiais existentes tenham sido preservados.

Na defesa, as tabelas da OAB representam honorários mínimos normativos e não necessariamente preços efetivamente pagos. A comparabilidade das descrições varia entre seccionais, e algumas referências publicadas em 2026 foram utilizadas como preços mais recentes disponíveis. Um processo pode envolver mais de uma pessoa acusada, substituição de representantes ou níveis de esforço distintos, dimensões que a unidade “caso novo” não capta integralmente.

Por fim, o eixo mede a Justiça Estadual. A exclusão da Justiça Federal, do Ministério Público Federal, dos tribunais superiores e da defesa federal deve ser considerada na interpretação do total nacional.

### 10. Fontes e referências

[Conselho Nacional de Justiça (CNJ). Justiça em Números 2003.](https://bibliotecadigital.cnj.jus.br/xmlui/bitstream/handle/123456789/169/Justi%C3%A7a%20em%20N%C3%BAmeros%202003.pdf?isAllowed=y&sequence=1)

[Conselho Nacional de Justiça (CNJ). Justiça em Números 2008 — Justiça Estadual, série 2004–2008.](https://bibliotecadigital.cnj.jus.br/jspui/bitstream/123456789/161/4/Justi%C3%A7a%20em%20n%C3%BAmeros%202008_Justi%C3%A7a%20Estadual.pdf)

[Conselho Nacional de Justiça (CNJ). Painel Justiça em Números e Sistema de Estatísticas do Poder Judiciário.](https://justica-em-numeros.cnj.jus.br/painel-estatisticas/)

[Conselho Nacional do Ministério Público (CNMP). Análise dos dados administrativos e orçamentários do Ministério Público — ano-base 2008.](https://www.cnmp.mp.br/portal/images/stories/Normas/relatoriosanuais/analisedosdadosadministrativoseoorcamentariosdompem2008.pdf)

[Conselho Nacional do Ministério Público (CNMP). Painéis estatísticos de Atuação Funcional.](https://www.cnmp.mp.br/portal/institucional/comissoes/comissao-de-planejamento-estrategico/indicadores-de-gestao-e-atuacao-funcional-do-ministerio-publico-brasileiro/ministerio-publico-um-retrato)

[Ordem dos Advogados do Brasil (OAB). Diário Eletrônico e tabelas de honorários das seccionais estaduais.](https://diario.oab.org.br/)

[Instituto Brasileiro de Geografia e Estatística (IBGE). Estimativas de população.](https://www.ibge.gov.br/estatisticas/sociais/populacao/9103-estimativas-de-populacao.html)

[Banco Central do Brasil. Calculadora do Cidadão — correção de valores por índice de preços.](https://www3.bcb.gov.br/CALCIDADAO/publico/corrigirPorIndice.do?method=corrigirPorIndice)

## Gastos hospitalares

### 1. Objetivo e delimitação da estimação

O eixo de gastos hospitalares estima, para 1996–2025, os custos associados às internações por agressão registradas no Sistema de Informações Hospitalares do Sistema Único de Saúde (SIH/SUS). O resultado principal reúne duas parcelas: o valor pago pelo SUS pelas internações selecionadas e a perda produtiva temporária correspondente aos dias de permanência hospitalar das pessoas que não morreram durante a internação.

O cenário incorporado à tabela final utiliza exclusivamente registros do SIH/SUS. Não são acrescentados atendimentos ambulatoriais, consultas, pronto-atendimentos sem internação, acompanhamento posterior à alta ou perdas produtivas além do período registrado em DIAS_PERM. A especificação deve, portanto, ser interpretada como uma estimativa conservadora, ou limite inferior, dos custos médicos da violência.

A perda de renda de longo prazo decorrente de homicídios integra o eixo de perdas produtivas e não é repetida aqui. No presente eixo, a parcela produtiva restringe-se às internações não fatais e ao tempo em que a pessoa permaneceu hospitalizada, evitando sobreposição entre os dois componentes do estudo.

### 2. Fontes de dados e cobertura temporal

#### 2.1. SIH-RD/SUS

A fonte principal são os microdados mensais do SIH-RD/SUS, obtidos no repositório do DATASUS com o pacote microdatasus no R. Para 1998–2007, os arquivos históricos foram processados por unidade da Federação e mês; para 2008–2025, foram baixados os arquivos mensais com cobertura de todas as UFs. Os registros foram posteriormente agregados ao nível nacional.

A unidade de observação é a Autorização de Internação Hospitalar (AIH), isto é, uma internação registrada, e não uma pessoa única. Uma mesma pessoa pode gerar mais de uma AIH ao longo do tempo. As variáveis centrais foram os campos de diagnóstico disponíveis em cada arquivo, VAL_TOT, DIAS_PERM, MORTE, IDADE e, nos arquivos históricos em que necessário, COD_IDADE. O código UF_ZI foi utilizado para associar cada registro a uma grande região na etapa de vinculação da renda.

#### 2.2. PNAD Contínua e renda esperada

A renda usada na perda produtiva temporária provém da mesma tabela de renda mensal esperada por idade e grande região construída para o eixo de perdas produtivas. Essa tabela foi estimada com os microdados anuais da primeira visita da PNAD Contínua de 2025, preservando os pesos e o desenho amostral da pesquisa.

Para cada idade e região, a renda esperada combina o rendimento mensal habitual do trabalho principal entre os ocupados, informado por VD4019, com a probabilidade de ocupação obtida por VD4002. Os rendimentos foram harmonizados com o deflator CO2 e expressos em reais de 2025. A construção completa dessa medida é apresentada no apêndice do eixo de perdas produtivas.

#### 2.3. Indicadores monetários

Os valores de VAL_TOT estão registrados em moeda corrente do período da internação. Para torná-los comparáveis ao restante do estudo, foram aplicados os fatores anuais de atualização monetária baseados no IPCA e preservados na planilha consolidada do projeto, convertendo os gastos para reais de dezembro de 2025. A renda esperada da PNAD Contínua já se encontrava nessa referência monetária.

### 3. Identificação das internações associadas à violência

A partir de 1998, uma AIH foi classificada como associada à violência quando ao menos um dos campos de diagnóstico disponíveis continha código da CID-10 nos intervalos X85–X99 ou Y00–Y09, ou os códigos W34 ou Y24. A busca foi realizada em todas as colunas de diagnóstico existentes em cada arquivo, e não apenas no diagnóstico principal.

Antes da aplicação do filtro, os códigos foram padronizados pela remoção de espaços e pontuação e pela conversão para letras maiúsculas. Cada AIH selecionada foi contabilizada uma única vez, mesmo quando mais de um campo apresentava código elegível. Os indicadores resultantes correspondem, portanto, a internações registradas, e não à contagem de diagnósticos.

A variável MORTE foi padronizada para distinguir internações não fatais, com valor 0, e mortes ocorridas durante a internação, com valor 1. Registros selecionados com informação de mortalidade ausente permanecem no cálculo do gasto hospitalar, mas não entram na perda produtiva temporária, que exige identificação explícita de desfecho não fatal.

### 4. Custo hospitalar direto

O custo hospitalar direto de cada ano corresponde à soma de VAL_TOT em todas as AIHs selecionadas. Essa variável informa o valor total registrado e pago pelo SUS na internação. Depois da agregação dos valores nominais, aplicou-se o fator de atualização monetária do respectivo ano:

$$
C_{\mathrm{SUS}}(t)=\sum_{i\in A(t)}VAL_{\mathrm{TOT}}(i)\times F_{\mathrm{IPCA}}(t).
$$

Nessa expressão, A(t) representa o conjunto de internações selecionadas no ano t e F_IPCA(t) é o fator que converte os valores monetários do ano para reais de dezembro de 2025.

### 5. Perda produtiva temporária durante a internação

#### 5.1. Vinculação da renda por idade e região

A perda produtiva foi calculada apenas para as AIHs não fatais. A idade foi convertida para anos completos quando a codificação histórica exigia essa transformação. Em seguida, a renda esperada foi associada pela combinação entre idade ajustada e grande região derivada de UF_ZI.

As idades de 15 a 69 anos foram mantidas individualmente. Para compatibilizar os registros com a tabela de renda, internações de pessoas com 14 anos ou menos receberam o valor de referência da idade 14, e internações de pessoas com 70 anos ou mais receberam o valor do grupo 70+. A tabela de renda foi previamente validada para conter uma única observação em cada combinação de idade e região.

#### 5.2. Cálculo individual e agregação

A renda mensal esperada foi convertida em renda diária. Para cada internação não fatal com idade, região, renda e dias válidos, a perda individual corresponde ao produto entre a renda diária e DIAS_PERM:

$$
PP_{\mathrm{temp}}(i)=\frac{RE(a(i),r(i))}{30}\times DIAS_{\mathrm{PERM}}(i).
$$

RE(a(i), r(i)) é a renda mensal esperada da idade ajustada a(i) e da região r(i). A perda produtiva temporária anual resulta da soma das perdas individuais das internações não fatais:

$$
PP_{\mathrm{temp}}(t)=\sum_{i\in A_{\mathrm{nf}}(t)}PP_{\mathrm{temp}}(i).
$$

O cálculo não projeta afastamento depois da alta nem incapacidade permanente. Também não atribui perda temporária às mortes hospitalares, cujas consequências produtivas de longo prazo são tratadas no eixo específico de perdas produtivas.

### 6. Tratamento das lacunas e imputações

#### 6.1. Anos de 1996 e 1997

O pacote utilizado para acessar os arquivos do DATASUS não disponibiliza dados utilizáveis do SIH-RD para 1996 e 1997. Para estimar esses dois anos, foram utilizados os números absolutos referentes a 1998, o ano mais próximo possível. Assim, 1996 e 1997 devem ser interpretados como anos imputados a partir da primeira observação disponível, e não como medidas produzidas diretamente dos microdados do respectivo exercício.

#### 6.2. Partições UF–mês ausentes em 1998–2007

O inventário do repositório histórico identificou sete arquivos UF–mês ausentes no intervalo efetivamente observado de 1998–2007: Roraima em dezembro de 1999 e de janeiro a maio de 2000, além do Amapá em outubro de 2007. Essas ausências foram tratadas separadamente em cada UF e indicador por interpolação linear entre os meses observados mais próximos. Quando a lacuna se encontrava na borda da série, utilizou-se o mês observado mais próximo. Contagens de internações, óbitos e totais de dias imputados foram arredondadas.

#### 6.3. Setembro de 2009

Na série de 2008–2025, o arquivo correspondente a setembro de 2009 não estava disponível no processamento final. Os indicadores desse mês foram imputados pela média aritmética dos valores observados nos demais meses de setembro da série. A linha imputada foi incorporada antes da agregação anual, preservando a cobertura de doze meses em 2009.

### 7. Agregação nacional e atualização monetária

Os indicadores foram primeiro calculados no nível mensal e, quando aplicável, por UF. A estimativa nacional anual corresponde à soma de todas as partições mensais depois dos tratamentos descritos. O gasto hospitalar nominal foi convertido para reais de dezembro de 2025; a perda produtiva temporária, já calculada com rendimentos nessa base, não recebeu nova atualização.

O resultado anual do eixo é definido por:

$$
G_{\mathrm{hospitalar}}(t)=C_{\mathrm{SUS}}(t)+PP_{\mathrm{temp}}(t).
$$

Essa soma reproduz a série de gastos hospitalares incorporada à tabela final nacional. A participação no PIB foi calculada posteriormente pela divisão do gasto total do eixo pelo PIB brasileiro do mesmo ano, também expresso em reais de dezembro de 2025.

### 8. Validação e controles de consistência

O processamento incluiu controles de cobertura e fechamento. Foram verificadas a existência das variáveis obrigatórias; a disponibilidade de renda para todas as combinações de idade e região; a preservação do número de AIHs após a vinculação da renda; o número esperado de partições UF–mês; a identificação explícita dos arquivos ausentes; e a inexistência de valores faltantes nas partições depois da imputação.

Também foram conferidas a decomposição entre internações não fatais, mortes hospitalares e mortalidade ignorada; a soma dos dias e dos valores de VAL_TOT; a equivalência entre as agregações mensais e anuais; e a identidade entre o gasto total e a soma de suas duas parcelas. Para 1998–2007, os filtros foram testados para assegurar uma seleção uniforme pela CID-10. Na série posterior, janeiro de 2024 foi utilizado como mês de validação detalhada, com inspeção da distribuição dos códigos, do número de internações, dos valores pagos, dos dias de permanência e das mortes hospitalares.

### 9. Interpretação e limitações

O eixo mede o custo registrado de internações financiadas pelo SUS e uma aproximação da renda perdida durante a permanência hospitalar. Ele não representa o custo integral da atenção à saúde decorrente da violência. Casos tratados sem internação, atendimentos na rede privada, gastos ambulatoriais, medicamentos e reabilitação após a alta não são observados.

VAL_TOT corresponde ao valor registrado no SIH/SUS, não necessariamente ao custo econômico completo de todos os recursos mobilizados pelo estabelecimento. Além disso, a AIH não identifica pessoas únicas e pode haver múltiplas internações para um mesmo indivíduo. A classificação depende da qualidade e da abrangência do preenchimento dos campos de diagnóstico.

A perda produtiva utiliza perfis médios de renda e ocupação de 2025 por idade e grande região, e não o rendimento efetivo de cada pessoa internada. A divisão da renda mensal por 30 e a equivalência entre dias de internação e dias sem produção são aproximações. A medida exclui afastamento depois da alta e incapacidade duradoura, o que reforça seu caráter conservador.

Por fim, os valores de 1996 e 1997 dependem da imputação baseada em 1998; as partições históricas ausentes e setembro de 2009 também foram preenchidos por regras explícitas. Essas decisões preservam a continuidade da série, mas reduzem a capacidade de interpretar variações pontuais nos anos afetados como mudanças efetivamente observadas.

### 10. Fontes e referências

[Ministério da Saúde/DATASUS — Informações de Saúde e Sistema de Informações Hospitalares do SUS](https://datasus.saude.gov.br/informacoes-de-saude-tabnet/).

[Ministério da Saúde/DATASUS — Transferência de Arquivos](https://datasus.saude.gov.br/transferencia-de-arquivos/).

[IBGE — Pesquisa Nacional por Amostra de Domicílios Contínua](https://www.ibge.gov.br/estatisticas/sociais/trabalho/17270-pnad-continua.html).

[IBGE — Microdados e documentação da PNAD Contínua anual](https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Anual/Microdados/Visita/Visita_1/Documentacao/).

[Banco Central do Brasil — Calculadora do Cidadão: correção de valores por índice de preços](https://www3.bcb.gov.br/CALCIDADAO/publico/corrigirPorIndice.do?method=corrigirPorIndice).

[Pacote R microdatasus — documentação e código-fonte](https://rfsaldanha.github.io/microdatasus/).
