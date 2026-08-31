# Status do projeto

**Atualizado:** 2026-08-31

## Situação atual

A primeira auditoria empírica e metodológica das duas planilhas finais foi concluída. Em seguida, as planilhas foram revisadas pelo autor para corrigir os erros identificados. O relatório de 2018 continua sendo usado apenas para conceitos e mudanças metodológicas materiais.

Na verificação da versão mais recente, o validador executou 3.247 verificações: 3.244 passaram, não restam erros mecânicos e 16 advertências exigem interpretação ou metadados. As diferenças agregadas dos MPs e das perdas produtivas UF de 2025 são não bloqueantes por decisões MD-014 e MD-015.

As Figuras 6–15 foram produzidas em PDF e PNG a partir de CSVs auditáveis em
`data/figure_data/`. As figuras nacionais usam 1996–2025. As figuras de UF usam 2025 como
`ANO_FINAL_UF` operacional porque as 27 UFs têm cobertura completa nas variáveis requeridas;
permanecem explicitamente preliminares devido à revisão pendente das perdas produtivas estaduais
e à diferença conceitual do encarceramento. A Figura 15 compara 2016 a 2025 em níveis.

As Figuras 3 e 4 e a pipeline SIM–IBGE que as sustenta também foram concluídas. `ANO_FINAL_SIM = 2024`: o OpenDataSUS identifica 2024 como final e 2025 como prévio. A pipeline retém microdados finais de 2015–2017 e 2022–2024, populações municipais oficiais do IBGE e a malha fixa de 558 microrregiões de 2015. Os pontos principais usam 2016 e 2024; 2023 é interpolado somente no denominador do diagnóstico suavizado.

O diagnóstico adicional de convergência microrregional foi incorporado ao relatório como Figura 5.
No scatterplot da taxa de 2016 contra a variação absoluta até 2024, a inclinação linear
ponderada pela população de 2016 é −0,50, a correlação ponderada é −0,69 e 70,3% das 558
microrregiões registram queda. Com médias trienais nos extremos, a inclinação permanece negativa
(−0,41). O padrão é compatível com convergência beta descritiva, mas não tem interpretação causal e
pode incorporar reversão à média.

As Figuras 1 e 2A–2D foram concluídas a partir de insumos oficiais retidos. O Sinesp sustenta
2016–2025 com 27 UFs e 12 meses para seis indicadores de vítimas. Quatro indicadores
patrimoniais de cobertura parcial aparecem separadamente em painéis balanceados específicos:
22 UFs para furto e roubo de veículo e 20 UFs para roubo de carga e a instituição financeira,
com cobertura entre 85,3% e 87,8% da população em 2025. A Figura 1 compara as taxas do UNODC em
2016 e 2024 numa amostra fixa de 87 unidades de reporte país/território observadas nas duas datas.
Com isso, todas as Figuras 1–15 estão produzidas; 2C e 2D são companheiras adicionais.

`docs/report.md` contém agora a primeira versão completa das Seções 1–6. A Conclusão foi redigida
antes da Introdução e do Sumário Executivo, conforme a sequência editorial do projeto. As Seções
3–5 receberam apenas ajustes dirigidos de transição, terminologia e conexão explícita com as figuras.
O relatório incorpora os 18 placeholders de Figuras 1–15, incluindo 2A–2D, e está pronto para
revisão substantiva do autor, mas não para publicação: os resultados estaduais e metadados listados
abaixo ainda precisam ser fechados.

O apêndice metodológico foi convertido de `docs/appendix.docx` para `docs/appendix.md` por uma
rotina reprodutível e estrita. A versão Markdown preserva sete blocos de componentes, 15 tabelas,
57 equações em TeX e 80 hiperlinks; a nota editorial sobre a utilização do perfil SIM de 2024 na
estimativa nacional de 2025 foi incorporada ao texto.

