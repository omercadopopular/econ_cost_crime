# Graphing style and output directions

- Charts should be clear and easy to understand. 
- They should avoid jargon.
- They should have a title and a subtitle.
- Axes should be properly labeled.
- A note should with the source should be explicit at the lower end.
- Legends should mapped to publication-quality Portuguese rather than printed directly if they use code/shorthand.
- Each graph should be associated with a single python script that places in the beginning of the code variables with:
    - input files names/paths
    - output file names/paths
    - title, subtitle, source note, axes labels
    - colors
    - if needed, line/legend maps
- Each graph should output one PDF and one PNG to /figs

if not docs/graphing-style.md:
    you will:
        - scan docs/bib/original-report.pdf
        - scan https://github.com/omercadopopular/Modelos_Graficos/blob/master/Histograma.ipynb
        - understand the instructions above
        - summarize the required graphing style for the original report

read docs/graphing-style.md

# Figures

- Figura 1. Mundo: Taxa de Homicídios.
    - y axis: Taxa de homicídios (por 100 mil habitantes)
    - x axis: Percentil da distribuição mundial
    - data points: country i's homicide rate
    - this should have a panel with two charts that shows two distributions: (2006-2015 average) and (2006-2025 average), depending on data availability
    - it should highlight where Brazil is in each decennial average and show the percentile
    - source: UNODC

- Figura 2. Brasil: Tendências de criminalidade (2016-2025).
    - y axis: counts
    - x axis: year
    - data points: crime reports, by crime
    - this should have a panel with multiple charts
    - you can essentially replicate/extend/update this code, adjusting formatting: https://github.com/omercadopopular/cgoes/blob/master/sinesp/sinesp.py
    - source: Sinespe (MJ)
    - check if it is possible to disaggregate it by state.
    - produce an identical version adjusted by population (rates per 100,000 people)

- Figura 3. Brasil: Taxa de Homicídios por Microrregião, 2025 (Homicídios	por	100	mil	 habitantes,	bolhas	proporcionais	à	população	da	microrregião)
    - Unit of observation: Brazilian microrregion.
    - y-axis: homicide rate per 100,000 residents.
    - x-axis: percentile of the microrregional homicide-rate distribution.
    - Bubble area: microrregional population.
    - One panel unless an explicit regional or temporal comparison is added.    
    - you can start from this code: https://github.com/omercadopopular/cgoes/blob/master/EconCostsViolenceBrazil/6.homicides_regional_analysis.py
    - source: Calculos dos autores com	dados	do	SIM/Ministério	da	Saúde	e	IBGE.
    - You may need to create a separate file to will process pre-process this data ahead of making the chart. I have used the following file to consolidate the DataSUS data before: https://github.com/omercadopopular/cgoes/blob/master/EconCostsViolenceBrazil/4.homicides_data_consolidation.py

Figura 4. Brasil: Variação na Taxa de Homicídios por Microrregião, 2016-2025 (Variação	absoluta	na	taxa	de	homicídios,	2016-2025)
    - This should be a map that shows the absolute change in homicide rates by microregion in Brazil, similar to the original report
    - source: Calculos dos autores com	dados	do	SIM/Ministério	da	Saúde	e	IBGE.
    - You may need to create a separate file to will process pre-process this data ahead of making the chart. I have used the following file to consolidate the DataSUS data before: https://github.com/omercadopopular/cgoes/blob/master/EconCostsViolenceBrazil/4.homicides_data_consolidation.py

Figura 5. Brasil: Gastos com Segurança Pública (1996-2025)
    - You can read/calculate shares directly from the data/output/tabela_final_cec_brasil.xlsx 
    - This should be a three panel Figure showing:
        - costs in constant Brazilian reais, by ente federativo
        - costs in share of GDP, by ente federativo
        - costs in share of total, by ente federativo
    - source: Calculos dos autores. Ver apêndice metodológico para detalhes.

Figura 6. Brasil: Gastos com Segurança Privada (1996-2025) 
    - You can read/calculate shares directly from the data/output/tabela_final_cec_brasil.xlsx 
    - This should be a three panel Figure showing:
        - costs in constant Brazilian reais, by formal/informal sector
        - costs in share of GDP, by formal/informal sector
        - costs in share of total, by formal/informal sector
    - source: Calculos dos autores com	microdados	da	RAIS/MTb,	IBGE	e	PNADC.	Ver	apêndice	metodológico	para	detalhes.

Figura 7. Brasil: Custos de Encarceramento e Auxílio-Reclusão (1996-2025) 
    - You can read/calculate shares directly from the data/output/tabela_final_cec_brasil.xlsx 
    - This should be a three panel Figure showing:
        - costs in constant Brazilian reais, by custodia_&_reintegracao e auxilio reclusao 
        - costs in share of GDP, by custodia_&_reintegracao e auxilio reclusao
        - costs in share of total, by custodia_&_reintegracao e auxilio reclusao
    - source: Calculos dos autores com		dados	do	IBGE;	dos	Anuários	Estatísticos	da	Previdência	Social;	Departamento	Penitenciário	Nacional;	e	CPI	sobre	o	Sistema	Penitenciário	Nacional.	Ver	apêndice	metodológico	para	detalhes.

