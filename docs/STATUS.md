# Status do projeto

**Atualizado:** 2026-08-29

## Situação atual

A primeira auditoria empírica e metodológica das duas planilhas finais foi concluída. Em seguida, as planilhas foram revisadas pelo autor para corrigir os erros identificados. O relatório de 2018 continua sendo usado apenas para conceitos e mudanças metodológicas materiais.

Na verificação da versão mais recente, o validador executou 3.247 verificações: 3.244 passaram, não restam erros mecânicos e 16 advertências exigem interpretação ou metadados. As diferenças agregadas dos MPs e das perdas produtivas UF de 2025 são não bloqueantes por decisões MD-014 e MD-015.

As Figuras 5–14 foram produzidas em PDF e PNG a partir de CSVs auditáveis em
`data/figure_data/`. As figuras nacionais usam 1996–2025. As figuras de UF usam 2025 como
`ANO_FINAL_UF` operacional porque as 27 UFs têm cobertura completa nas variáveis requeridas;
permanecem explicitamente preliminares devido à revisão pendente das perdas produtivas estaduais
e à diferença conceitual do encarceramento. A Figura 14 compara 2016 a 2025 em níveis.

## Trabalho concluído

- Inventário das oito abas nacionais e onze abas de UF.
- Identificação da unidade observacional, chave, cobertura, variáveis, unidades, fórmulas, deflatores, denominadores conhecidos e status de imputação/modelagem.
- Verificação de chaves únicas, tipos numéricos, anos esperados e 27 UFs em 2016 e 2025.
- Mapeamento variável–conceito–fonte–fórmula no `DATA-DICTIONARY.md`.
- Comparação conceitual com o relatório de 2018, sem reconciliação artificial dos pontos históricos.
- Testes de identidades contábeis, participações no PIB, pesos, PIB per capita e reconciliações Brasil–UF conceitualmente apropriadas.
- Implementação de `python -m src.validation.validate_data`, sem dependências externas, e geração de `data/audit/workbook_validation.json`.
- Implementação dos dez entry points em `src/figures/`, de um construtor conjunto e de validação específica para as Figuras 5–14.
- Exportação de dez CSVs publication-facing, dez PDFs, dez PNGs e um manifesto com hashes das saídas.
- Inspeção visual das dez PNGs. As séries anuais nacionais usam barras, imprimem todos os anos com rótulos a 90 graus e denominam o terceiro painel `Percentual do total`.
- Auditoria visual de figuras selecionadas do relatório de 2018 e do notebook histórico fixado por commit. O sistema atualizado preserva fundo branco, hierarquia tipográfica, legenda superior, grade horizontal e nota de fonte, com paleta acessível.

## Figuras locais e validação

| Figura | Período efetivo | Situação |
|---|---|---|
| 5 — Segurança pública | 1996–2025; percentuais por esfera em 2016–2025 | Concluída. Total exibido em todo o período; a decomposição é detectada dinamicamente e não é imputada |
| 6 — Segurança privada | 1996–2025 | Concluída |
| 7 — Encarceramento e auxílio-reclusão | 1996–2025 | Concluída; transferência identificada |
| 8 — Seguros e perdas materiais | 1996–2025 | Concluída; cenário contábil amplo e sobreposição sinalizados |
| 9 — Perda de capacidade produtiva | 1996–2025 | Concluída; medida modelada identificada visualmente |
| 10 — Custos judiciais | 1996–2025 | Concluída; alerta MP permanece no validador geral |
| 11 — Serviços médico-terapêuticos | 1996–2025 | Concluída |
| 12 — Total nacional | 1996–2025 | Concluída; sete componentes reproduzem o total dentro de R$ 2 e os percentuais somam 100% |
| 13 — Nível e componentes por UF | 2025 | Concluída como preliminar; 27 UFs e identidades por UF passam |
| 14 — Trajetórias por UF | 2016–2025 | Concluída como preliminar; cada UF aparece uma vez em cada ponta |

O validador de figuras executa 11 grupos de verificações: todos passaram, sem erros, com duas
advertências econômicas já documentadas (resultados estaduais preliminares e metadados de vintage
de PIB/população `PENDING`). O validador dos workbooks continua passando com 3.244 de 3.247
verificações, zero erros e 16 advertências.

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

Avançar para a construção da pipeline a partir dos dados-fonte, centralizando a geração das abas e preservando alertas para MP e perdas produtivas estaduais. As Figuras 1–4 permanecem fora desta etapa porque exigem insumos externos. Antes da publicação, atualizar os dados estaduais, regenerar os workbooks, reconstruir as Figuras 5–14 e rerodar:

```powershell
python -m src.validation.validate_data --json-out data/audit/workbook_validation.json
python -B -m src.figures.build_local_figures
```

O desenvolvimento da pipeline está liberado e os validadores retornam status 0. A liberação para publicação requer atualização/reconciliação das perdas produtivas estaduais e nova verificação do MP. A redação substantiva de `docs/report.md` ainda não foi iniciada; somente os placeholders das Figuras 5–14 foram atualizados.