Uma cópia combinada de revisão foi compilada em `docs/report.pdf` por meio de
`python -B -m src.report.build_report`. O compilador processa os 18 marcadores de figura, as sete
notas Markdown e todo o apêndice, retém o TeX e os logs em `build/report/` e produziu um PDF A4 de
87 páginas. A versão Word correspondente foi gerada em `docs/report.docx`, com 18 figuras, 57
fórmulas compostas e notas de rodapé nativas incorporadas; sua exportação diagnóstica tem 89
páginas A4. Foram inspecionadas visualmente a capa, prosa, notas, tabelas e equações nos dois
formatos. O código Word reduz automaticamente imagens que excedam a área útil da página, e a
prévia final confirmou que os gráficos e mapas não sofrem corte lateral.

A autoria e a identificação editorial foram incorporadas às duas edições:
Carlos Góes, Lucas Siqueira Simões, Giulia Spiess e Bruna Santos; publicação do
Inter-American Dialogue — Brazil Program. O manuscrito completo foi traduzido para
`docs/report-en.md`; as 18 figuras e seus CSVs receberam versões paralelas em inglês,
e foram gerados `docs/report-en.pdf` (42 páginas) e `docs/report-en.docx` (30 páginas
na prévia do Word). A edição inglesa é uma publicação autônoma do relatório; o apêndice
metodológico completo, com 57 equações e 15 tabelas, permanece incorporado à edição
portuguesa e não foi inserido em português no arquivo inglês.

O hotsite bilíngue está montado em `site/`, com português como idioma padrão,
alternância para inglês, 18 visualizações Plotly, downloads dos 36 CSVs paralelos e
dos seis arquivos de relatório e mapa interativo das 558 microrregiões na geografia
fixa de 2015. A geometria web foi simplificada apenas para visualização; os valores
analíticos permanecem nos CSVs. A inspeção headless carregou todos os insumos locais,
confirmou a troca de idioma e não encontrou gráficos em estado de erro. O fluxo
`.github/workflows/pages.yml` publica o diretório estático no GitHub Pages em pushes
para `main`.

O ambiente Python local foi fixado em `.venv` (não versionada) a partir de
`requirements.txt`: Matplotlib 3.11.1 e PyShp 2.3.1, além das dependências transitivas.
As rotinas finais de figuras, validação, relatório e site foram executadas com esse
interpretador.

## Trabalho concluído

- Inventário das oito abas nacionais e onze abas de UF.
- Identificação da unidade observacional, chave, cobertura, variáveis, unidades, fórmulas, deflatores, denominadores conhecidos e status de imputação/modelagem.
- Verificação de chaves únicas, tipos numéricos, anos esperados e 27 UFs em 2016 e 2025.
- Mapeamento variável–conceito–fonte–fórmula no `DATA-DICTIONARY.md`.
- Comparação conceitual com o relatório de 2018, sem reconciliação artificial dos pontos históricos.
- Testes de identidades contábeis, participações no PIB, pesos, PIB per capita e reconciliações Brasil–UF conceitualmente apropriadas.
- Implementação de `python -m src.validation.validate_data`, sem dependências externas, e geração de `data/audit/workbook_validation.json`.
- Implementação dos dez entry points em `src/figures/`, de um construtor conjunto e de validação específica para as Figuras 6–15.
- Exportação de dez CSVs publication-facing, dez PDFs, dez PNGs e um manifesto com hashes das saídas.
- Inspeção visual das dez PNGs. As séries anuais nacionais usam barras, imprimem todos os anos com rótulos a 90 graus e denominam o terceiro painel `Percentual do total`.
- Auditoria visual de figuras selecionadas do relatório de 2018 e do notebook histórico fixado por commit. O sistema atualizado preserva fundo branco, hierarquia tipográfica, legenda superior, grade horizontal e nota de fonte, com paleta acessível.
- Auditoria da definição de homicídio no apêndice, relatório original e scripts legados; adoção de `CAUSABAS` X85–X99, Y00–Y09, Y35 e Y36, todas as idades, por residência.
- Implementação das três aquisições versionadas em `src/data/`, com fontes brutas retidas e manifesto de checksums, e da consolidação município–ano e microrregião–ano.
- Construção de crosswalk estável com 5.570 municípios, 558 microrregiões e 27 UFs; reconciliação integral dos códigos com a malha IBGE 2015.
- Exportação e inspeção visual das Figuras 3–5 em PDF e PNG, com CSVs exatos de plotagem e validação específica.
- Retenção de onze arquivos anuais Sinesp (2015–2025), da projeção populacional UF do
  IBGE e do workbook/metadados de homicídio do UNODC, todos com checksums no manifesto.
