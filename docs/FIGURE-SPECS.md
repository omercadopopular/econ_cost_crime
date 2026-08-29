# Figure specifications

## Common rules

These specifications define the intended analytical content. `docs/graphing-style.md` defines the visual system.

- Use `ANO_FINAL` for the latest complete common year, with 2025 as the target. Do not label a figure as 2025 until completeness has been verified.
- In titles and subtitles, display the actual years used.
- Express monetary values in the convention documented in `docs/DATA-DICTIONARY.md`. State the constant-price base year and deflator in the note.
- For Figures 5–8 and 10, “share of total” means the share of the relevant cost component, so the plotted categories should sum to 100% within each year. For Figure 12, it means the share of total measured economic costs of crime.
- Use publication-quality Portuguese labels. Never print raw workbook column names.
- Every script must export PDF and PNG versions to `figs/` and, whenever feasible, a figure-ready CSV to `data/figure_data/`.
- Source notes must identify the institution, series or database, author calculations, and any non-obvious transformation.
- Validate totals, denominators, missing values, year coverage, and geographic coverage before plotting.
- When a preferred period is unavailable, use the nearest defensible common period and document the change in `docs/METHODOLOGY-DECISIONS.md` and `docs/STATUS.md`.

## Figure 1 — Mundo: distribuição das taxas de homicídio

**Output stem:** `fig_01_distribuicao_mundial_homicidios`

**Purpose:** Compare Brazil with the cross-country distribution in two non-overlapping periods.

**Preferred design:** Two aligned panels.

- Panel A: average homicide rate in 2006–2015.
- Panel B: average homicide rate in 2016–2025.
- If 2025 is unavailable, use the latest two non-overlapping windows of equal length ending in the latest complete year. Report the exact windows.
- Unit of observation: country.
- Vertical axis: average homicides per 100,000 inhabitants.
- Horizontal axis: percentile in the unweighted country distribution.
- Highlight Brazil and report its percentile in each panel.
- Prefer a common country sample across panels. Require a documented minimum annual coverage within each window; report sample size and coverage rule.
- Do not mix national sources or interpolate missing annual rates without documentation.

**Source:** UNODC, with author calculations.

## Figure 2 — Brasil: tendências da criminalidade

**Output stems:** `fig_02a_crimes_registrados` and `fig_02b_taxas_criminalidade`

**Purpose:** Show recent national trends in consistently defined reported crimes.

**Preferred design:** The same small-multiple layout in two companion versions.

- Figure 2A: incident counts.
- Figure 2B: incidents per 100,000 inhabitants using a documented IBGE population series.
- Horizontal axis: year.
- Vertical axis: incidents or incidents per 100,000, as applicable.
- Use the same offenses, ordering, and period in both versions.
- Include only offenses with sufficiently stable definitions and reporting coverage. Do not merge categories across classification breaks without a documented crosswalk.
- Annotate material changes in coverage, reporting rules, or participating jurisdictions.
- Produce a state-level validation or appendix output when comparable state reporting is feasible; do not force state disaggregation when coverage is inconsistent.

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

## Figure 5 — Brasil: gastos com segurança pública

**Output stem:** `fig_05_seguranca_publica`

**Input:** `data/output/tabela_final_cec_brasil.xlsx`

**Preferred design:** Three aligned panels by level of government: União, states/Federal District, and municipalities.

- Panel A: constant reais, preferably R$ billions.
- Panel B: percentage of GDP.
- Panel C: percentage composition of total public-security expenditure.
- Verify whether the workbook series are consolidated or gross of intergovernmental transfers and state the treatment in the note.
- Categories in Panel C must sum to 100% within numerical tolerance.

**Source:** Author calculations; see the methodological appendix for underlying official sources and construction.

## Figure 6 — Brasil: gastos com segurança privada

**Output stem:** `fig_06_seguranca_privada`

**Input:** `data/output/tabela_final_cec_brasil.xlsx`

**Preferred design:** Three aligned panels for formal and informal private-security provision.

- Panel A: constant reais.
- Panel B: percentage of GDP.
- Panel C: percentage composition of total private-security expenditure.
- Use publication labels such as “setor formal” and “provisão informal”; do not expose raw variable names.
- Categories in Panel C must sum to 100% within numerical tolerance.

**Source:** Author calculations using RAIS/MTb, IBGE, and PNADC; see the methodological appendix.

## Figure 7 — Brasil: custos de encarceramento e auxílio-reclusão

**Output stem:** `fig_07_encarceramento_auxilio_reclusao`

**Input:** `data/output/tabela_final_cec_brasil.xlsx`

**Preferred design:** Three aligned panels for custody and reintegration expenditures and `auxílio-reclusão`.

