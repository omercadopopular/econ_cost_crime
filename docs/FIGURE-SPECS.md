# Figure specifications

## Common rules

These specifications define the intended analytical content. `docs/graphing-style.md` defines the visual system.

- Use `ANO_FINAL` for the latest complete common year, with 2025 as the target. Do not label a figure as 2025 until completeness has been verified.
- In titles and subtitles, display the actual years used.
- Express monetary values in the convention documented in `docs/DATA-DICTIONARY.md`. State the constant-price base year and deflator in the note.
- For Figures 6–9 and 11, “share of total” means the share of the relevant cost component, so the plotted categories should sum to 100% within each year. For Figure 13, it means the share of total measured economic costs of crime.
- Use publication-quality Portuguese labels. Never print raw workbook column names.
- Every script must export PDF and PNG versions to `figs/` and, whenever feasible, a figure-ready CSV to `data/figure_data/`.
- Source notes must identify the institution, series or database, author calculations, and any non-obvious transformation.
- Validate totals, denominators, missing values, year coverage, and geographic coverage before plotting.
- For annual time series, use bars so that each year's value is visually discrete. Print every
  year on the horizontal axis and rotate the labels 90 degrees.
- Name panels that report category shares **"Percentual do total"**. The denominator is the
  relevant component total in Figures 6–9 and 11, and total measured crime costs in Figure 13.
- When an authoritative total exists but its component decomposition is unavailable for part of the
  period, show the total over the full available period and leave the decomposition visibly absent.
  Do not impute component shares solely to complete a figure. Figure code must detect newly populated
  source components and extend the decomposition automatically on the next run.
- When a preferred period is unavailable, use the nearest defensible common period and document the change in `docs/METHODOLOGY-DECISIONS.md` and `docs/STATUS.md`.

## Figure 1 — Mundo: distribuição das taxas de homicídio

**Output stem:** `fig_01_distribuicao_mundial_homicidios`

**Purpose:** Compare Brazil with the cross-country distribution in 2016 and 2024.

**Preferred design:** Two aligned panels.

- Panel A: homicide rate in 2016.
- Panel B: homicide rate in 2024, the latest year with sufficiently broad coverage in the retained UNODC vintage.
- Unit of observation: official country/territory reporting unit observed in both years.
- Vertical axis: intentional homicides per 100,000 inhabitants in the stated year.
- Horizontal axis: percentile in the unweighted country distribution.
- Highlight Brazil and report its percentile in each panel.
- Use the common sample observed in both panels and report its size.
- Do not mix national sources, fill missing annual rates or change the sample between panels.

**Source:** UNODC, with author calculations.

## Figure 2 — Brasil: tendências da criminalidade

**Output stems:** `fig_02a_crimes_registrados`, `fig_02b_taxas_criminalidade`,
`fig_02c_crimes_cobertura_parcial` and `fig_02d_taxas_cobertura_parcial`

**Purpose:** Show recent national trends in consistently defined reported crimes.

**Preferred design:** The same small-multiple layout in two companion versions.

- Figure 2A: incident counts.
- Figure 2B: incidents per 100,000 inhabitants using a documented IBGE population series.
- Horizontal axis: year.
- Vertical axis: incidents or incidents per 100,000, as applicable.
- Use the same offenses, ordering, and period in both versions.
- Print the value above every annual bar in Figures 2A–2D using Brazilian formatting. Count panels (2A and 2C) use no decimal places and display positive values below one thousand as `<1`. Rate panels (2B and 2D) use one decimal place and display positive values below 0.05 per 100,000 as `<0,1`, rather than rounding them to zero.
- Include only offenses with sufficiently stable definitions and reporting coverage. Do not merge categories across classification breaks without a documented crosswalk.
- Annotate material changes in coverage, reporting rules, or participating jurisdictions.
- Produce a state-level validation or appendix output when comparable state reporting is feasible; do not force state disaggregation when coverage is inconsistent.

**Companion figures for partial coverage:** Figures 2C (counts) and 2D (rates) show the
otherwise usable property-crime indicators that do not cover all 27 UFs: vehicle theft, vehicle
robbery, cargo robbery and robbery of financial institutions. Use a separate UF panel for each
indicator, balanced over the entire displayed period, to maximize valid geographic coverage without
changing the sample within a series. For every indicator, state in the note the excluded UFs and the
population share covered in the terminal year; never describe these values as Brazil-wide totals.
Do not replace missing reporting with zero. Figures 2C and 2D must use identical offenses, ordering,
period and, within each indicator, the same geographic sample.

**Legacy reference:** `sinesp/sinesp.py` in the pinned legacy-code commit listed in `docs/REFERENCE-FILES.md`.

**Source:** Sinesp/MJSP; IBGE population series for rates; author calculations.

## Figure 3 — Brasil: distribuição das taxas de homicídio por microrregião

**Output stem:** `fig_03_homicidios_microrregioes`

**Purpose:** Show the distribution and population exposure across substate areas in the latest complete SIM year.

**Preferred design:** One bubble chart.