- Auditoria UF–ano–crime do Sinesp sem conversão de faltantes em zero; construção dos
  painéis nacional completo e patrimonial balanceado, com arquivo de diagnóstico por UF.
- Construção da amostra internacional comum de 2016 e 2024 e percentis não ponderados;
  produção e inspeção visual das Figuras 1 e 2A–2D.
- Redação das Seções 1–6 e auditoria integral de números, referências de figuras, terminologia,
  conceitos econômicos e atribuições institucionais.
- Revisão ortográfica e de concordância do manuscrito; reescrita da Conclusão e reformulação do
  Sumário Executivo em tópicos quantitativos, seguindo a organização expositiva do relatório original.
- Renumeração integral das figuras: o diagnóstico de convergência passou a ser a Figura 5 e as antigas
  Figuras 5–14 passaram a 6–15; scripts, CSVs, saídas, especificações e referências textuais foram
  atualizados de forma consistente. Todos os títulos agora começam por `Figura X.`.
- Compilação reproduzível de `docs/report.md` em `docs/report.pdf`, com processamento de notas
  de rodapé, inclusão automática dos PDFs das figuras e incorporação do apêndice metodológico.
- Conversão reproduzível de `docs/appendix.docx` para `docs/appendix.md`, com validação estrita das
  57 equações em TeX, 15 tabelas, sete componentes e 80 hiperlinks.
- Geração de `docs/report.docx` com figuras e fórmulas incorporadas, notas de rodapé nativas e
  exportação diagnóstica em PDF para inspeção visual.
- Geração da edição inglesa completa do manuscrito principal, de 18 figuras/CSVs paralelos e dos
  arquivos finais `docs/report-en.pdf` e `docs/report-en.docx`.
- Construção e inspeção do hotsite bilíngue e interativo em `site/`, com downloads auditáveis e
  workflow oficial de implantação no GitHub Pages.

## Figuras locais e validação

| Figura | Período efetivo | Situação |
|---|---|---|
| 1 — Distribuição mundial dos homicídios | 2016 e 2024 | Concluída; 87 unidades país/território observadas nos dois anos e percentis não ponderados |
| 2A–2B — Tendências nacionais registradas | 2016–2025 | Concluídas; seis indicadores de vítimas, 27 UFs e 12 meses em todos os anos; barras rotuladas sem casas decimais nas contagens e com uma casa nas taxas |
| 2C–2D — Crimes patrimoniais de cobertura parcial | 2016–2025 | Concluídas; quatro indicadores de ocorrências, painel balanceado específico de 20 ou 22 UFs por indicador; barras rotuladas sem casas decimais nas contagens e com uma casa nas taxas |
| 3 — Distribuição microrregional dos homicídios | 2024 | Concluída; 558 microrregiões, percentil não ponderado e área das bolhas proporcional à população |
| 4 — Mudança microrregional dos homicídios | 2016–2024 | Concluída; variação absoluta, geografia fixa de 2015 e escala divergente centrada em zero |
| 5 — Convergência microrregional dos homicídios | 2016–2024 | Concluída; inclinação ponderada −0,50, correlação ponderada −0,69 e bolhas proporcionais à população de 2016 |
| 6 — Segurança pública | 1996–2025; percentuais por esfera em 2016–2025 | Concluída. Total exibido em todo o período; a decomposição é detectada dinamicamente e não é imputada |
| 7 — Segurança privada | 1996–2025 | Concluída |
| 8 — Encarceramento e auxílio-reclusão | 1996–2025 | Concluída; transferência identificada |
| 9 — Seguros e perdas materiais | 1996–2025 | Concluída; cenário contábil amplo e sobreposição sinalizados |
| 10 — Perda de capacidade produtiva | 1996–2025 | Concluída; medida modelada identificada visualmente |
| 11 — Custos judiciais | 1996–2025 | Concluída; alerta MP permanece no validador geral |
| 12 — Serviços médico-terapêuticos | 1996–2025 | Concluída |
| 13 — Total nacional | 1996–2025 | Concluída; sete componentes reproduzem o total dentro de R$ 2 e os percentuais somam 100% |
| 14 — Nível e componentes por UF | 2025 | Concluída como preliminar; 27 UFs e identidades por UF passam |
| 15 — Trajetórias por UF | 2016–2025 | Concluída como preliminar; cada UF aparece uma vez em cada ponta |