- Panel A: constant reais.
- Panel B: percentage of GDP.
- Panel C: percentage composition of the displayed accounting component.
- Replace raw labels such as `custodia_&_reintegracao` with publication-quality Portuguese.
- Identify `auxílio-reclusão` explicitly as a transfer rather than a direct resource cost. Preserve the original accounting treatment in totals unless a documented methodology decision changes it.
- Categories in Panel C must sum to 100% within numerical tolerance.

**Source:** Author calculations using IBGE, Anuários Estatísticos da Previdência Social, Departamento Penitenciário Nacional, and the CPI sobre o Sistema Penitenciário Nacional; see the methodological appendix.

## Figure 8 — Brasil: seguros e perdas materiais

**Output stem:** `fig_08_seguros_perdas_materiais`

**Input:** `data/output/tabela_final_cec_brasil.xlsx`

**Preferred design:** Three aligned panels for automotive, property, transport/cargo, and material-loss components documented in the data dictionary.

- Panel A: constant reais.
- Panel B: percentage of GDP.
- Panel C: percentage composition of total insurance and material-loss costs.
- Use a stable, documented display mapping for all components.
- Explain in the note that insurance expenditures or claims and material losses have different accounting interpretations.
- Categories in Panel C must sum to 100% within numerical tolerance.

**Source:** Author calculations using Susep and IBGE. State the precise Susep products, aggregation frequency, and terminal year documented in the data dictionary and methodological appendix.

## Figure 9 — Brasil: perda de capacidade produtiva

**Output stem:** `fig_09_perda_capacidade_produtiva`

**Input:** `data/output/tabela_final_cec_brasil.xlsx`

**Preferred design:** Two vertically aligned panels rather than a dual-axis chart.

- Panel A: constant reais.
- Panel B: percentage of GDP.
- The note must summarize the valuation basis and direct readers to the methodological appendix.
- If the estimate is model-based, distinguish it visually and textually from observed expenditure series.

**Source:** Author calculations; see the methodological appendix.

## Figure 10 — Brasil: custos judiciais associados à criminalidade

**Output stem:** `fig_10_custos_judiciais`

**Input:** `data/output/tabela_final_cec_brasil.xlsx`

**Preferred design:** Three aligned panels for courts, public prosecutors, and defense or legal-aid institutions, using the exact conceptual mapping in the data dictionary.

- Panel A: constant reais.
- Panel B: percentage of GDP.
- Panel C: percentage composition of total judicial costs attributed to criminality.
- Do not label an aggregate simply as “defesa” unless the underlying institutions and perimeter are defined.
- Categories in Panel C must sum to 100% within numerical tolerance.

**Source:** Author calculations using Conselho Nacional de Justiça, Conselho Nacional do Ministério Público, relevant federal budget or planning sources, and IBGE; see the methodological appendix.

## Figure 11 — Brasil: custos médico-terapêuticos

**Output stem:** `fig_11_custos_medico_terapeuticos`

**Input:** `data/output/tabela_final_cec_brasil.xlsx`

**Preferred design:** Two vertically aligned panels rather than a dual-axis chart.

- Panel A: constant reais.
- Panel B: percentage of GDP.
- The note must identify the coverage of injuries, services, and valuation inputs.

**Source:** Author calculations; see the methodological appendix.

## Figure 12 — Brasil: custos econômicos da criminalidade

**Output stem:** `fig_12_custos_economicos_criminalidade`

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
- Panel C: percentage composition of total measured economic costs of crime.
- Components in Panel C must sum to 100% within numerical tolerance.
- The note must flag transfers, model-based components, and any known overlap retained in the total.
- Use the same component ordering and display mapping across all panels and related text.

**Source:** Author calculations; see the methodological appendix.

## Figure 13 — UFs: nível e composição dos custos econômicos da criminalidade

**Output stem:** `fig_13_custos_economicos_ufs`

**Input:** `data/output/tabela_final_cec_ufs.xlsx`

**Reference year:** latest year with complete, comparable coverage across all 27 federative units.

**Preferred design:** Two panels.

- Panel A: scatterplot of total measured costs as a percentage of state GDP against real state GDP per capita. Label UFs with abbreviations. Use GDP, population, price base, and vintage documented in the data dictionary.
- Panel B: horizontal stacked bars showing component contributions as percentages of state GDP. Order UFs by total burden. Use all 27 UFs unless a documented coverage problem requires exclusion.
- Do not describe the cross-sectional association as causal.
- Report the actual reference year in the title and note.

**Source:** Author calculations from the state workbook and the underlying official sources documented in the appendix.

## Figure 14 — UFs: trajetória da renda e do custo da criminalidade

**Output stem:** `fig_14_trajetoria_renda_custo_ufs`

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