- Unit of observation: a fixed-definition Brazilian microrregion.
- Vertical axis: homicides per 100,000 inhabitants.
- Horizontal axis: percentile in the unweighted microrregional distribution.
- Bubble **area**, not radius, is proportional to population.
- Use the same geographic vintage for deaths, population, and the change map in Figure 4.
- If the legacy microrregion classification is retained, document the municipal crosswalk and keep it fixed over time.
- The title must use the actual latest complete year; do not force 2025 when SIM data are incomplete.
- Identify Brazil-wide reference values only when they aid interpretation and are calculated consistently.

**Legacy references:** regional-analysis and data-consolidation scripts in the pinned legacy-code commit.

**Source:** Author calculations using SIM/Ministério da Saúde and IBGE.

## Figure 4 — Brasil: variação da taxa de homicídios por microrregião

**Output stem:** `fig_04_variacao_homicidios_microrregioes`

**Purpose:** Map changes in the local homicide rate between 2016 and the latest complete common year.

**Preferred design:** Choropleth map using a diverging scale centered at zero.

- Statistic: end-year rate minus 2016 rate, in homicides per 100,000 inhabitants.
- Use the same fixed geography, mortality definition, and population convention as Figure 3.
- Distinguish missing observations from zero changes.
- Report the endpoints in the title and note.
- Because annual rates can be noisy in small areas, produce a robustness version based on centered or trailing multi-year averages when feasible. Do not silently replace the annual-endpoint specification.

**Source:** Author calculations using SIM/Ministério da Saúde and IBGE.

## Figure 5 — Brasil: convergência das taxas de homicídio entre microrregiões

**Output stem:** `fig_05_convergencia_homicidios_microrregioes`

**Purpose:** Assess whether microrregions with higher homicide rates in 2016 subsequently registered larger absolute declines through 2024.

**Preferred design:** Population-weighted bubble scatterplot.

- Horizontal axis: homicide rate per 100,000 inhabitants in 2016.
- Vertical axis: 2024 rate minus 2016 rate, in homicides per 100,000 inhabitants.
- Bubble area: 2016 microrregion population.
- Include a population-weighted descriptive regression line and report its coefficient.
- State explicitly that the relationship is descriptive, that the initial rate enters mechanically in the dependent-variable change, and that the result may reflect regression to the mean.
- Retain the smoothed-endpoint diagnostic in the audit output.

**Source:** Author calculations using SIM/Ministério da Saúde and IBGE.

## Figure 6 — Brasil: gastos com segurança pública

**Output stem:** `fig_06_seguranca_publica`

**Input:** `data/output/tabela_final_cec_brasil.xlsx`

**Preferred design:** Three aligned panels by level of government: União, states/Federal District, and municipalities.

- Overlay a clearly identified total line in Panels A and B. Where the sphere decomposition is
  unavailable, retain the total bars and line rather than dropping those years.
- Panel A: constant reais, preferably R$ billions.
- Panel B: percentage of GDP.
- Panel C: percentage of total public-security expenditure.
- Verify whether the workbook series are consolidated or gross of intergovernmental transfers and state the treatment in the note.
- Categories in Panel C must sum to 100% within numerical tolerance.

**Source:** Author calculations; see the methodological appendix for underlying official sources and construction.

## Figure 7 — Brasil: gastos com segurança privada

**Output stem:** `fig_07_seguranca_privada`

**Input:** `data/output/tabela_final_cec_brasil.xlsx`

**Preferred design:** Three aligned panels for formal and informal private-security provision.

- Panel A: constant reais.
- Panel B: percentage of GDP.
- Panel C: percentage of total private-security expenditure.
- Use publication labels such as “setor formal” and “provisão informal”; do not expose raw variable names.
- Categories in Panel C must sum to 100% within numerical tolerance.

**Source:** Author calculations using RAIS/MTb, IBGE, and PNADC; see the methodological appendix.

## Figure 8 — Brasil: custos de encarceramento e auxílio-reclusão

**Output stem:** `fig_08_encarceramento_auxilio_reclusao`

**Input:** `data/output/tabela_final_cec_brasil.xlsx`

**Preferred design:** Three aligned panels for custody and reintegration expenditures and `auxílio-reclusão`.

- Panel A: constant reais.
- Panel B: percentage of GDP.
- Panel C: percentage of the displayed accounting component total.
- Replace raw labels such as `custodia_&_reintegracao` with publication-quality Portuguese.
- Identify `auxílio-reclusão` explicitly as a transfer rather than a direct resource cost. Preserve the original accounting treatment in totals unless a documented methodology decision changes it.
- Categories in Panel C must sum to 100% within numerical tolerance.

**Source:** Author calculations using IBGE, Anuários Estatísticos da Previdência Social, Departamento Penitenciário Nacional, and the CPI sobre o Sistema Penitenciário Nacional; see the methodological appendix.

## Figure 9 — Brasil: seguros e perdas materiais

**Output stem:** `fig_09_seguros_perdas_materiais`

**Input:** `data/output/tabela_final_cec_brasil.xlsx`

**Preferred design:** Three aligned panels for automotive, property, transport/cargo, and material-loss components documented in the data dictionary.