O validador de figuras executa 11 grupos de verificações: todos passaram, sem erros, com duas
advertências econômicas já documentadas (resultados estaduais preliminares e metadados de vintage
de PIB/população `PENDING`). O validador dos workbooks continua passando com 3.244 de 3.247
verificações, zero erros e 16 advertências.

O validador externo executou 326 verificações: todas passaram, sem erros e sem advertências.
Ele confere checksums e integridade dos arquivos brutos, unicidade UF–ano–crime e país–ano,
status explícito de não reporte, identidade de taxas, igualdade das amostras entre contagens e
taxas, regra internacional de cobertura e existência/integridade das cinco saídas PNG/PDF.

## Pipelines Sinesp e UNODC

As Figuras 2A–2B usam homicídio doloso, latrocínio, tentativa de homicídio, estupro, estupro
de vulnerável e feminicídio. Todos têm 27 UFs e 12 meses em 2016–2025. As duas séries de
estupro são mantidas separadas. Feminicídio requer cautela porque o crescimento também pode
refletir consolidação da classificação legal.

As Figuras 2C–2D usam furto de veículo, roubo de veículo, roubo de carga e roubo a
instituição financeira em painéis fixos específicos por indicador. Furto e roubo de veículo usam
22 UFs, excluindo AC, ES, GO, PR e RO, e cobrem 87,8% da população em 2025. Roubo de carga
usa 20 UFs, excluindo AC, ES, GO, MS, PR, RO e SE, e cobre 85,3%; roubo a instituição
financeira também usa 20 UFs, mas exclui AC, AP, ES, GO, MS, PR e RO e cobre 86,0%.
Entre 2016 e 2025, as variações das contagens nesses painéis são −25,5%, −60,0%, −62,8% e
−93,8%, respectivamente; nas taxas, −28,6%, −61,7%, −64,4% e −94,0%. A maior diferença
em relação ao antigo painel comum de 19 UFs é de apenas 0,7 p.p., de modo que a ampliação da
cobertura não altera a leitura substantiva. Tráfico de drogas e
armas apreendidas permanecem apenas nos diagnósticos porque refletem fiscalização e, no segundo
caso, quantidade de objetos.

O workbook UNODC de julho de 2026 fornece taxas até 2024. A cobertura anual cai de 105 unidades
em 2023 para 95 em 2024. Para a comparação solicitada, a interseção das observações de 2016 e
2024 retém 87 unidades de reporte. O Brasil passa de 30,1 homicídios por 100 mil e percentil 91,9
em 2016 para 18,7 e percentil 86,0 em 2024. Não houve interpolação, ponderação populacional nem
emenda com fonte nacional. Por usar anos isolados, a nova especificação é mais sensível a oscilações
transitórias do que a comparação anterior por médias decenais; essa escolha está registrada em MD-023.

O universo oficial `Country` inclui unidades territoriais com ISO-3, entre elas Bermuda, Hong Kong,
Macau e Porto Rico. Elas foram mantidas; registros explicitamente subnacionais com identificadores
compostos foram excluídos. Por isso, o denominador correto da Figura 1 é "unidades oficiais de
reporte país/território", e não uma lista estrita de Estados soberanos.

## Pipeline de homicídios e cobertura geográfica