Figura 8. Brasil: Gastos com Seguro e Perdas Materiais (1996-2025) 
    - You can read/calculate shares directly from the data/output/tabela_final_cec_brasil.xlsx 
    - This should be a three panel Figure showing:
        - costs in constant Brazilian reais, by seguro automotivo, seguro patrimonial, seguro de transporte e carga, perda patrimonial, perda de transportes e perda automobilistica
        - costs in share of GDP, by seguro automotivo, seguro patrimonial, seguro de transporte e carga, perda patrimonial, perda de transportes e perda automobilistica
        - costs in share of total, by seguro automotivo, seguro patrimonial, seguro de transporte e carga, perda patrimonial, perda de transportes e perda automobilistica
        - source: Calculos dos autores com	dados	do	Superintendência	de	Seguros	Privados	do	Ministério	da	Fazenda	(Susep/MF)	e	IBGE.	Entre	1996 2000,	dados	consolidados	dos	Boletins	Consolidados	do	Mercado	de	Seguros	para	dezembro	de	cada	exercício.	Entre	2001 2026,	dados	mensais	agregados,	disponíveis	no	SES	-	Sistema	de	Estatísticas	da	Susep

Figura 9. Brasil: Custo de perda de capacidade produtiva (1996-2025) 
    - You can read/calculate shares directly from the data/output/tabela_final_cec_brasil.xlsx 
    - This should be a single panel Figure showing:
        - costs in constant Brazilian reais (left axis)
        - costs in share of GDP (right axis)
        - source: Calculos dos autores. Ver	apêndice	metodológico	para	detalhes

Figura 10. Brasil: Custos Judiciais da Criminalidade (1996-2025) 
    - You can read/calculate shares directly from the data/output/tabela_final_cec_brasil.xlsx 
    - This should be a three panel Figure showing:
        - costs in constant Brazilian reais, by TJs, MP, defesa
        - costs in share of GDP, by TJs, MP, defesa
        - costs in share of total, by TJs, MP, defesa
        - source: Calculos dos autores com	dados	do	Conselho	Nacional	da	Justiça,	Conselho	Nacional	do	Ministério	Público,	Ministério	do	
Planejamento	e	IBGE.

Figura 11. Brasil: Custos Médico-Terapêuticos (1996-2025) 
    - You can read/calculate shares directly from the data/output/tabela_final_cec_brasil.xlsx 
    - This should be a single panel Figure showing:
        - costs in constant Brazilian reais (left axis)
        - costs in share of GDP (right axis)
        - source: Calculos dos autores. Ver	apêndice	metodológico	para	detalhes

Figura 12. Brasil: Custos Econômicos da Criminalidade (1996-2025) 
    - You can read/calculate shares directly from the data/output/tabela_final_cec_brasil.xlsx 
    - This should be a three panel Figure showing:
        - costs in constant Brazilian reais, by Médico-terapêuticos, Encarceramento, Judiciais, Perda de capacidade produtiva, Seguros e perdas materiais, Segurança privada Segurança pública;
        - costs in share of GDP, by Médico-terapêuticos, Encarceramento, Judiciais, Perda de capacidade produtiva, Seguros e perdas materiais, Segurança privada Segurança pública;
        - costs in share of total, by Médico-terapêuticos, Encarceramento, Judiciais, Perda de capacidade produtiva, Seguros e perdas materiais, Segurança privada Segurança pública;
        - source: Calculos dos autores. Ver	apêndice	metodológico	para	detalhes

Figura 13. UFs: Custos Econômicos da Criminalidade (2025) 
    - You can read/calculate shares directly from the data/output/tabela_final_cec_ufs.xlsx 
    - This should be a two panel Figure showing:
        - first panel: a scatterplot showing custos	econômicos	da	criminalidade	como	percentual	do	PIB	estadual (y-axis)	e	renda	per	 capita	em	reais	de	2025 (x-axis)
        - second panel: bar plot showing custos	econômicos	da	criminalidade	como	percentual	do	PIB	estadual (y-axis) for each state (x-axis) decomposed by Médico-terapêuticos, Encarceramento, Judiciais, Perda de capacidade produtiva, Seguros e perdas materiais, Segurança privada Segurança pública. States should be ordered left-to right by the size of total cost as a share of GDP. 

Figura 14. UFs: Variação Custos Econômicos da Criminalidade (2016-2025) 
    - You can read/calculate shares directly from the data/output/tabela_final_cec_ufs.xlsx 
    - This should be a single panel Figure showing a scatterplot with arrows:
        - start_s = (GDP per capita_(s,2016), Custo Economico da Criminalidade_(s,2016))
        - end_s = (GDP per capita_(s,2025), Custo Economico da Criminalidade_(s,2025))
        - GDP per capita should be in constant BRL;
        - Custo Economico da Criminalidade should be in share of running year GDP.
    - The vectors should start at their 2016 values and end at their 2025 values;
    - The idea is to show that states increased their income and evaluate if the crime burden decreased or increased.  