- Panel A: constant reais.
- Panel B: percentage of GDP.
- Panel C: percentage of total insurance and material-loss costs.
- Use a stable, documented display mapping for all components.
- Explain in the note that insurance expenditures or claims and material losses have different accounting interpretations.
- Categories in Panel C must sum to 100% within numerical tolerance.

**Source:** Author calculations using Susep and IBGE. State the precise Susep products, aggregation frequency, and terminal year documented in the data dictionary and methodological appendix.

## Figure 10 — Brasil: perda de capacidade produtiva

**Output stem:** `fig_10_perda_capacidade_produtiva`

**Input:** `data/output/tabela_final_cec_brasil.xlsx`

**Preferred design:** Two vertically aligned panels rather than a dual-axis chart.

- Panel A: constant reais.
- Panel B: percentage of GDP.
- The note must summarize the valuation basis and direct readers to the methodological appendix.
- If the estimate is model-based, distinguish it visually and textually from observed expenditure series.

**Source:** Author calculations; see the methodological appendix.

## Figure 11 — Brasil: custos judiciais associados à criminalidade

**Output stem:** `fig_11_custos_judiciais`

**Input:** `data/output/tabela_final_cec_brasil.xlsx`

**Preferred design:** Three aligned panels for courts, public prosecutors, and defense or legal-aid institutions, using the exact conceptual mapping in the data dictionary.

- Panel A: constant reais.
- Panel B: percentage of GDP.
- Panel C: percentage of total judicial costs attributed to criminality.
- Do not label an aggregate simply as “defesa” unless the underlying institutions and perimeter are defined.
- Categories in Panel C must sum to 100% within numerical tolerance.

**Source:** Author calculations using Conselho Nacional de Justiça, Conselho Nacional do Ministério Público, relevant federal budget or planning sources, and IBGE; see the methodological appendix.

## Figure 12 — Brasil: custos médico-terapêuticos

**Output stem:** `fig_12_custos_medico_terapeuticos`

**Input:** `data/output/tabela_final_cec_brasil.xlsx`

**Preferred design:** Two vertically aligned panels rather than a dual-axis chart.

- Panel A: constant reais.
- Panel B: percentage of GDP.
- The note must identify the coverage of injuries, services, and valuation inputs.

**Source:** Author calculations; see the methodological appendix.

## Figure 13 — Brasil: custos econômicos da criminalidade

**Output stem:** `fig_13_custos_economicos_criminalidade`

**Input:** `data/output/tabela_final_cec_brasil.xlsx`

**Preferred design:** Three aligned panels for:

- serviços médico-terapêuticos;
- encarceramento;
- custos judiciais;
- perda de capacidade produtiva;
- seguros e perdas materiais;
- segurança privada;
- segurança pública.

Panels:

- Panel A: constant reais.
- Panel B: percentage of GDP.
- Panel C: percentage of total measured economic costs of crime.
- Components in Panel C must sum to 100% within numerical tolerance.
- The note must flag transfers, model-based components, and any known overlap retained in the total.
- Use the same component ordering and display mapping across all panels and related text.

**Source:** Author calculations; see the methodological appendix.

## Figure 14 — UFs: nível e composição dos custos econômicos da criminalidade

**Output stem:** `fig_14_custos_economicos_ufs`

**Input:** `data/output/tabela_final_cec_ufs.xlsx`

**Reference year:** latest year with complete, comparable coverage across all 27 federative units.

**Preferred design:** Two panels.

- Panel A: scatterplot of total measured costs as a percentage of state GDP against real state GDP per capita. Label UFs with abbreviations. Use GDP, population, price base, and vintage documented in the data dictionary.
- Panel B: horizontal stacked bars showing component contributions as percentages of state GDP. Order UFs by total burden. Use all 27 UFs unless a documented coverage problem requires exclusion.
- Do not describe the cross-sectional association as causal.
- Report the actual reference year in the title and note.

**Source:** Author calculations from the state workbook and the underlying official sources documented in the appendix.

## Figure 15 — UFs: trajetória da renda e do custo da criminalidade

**Output stem:** `fig_15_trajetoria_renda_custo_ufs`

**Input:** `data/output/tabela_final_cec_ufs.xlsx`

**Preferred design:** Arrow plot in levels.

For each state \(s\):

\[
\text{start}_s =
\left(
GDPpc_{s,2016},
CECshare_{s,2016}
\right)
\]

\[
\text{end}_s =
\left(
GDPpc_{s,ANO\_FINAL},
CECshare_{s,ANO\_FINAL}
\right)
\]

- Horizontal axis: real state GDP per capita in the documented constant-price base.
- Vertical axis: total measured costs as a percentage of current-year state GDP.
- Use distinct start markers and arrowheads so direction is legible without relying only on color.
- Label states with abbreviations while minimizing overlap; facet by macroregion only if a single panel is unreadable.
- Use a common end year across all UFs and report it in the title.
- This is a descriptive trajectory, not a causal estimate of the effect of income on crime costs.
- Do not instead plot \((\Delta GDPpc_s,\Delta CECshare_s)\); that would be a different figure.

**Source:** Author calculations from the state workbook and the underlying official sources documented in the appendix.