Os totais produzidos diretamente dos microdados finais reconciliam com os agregados oficiais selecionados: 62.517 homicídios em 2016, 45.747 em 2023 e 42.590 em 2024. A conversão genérica `Mortalidade_Geral_2023_csv.zip`, que retornava 38.559, foi diagnosticada como incompleta para essa finalidade, preservada no manifesto como não utilizada e substituída na produção pelo recurso final `DO23OPEN.csv`.

| Ano | Homicídios no SIM | Alocados a microrregião | Taxa de correspondência | Sem município (`UF0000`) |
|---:|---:|---:|---:|---:|
| 2015 | 59.080 | 58.278 | 98,6425% | 802 |
| 2016 | 62.517 | 61.531 | 98,4228% | 986 |
| 2017 | 65.602 | 64.660 | 98,5641% | 942 |
| 2022 | 46.409 | 45.819 | 98,7287% | 590 |
| 2023 | 45.747 | 45.210 | 98,8262% | 537 |
| 2024 | 42.590 | 42.132 | 98,9246% | 458 |

Os casos não alocados têm UF conhecida, mas município de residência codificado como `UF0000`. Eles não foram rateados nem descartados silenciosamente: permanecem nos totais brutos do arquivo de auditoria e são excluídos apenas das taxas microrregionais. Não há código municipal válido sem correspondência, população municipal faltante, população não positiva, taxa não finita ou diferença de unidades geográficas entre 2016 e 2024.

A comparação solicitada de 2016 a 2024 apresenta queda da mediana microrregional de 23,0 para 18,1 homicídios por 100 mil habitantes; a variação mediana é −4,1. O diagnóstico que agrega os triênios 2015–2017 e 2022–2024 tem correlação de 0,889 com a mudança de anos isolados e preserva o sinal em 81,5% das microrregiões. A conclusão espacial ampla não muda, mas movimentos locais de áreas pequenas devem ser interpretados com cautela. A Figura 4 principal permanece nos anos isolados, conforme MD-020.

A escala de cor da Figura 4 é centrada em zero e limitada visualmente a ±45 homicídios por 100 mil, valor obtido arredondando para cima o percentil 98 da mudança absoluta. Onze microrregiões ultrapassam esse limite; seus valores verdadeiros não foram winsorizados e permanecem no CSV.

O validador específico de homicídios executou 132 verificações: 126 passaram, não há erros e há seis advertências, uma por ano, porque a correspondência municipal fica abaixo do limiar informativo de 99%. Todas superam o piso operacional documentado de 95%; os remanescentes são exclusivamente `UF0000` e estão quantificados acima. O validador também confere os dados e o coeficiente da Figura 5. O validador geral das planilhas também foi rerodado e permanece em 3.244 de 3.247 verificações, zero erros e 16 advertências já documentadas.

## Estrutura e cobertura validadas

| Bloco | Cobertura | Resultado estrutural |
|---|---|---|
| Nacional | Anual, 1996–2025, 30 observações por aba relevante | Chave `ano` única; sete componentes, PIB e participações completos no agregado |
| UFs | 2016 e 2025, 54 observações por aba relevante | Chave `(UF, ano)` única; 26 estados + DF presentes nos dois anos |
| Folhas auxiliares | `dados_aux_graficos` tem dois blocos e `graficos_finais_ufs` está vazia | Não são fontes econômicas primárias |

Passam a nova fórmula do total nacional, participações no PIB, seis parcelas de seguros, pesos de rateio, PIB per capita e identidades internas de perdas produtivas e saúde. A soma de PIB das UFs reconcilia com o PIB nacional; segurança pública, seguros/danos e saúde também reconciliam quando se respeita sua construção. O validador agora resolve a aba nacional por nomes de variáveis, sem depender da nova ordem das colunas.

## Correções verificadas e pendências de propagação

1. **Total nacional — corrigido.** A aba foi reorganizada e `SUM(B:H)` soma somente os sete componentes. A identidade passa.
2. **Encarceramento por UF — correção completa.** `gasto_anual_presos` aplica ×12 nas 54 linhas e os valores foram propagados para `custo_total_violencia_ufs` e `graficos_ufs`. Todas as identidades mecânicas passam. A diferença conceitual frente ao método nacional permanece como ressalva pré-publicação.
3. **Ministério Público — nota não bloqueante.** A soma UF excede o nacional em R$ 959,1 milhões (5,96%) em 2016 e R$ 1,465 bilhão (6,44%) em 2025. TJs e defesa reconciliam exatamente. Por MD-014, isso não impede avançar, mas exige nova conferência da fonte antes da publicação.
4. **Perdas produtivas 2025 — alerta não bloqueante.** A aba-fonte e a aba-resumo nacionais reproduzem 40.775 homicídios e R$ 29,17 bilhões, escalando o perfil de 2024. As UFs permanecem em 36.362 homicídios e R$ 25,31 bilhões, diferença de 4.413 homicídios e R$ 3,861 bilhões. Por MD-015, a pipeline pode avançar, mas os dados estaduais devem ser atualizados antes da publicação.
5. **AC–2025 — corrigido.** `homicidios_com_idade` foi corrigido de 191 para 181, restaurando a identidade `181 + 1 = 182`.

## Advertências e revisões plausíveis

- A perda produtiva nacional de 2025 usa o total agregado de 40.775 homicídios, mas reaproveita o perfil de perda de 2024 porque os microdados por idade/região ainda não estavam disponíveis.
- Dezesseis observações UF-ano de segurança pública têm alguma subfunção vazia; `SUM` trata o vazio como zero, mas sua semântica não está documentada.
- Quatro nomes estão truncados na aba de segurança pública por UF: Amazonas, Minas Gerais, Pernambuco e Santa Catarina.
- A soma das estimativas amostrais de segurança privada por UF difere do nacional em −0,0114% em 2016 e +0,1687% em 2025; é plausível porque Brasil e UFs são estimados separadamente na PNAD Contínua.
- A diferença de perdas produtivas em 2016 é R$ 8,2 milhões (0,0168%), com contagem idêntica de homicídios; foi classificada como revisão plausível de vintage/agregação.
- Movimentos anuais acima do filtro diagnóstico de 40% aparecem no encarceramento (2013 e 2017) e nos serviços médicos (2009). São advertências de revisão, não erros por si mesmos.
- As planilhas não codificam status observado/revisado/provisório/imputado de forma geral e legível por máquina.

## Disponibilidade real do ano terminal

| Série nacional | 2025 no arquivo | Avaliação de uso |
|---|---|---|
| Segurança pública | Sim | Utilizável; fonte FBSP |
| Segurança privada | Sim | Utilizável; PNAD Contínua |
| Encarceramento | Sim | Utilizável nacionalmente com nota de sete UFs imputadas (CE, MG, PA, PI, RJ, RS, SE) |
| Seguros e danos materiais | Sim | Utilizável como cenário contábil amplo, com componentes observados e construídos |
| Processos judiciais | Sim | Utilizável com nota sobre MP; reconciliação obrigatória antes da publicação |
| Serviços médicos | Sim | Utilizável, com escopo SIH e imputações históricas documentadas |
| Perdas produtivas | Estimativa parcial | Usa contagem agregada de 2025 e perfil de 2024; nacionalmente consistente, mas ainda precisa ser reconciliada com UFs |

Todas as abas relevantes por UF contêm 27 unidades em 2025. O total UF pode ser processado pela pipeline, mas ainda não deve ser tratado como resultado regional final porque as perdas produtivas estaduais serão atualizadas e o conceito de encarceramento difere do nacional.

## Diferenças metodológicas relevantes em relação a 2018

- base monetária mudou de reais de 2017 para reais de dezembro de 2025;
- segurança pública usa uma nova cadeia de fontes e anos de quebra;
- segurança privada passou de empresa/CNAE e imputação de informalidade (RAIS/PNAD) para ocupação e estimativa direta pela PNAD/PNAD Contínua, com multiplicador 1,86;
- encarceramento passou para despesa liquidada consolidada na subfunção 421, líquida de transferências entre União e UFs, e removeu a soma separada de pessoal;
- seguros/danos passaram a combinar prêmio direto, sinistro híbrido e nova reconstrução de perdas de veículos;
- perda produtiva usa perfis idade–região da PNAD Contínua 2025, sobrevivência e imputação explícita, em lugar dos perfis 2012/2017 do relatório antigo;
- processos judiciais agora cobrem Justiça Estadual, com novos pesos e métodos para TJ, MP e defesa, em vez do escopo que também incluía tribunais federais;
- saúde passou de SIH+SIA com fatores agregados e proxy de 10% para SIH apenas, custo observado da AIH e dias efetivos de afastamento.

Essas mudanças justificam diferenças históricas moderadas sem constituir problemas de qualidade. Não foi produzida reconciliação ponto a ponto com os números de 2018.

## Entradas e metadados ausentes

- arquivos-fonte e código de produção que geraram as duas planilhas finais;
- fonte, release/vintage e transformação do PIB nacional;
- fonte, release/vintage, referência da população e transformação de PIB/população das UFs;
- conversão exata dos rendimentos PNAD Contínua de preços médios de 2025 para dezembro de 2025;
- fonte e construção do encarceramento por UF;
- semântica dos vazios de subfunções da segurança pública por UF;
- fonte/justificativa dos pesos usados para ratear seguros e danos por UF;
- origem temporal exata do bloco UF de perdas produtivas rotulado 2025;
- flags de revisão/provisoriedade dos insumos de 2025.

## Decisões metodológicas pendentes

As questões MD-P01, MD-P02, MD-P04, MD-P05 e MD-P06 permanecem em `METHODOLOGY-DECISIONS.md`. MD-014 e MD-015 permitem avançar com alertas para MP e perdas produtivas estaduais; ambas as reconciliações são obrigatórias antes da publicação. MD-P03 está temporariamente coberta pela decisão não bloqueante MD-014, mas a escolha do vintage do MP ainda precisa ser fechada antes da publicação.

## Próxima tarefa recomendada

As Seções 1–6 de `docs/report.md` formam agora uma primeira versão completa em português, com as
Figuras 1–15 integradas nos respectivos argumentos. A Seção 5.3 proposta não foi aberta: os
desfechos criminais comparáveis e os custos estaduais têm anos terminais e conceitos distintos, e
os custos por UF de 2025 ainda são preliminares. Forçar uma associação nesse estágio adicionaria
mais ressalvas do que informação.

A auditoria da redação recalcula 205 estatísticas a partir dos CSVs de figura, dos workbooks e do painel UNODC retido e mantém o ledger em
`data/audit/report_sections_3_5_claims.csv`. A checagem integral reconciliou 75 representações
decimais distintas nas Seções 3–5 e 87 no relatório completo, verificou 15 estatísticas de destaque em
`data/audit/report_headline_statistics.csv`, confirmou os 18 placeholders e a existência das saídas
PDF/PNG e registrou seis grupos de fontes em `data/audit/report_citation_audit.csv`. Não restam
`TODO`, `TBD`, `PENDING`, `XXX`, citações provisórias ou nomes brutos de variáveis no relatório.

A próxima etapa editorial recomendada é a revisão substantiva do autor, seguida de fact-check
externo, copyediting e diagramação. Em paralelo, a recuperação das pipelines que geram as planilhas
finais deve preservar os alertas de MP e perda de capacidade produtiva estadual. Antes da publicação,
atualizar os dados estaduais, regenerar os workbooks e rerodar:

```powershell
python -m src.validation.validate_data --json-out data/audit/workbook_validation.json
python -B -m src.validation.validate_homicide_data
python -B -m src.figures.build_homicide_figures
python -B -m src.figures.build_local_figures
python -B -m src.figures.build_external_figures
python -B -m src.validation.validate_report_sections_3_5 --check-draft
python -B -m src.validation.validate_report
python -B -m src.report.convert_appendix
python -B -m src.report.build_report
python -B -m src.report.build_word
```

O desenvolvimento da pipeline e a revisão substantiva estão liberados, e os validadores retornam
status 0. A liberação para publicação requer atualização e reconciliação da perda de capacidade
produtiva estadual, nova verificação do MP, fechamento dos metadados pendentes, copyediting,
diagramação e fact-check externo.
