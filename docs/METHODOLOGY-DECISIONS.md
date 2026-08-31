# Methodology decisions

This is the authoritative decision log for deviations from, clarifications of, or extensions to the 2018 methodology. Do not rewrite history: append or supersede entries and preserve the rationale.

## Active decisions

| ID | Date | Decision | Rationale | Affected outputs | Status |
|---|---|---|---|---|---|
| MD-001 | 2026-08-29 | Preserve a formal reconciliation between the published 2018 values and the updated vintage over their common period. | A longer series is not comparable if historical revisions are hidden. | All components and totals | Superseded by MD-009 |
| MD-002 | 2026-08-29 | Treat 2025 as the target terminal year, but use the latest complete common year whenever 2025 is incomplete. | Prevents mixed-vintage aggregates and misleading titles. | Report, tables, all figures | Active |
| MD-003 | 2026-08-29 | Distinguish resource costs, expenditures, transfers, insurance-related flows, material losses, and model-based productive-capacity losses in text and notes. | These objects have different economic interpretations even when retained in one accounting total. | Sections 4.1–4.7; Figures 6–13 | Active |
| MD-004 | 2026-08-29 | In Figures 6–9 and 11, composition shares use the relevant component total as denominator; Figure 13 uses total measured economic costs of crime. | Removes ambiguity in “share of total.” | Figures 6–9, 11, 13 | Active |
| MD-005 | 2026-08-29 | Use two non-overlapping periods for the international homicide comparison. Preferred windows are 2006–2015 and 2016–2025; use equal-length alternatives if the terminal period is incomplete. | The earlier draft incorrectly compared a ten-year average with a twenty-year average. | Figure 1 | Superseded by MD-023 |
| MD-006 | 2026-08-29 | Prefer aligned level and GDP-share panels to dual y-axes for productive-capacity and medical-therapeutic costs. | Improves scale transparency and comparability. | Figures 9 and 11 | Active |
| MD-007 | 2026-08-29 | Hold substate geography fixed across the microrregional level and change figures. | Prevents boundary changes from being interpreted as changes in homicide rates. | Figures 3 and 4 | Active |
| MD-008 | 2026-08-29 | Figure 15 plots arrows from 2016 levels to terminal-year levels in real GDP per capita and cost share of GDP. It does not put changes on the axes. | An arrow between level pairs and a scatterplot of changes are different estimands. | Figure 15 | Active |
| MD-009 | 2026-08-29 | Treat the two final workbooks as numerical ground truth. Use the 2018 report only for concepts, historical interpretation and presentation; do not force current historical point estimates to match it. Investigate a discrepancy only when it indicates a likely code/unit/accounting error or a material methodological break. | Current source and method revisions legitimately change historical estimates. This rule supersedes the blanket reconciliation requirement in MD-001. | All data validation, figures and report statistics | Active |
| MD-010 | 2026-08-29 | Use December 2025 reais as the common monetary convention, with IPCA as the project deflator; retain explicit notice that PNAD Contínua earnings first use CO2 at average-2025 prices and that the final average-to-December adjustment is `PENDING`. | A single price convention is needed for addition, but the unresolved PNAD transformation must not be silently inferred. | All monetary components | Active with metadata pending |
| MD-011 | 2026-08-29 | The corrected UF incarceration component may enter pipeline development, but must be labelled as a different construction from the national subfunction-421 measure and reviewed before publication. | The ×12 correction is propagated and passes mechanically; the UF method still adds staff separately, unlike the national method. | UF comparisons, maps, totals and Figures 14–15 | Active; pre-publication review required |
| MD-012 | 2026-08-29 | Label the national 2025 productive-loss value as modeled from the aggregate 2025 homicide count and the 2024 age-region loss profile. Do not describe the age-region structure as observed in 2025. | The source now scales the 2024 loss by `40.775/42.590`; 2025 age-region microdata remain unavailable. | National total, productive-loss figures and terminal-year prose | Active |
| MD-013 | 2026-08-29 | Retain insurance premiums, insurance loss measures and material losses as separately labelled objects. If the workbook's `amplo` sum is shown, describe it as an accounting scenario with potential overlap, not a causal welfare loss. | These flows have different incidence and can overlap; addition does not make them a homogeneous welfare concept. | Insurance/material component, total and notes | Active |
| MD-014 | 2026-08-29 | Treat the national–UF MP discrepancy as a documented, non-blocking warning while the source pipeline is reconstructed. Require a fresh reconciliation before publication. | The difference is isolated to MP; the source inputs will be reviewed and adjusted during pipeline construction. It should remain visible without preventing the next development stage. | Justice series, validation and publication gate | Active; pre-publication check required |
| MD-015 | 2026-08-29 | Treat the 2025 national–UF productive-loss discrepancy as a documented, non-blocking warning during pipeline construction. Update the state source data and require exact revalidation before publication. | The national series uses 40.775 homicides and R$ 29,17 billion, while current UFs sum to 36.362 and R$ 25,31 billion. The state inputs are known to be pending revision, so the discrepancy should remain visible without blocking pipeline development. | UF productive losses, UF totals, regional outputs and publication gate | Active; state update and pre-publication check required |
| MD-016 | 2026-08-29 | In Figure 5, show the authoritative public-security total for 1996–2025 and the federal/state/municipal percentages only in years where all three workbook components are numeric (currently 2016–2025). Do not impute the missing historical decomposition; detect newly populated component years on every run. | The total is complete but the three source columns are not. Imputation would create unsupported historical shares, while dynamic detection lets an upstream workbook revision flow through automatically. | Figure 5, its figure-ready CSV and validation | Active |
| MD-017 | 2026-08-29 | Define homicide from SIM `CAUSABAS` as X85–X99, Y00–Y09, Y35 or Y36, by municipality of residence and for all ages. Do not filter on `CIRCOBITO`; exclude Y10–Y34. | This is the definition documented in the current appendix. It includes legal intervention and operations of war and supersedes the legacy-script filters `CIRCOBITO == 3` and ages 1–99. | Homicide pipeline; Figures 3 and 4 | Active |
| MD-018 | 2026-08-29 | Set `ANO_FINAL_SIM = 2024`, use only final SIM annual files, and select the final `DO23OPEN.csv` route for 2023. Retain but do not use the generic 2023 conversion that fails the official national reconciliation. | The Ministry catalog identifies 2024 as final and 2025 as preliminary. `DO23OPEN` gives 45.747 homicides and 2024 gives 42.590, matching published totals; the generic 2023 conversion gives only 38.559. | Figures 3 and 4; retained-source manifest | Active |
| MD-019 | 2026-08-29 | Hold the 558 IBGE microrregiões and their municipality membership fixed at the 2015 vintage. Exclude, without allocation, SIM deaths recorded as `UF0000`; report their number and share. | Fixed geography prevents boundary changes from becoming measured violence changes. `UF0000` identifies no municipality, so allocating it would invent substate location; match rates remain 98,42%–98,92% at the two principal endpoints. | Crosswalk, microrregional rates, Figures 3 and 4 | Active |
| MD-020 | 2026-08-29 | Keep the requested single-year 2016–2024 change as Figure 4. Use pooled 2015–2017 and 2022–2024 rates only as a noise diagnostic; interpolate 2023 municipality population linearly between official 2022 and 2024 values solely for that diagnostic. | The annual and pooled changes have correlation 0,889 and the same direction in 81,5% of microrregiões, so smoothing does not overturn the broad map, although it attenuates local small-population noise. | Figure 4 and robustness audit | Active |
| MD-021 | 2026-08-30 | Use 2016–2025 and all 27 UFs in Figures 2A–2B for six Sinesp victim indicators with complete monthly reporting: homicídio doloso, latrocínio, tentativa de homicídio, estupro, estupro de vulnerável and feminicídio. Show four property-crime occurrence indicators separately in Figures 2C–2D and never convert non-reporting to zero. | The six principal series have 12 months and 27 UFs in every year. Drug trafficking and seized firearms remain diagnostics because they partly measure enforcement activity, and firearms are objects rather than crimes or victims. | Sinesp panel and Figures 2A–2D | Active; partial-coverage sample rule superseded by MD-024 |
| MD-022 | 2026-08-30 | Use equal, non-overlapping UNODC windows 2005–2014 and 2015–2024. Require at least 8 of 10 annual rates in each window and use the resulting common sample of 91 official country/territory reporting units. Calculate unweighted average-rank percentiles as `100 × (rank−1)/(N−1)`, averaging tied ranks. Retain ISO-3 territories in the UNODC `Country` universe and exclude explicitly subnational compound identifiers. | The official July 2026 release ends in 2024. Equal ten-year windows are more comparable than retaining a nine-year second window. Annual 2024 coverage is 95 reporting units, but decade means remain protected by the 8-of-10 common-sample rule; no rates are interpolated. | UNODC panel and Figure 1 | Superseded by MD-023 |
| MD-023 | 2026-08-30 | Compare the UNODC cross-sections of 2016 and 2024 in Figure 1, using the common sample of 87 official country/territory reporting units observed in both years. Keep the unweighted average-rank percentile convention and do not interpolate or splice national data. | The author requested a direct comparison of the report's recent initial year with the latest broadly covered UNODC year. A fixed common sample isolates changes in rates and ranks from changes in reporting composition, while the text notes that single-year comparisons are more sensitive to transitory variation than period means. | UNODC comparison panel, Figure 1 and Sections 1–3 and 6 | Active; supersedes MD-022 |
| MD-024 | 2026-08-30 | In Figures 2C–2D, use the largest 2016–2025 time-balanced UF panel separately for each property-crime indicator. Keep the count and rate sample identical within an indicator and report excluded UFs and terminal-year population coverage in the figure note. | Requiring a common panel for all four indicators reduces the sample to 19 UFs, while indicator-specific panels retain 22 UFs for vehicle theft/robbery and 20 for cargo and financial-institution robbery. The 2016–2025 rate changes differ from the common-panel results by at most 0.7 p.p.; the larger panels therefore improve coverage without changing the substantive trends. | Sinesp partial-coverage panel, Figures 2C–2D and report Section 3.2 | Active; supersedes the partial-coverage sample rule in MD-021 |

## Material methodological differences from the 2018 report

Modest differences in overlapping historical point estimates are expected because the updated data incorporate source, deflator and method revisions. The table records only differences that change interpretation or comparability.

| Component | 2018 benchmark | Current methodology | Why it matters | Revision class |
|---|---|---|---|---|
| Monetary convention | Reais constantes de 2017 | Reais de dezembro de 2025, generally by IPCA; PNAD Contínua earnings use CO2 before final harmonization | All monetary levels change; this is not evidence of an error | `PRICE_BASE_REVISION` |
| Public security | Historical chain based on Ipea/STN through 2001 and Peres et al./STN for 2002–2015 | Ipea/STN 1996–2003, STN consolidation 2004–2011, annual FBSP publications 2012–2025 | Source/classification breaks occur in different years and historical values may be revised | `SOURCE_REVISION`, `CLASSIFICATION_CHANGE` |
| Private security | RAIS establishment activity (CNAE 7460-8) for formal employment; formal payroll doubled for costs; informality and 70% wage assumption from PNAD | Occupation-based PNAD/PNAD Contínua series is primary; formal multiplier 1,86; informal employment and wages estimated directly; research break in 2012; RAIS only robustness | Changes target population, formal/informal allocation and labor-cost valuation | `CONCEPTUAL_REVISION`, `SOURCE_REVISION`, `IMPUTATION_CHANGE` |
| Incarceration | Three-part construction using prison administration, separately estimated personnel and auxílio-reclusão, anchored around 2013–2014 | Consolidated liquidated expenditure in subfunction 421 plus auxílio; federal transfers to UFs removed; separate personnel excluded; detailed retroprojection and UF imputations | Changes coverage and removes a potential personnel double count; auxiliary benefit remains a transfer | `CONCEPTUAL_REVISION`, `SOURCE_REVISION`, `IMPUTATION_CHANGE` |
| Insurance/material loss | Susep retained claims; vehicle loss based on Sinesp 2004–2015, homicide-regression backcast and a fixed VW Gol price | Direct premiums, hybrid direct/incurred claims, national FBSP vehicle counts from 2013, fixed SP+RJ expansion before 2013, AutoSeg/IPCA price chain and 36,5% recovery | Introduces a claims-definition break and materially different imputation/valuation | `CONCEPTUAL_REVISION`, `SOURCE_REVISION`, `IMPUTATION_CHANGE` |
| Productive capacity | PNAD Contínua 2017 income profiles plus 2012 employment probabilities for a restricted comparison group; fitted age profiles | PNAD Contínua 2025 expected earnings by age × region for the population, survival probabilities, explicit 2% growth and 3% discount, age-missing imputation | Changes the counterfactual earnings profile, geography and age treatment | `CONCEPTUAL_REVISION`, `SOURCE_REVISION`, `IMPUTATION_CHANGE` |
| Judicial processes | Included state courts and federal regional courts; older TJ staffing extrapolation, MP 2011–2017 relationship and ordinary-process OAB valuation | Justice Estadual only; UF-year sentence weights for TJs, reconstructed MPs, separate common/JECRIM defense values using current OAB references | Geographic/institutional scope changes and defense is valued differently | `COVERAGE_CHANGE`, `CONCEPTUAL_REVISION`, `IMPUTATION_CHANGE` |
| Medical/therapeutic | SIH and SIA scaled with budget/underreporting adjustments; temporary loss approximated as 10% of a homicide loss per admission | SIH hospitalizations only; observed AIH value plus actual nonfatal days × expected daily income; explicit missing-month imputations | Narrows service coverage while replacing a coarse productive-loss proxy with a duration-based model | `COVERAGE_CHANGE`, `CONCEPTUAL_REVISION`, `IMPUTATION_CHANGE` |
| Microrregional homicide figures | Legacy consolidation restricted `CIRCOBITO == 3` and age codes corresponding to 1–99 years; 2015 geography/population were joined ad hoc | Current appendix definition uses `CAUSABAS` X85–X99, Y00–Y09, Y35 and Y36, all ages, residence, fixed 2015 microrregiões and versioned annual population denominators | Changes sample membership and makes the cross-period geography and denominator explicit; old plotted values are not a numerical target | `CONCEPTUAL_REVISION`, `COVERAGE_CHANGE`, `GEOGRAPHIC_CHANGE` |

## Unresolved decisions requiring judgment

### MD-P01 — UF incarceration

- **Question:** should the UF series be rebuilt from the same subfunction-421 concept as the national series, or should the current prisoner/staff model be retained after correcting its annualization?
- **Why it matters:** it determines UF rankings and totals and may introduce personnel double counting.
- **Alternatives:** (a) rebuild from subfunction 421 and decide how to allocate auxílio; (b) multiply prisoner cost by 12 and retain the separate staff model; (c) publish no UF incarceration result.
- **Evidence:** the appendix documents (a) for the national series and explicitly rejects separate staff addition; the UF workbook now applies ×12 consistently through source and aggregate abas but still lacks source metadata.
- **Recommended next step:** preserve the mechanically consistent series during pipeline construction, then rebuild/trace or explicitly approve the distinct UF concept before publication.

### MD-P02 — Productive losses in the terminal year

- **Question:** should the current scaling by the aggregate 2025 homicide count be retained until age-region microdata are available, and how should the UF block be rebuilt?
- **Why it matters:** the national source/summary and UF block differ by 4.413 deaths and R$ 3,861 billion.
- **Alternatives:** current scaled estimate with explicit label; actual 2025 microdata rebuild; common-year 2024 output.
- **Evidence:** the national source uses 40.775 and scales the 2024 loss by `40.775/42.590`; UFs retain 36.362 and the source year remains `PENDING`.
- **Recommended next step:** trace/rebuild the UF block in the pipeline; retain an explicit proxy label until age-region microdata are processed.
- **Interim decision:** per MD-015, retain the discrepancy as a warning and proceed with pipeline construction; do not certify final regional results until the state inputs are updated and revalidated.

### MD-P03 — Ministério Público national–UF vintage

- **Question:** which MP series/vintage is authoritative for 2016 and 2025?
- **Why it matters:** the appendix says the national total after 2009 is the sum of UFs, but UFs exceed the national value by 5,96% and 6,44%.
- **Alternatives:** rebuild national from current UFs; rebuild UFs from the national input; document a deliberate difference if concepts are not actually identical.
- **Evidence:** TJ and defense reconcile exactly, localizing the conflict to MP.
- **Recommended next step:** compare the upstream MP tables and production code, then regenerate the inconsistent output rather than patching workbook cells.
- **Interim decision:** per MD-014, keep the discrepancy as a note/warning and allow pipeline construction to advance; rerun this reconciliation before publication.

### MD-P04 — Denominator vintages

- **Question:** what GDP and population releases, reference dates and deflation steps produced the national and UF denominators?
- **Why it matters:** shares of GDP, GDP per capita and cross-UF comparisons cannot be fully cited without these vintages.
- **Alternatives:** recover existing lineage; or, with explicit authorization, rebuild all denominators from one official vintage.
- **Evidence:** formulas are internally correct and UF GDP sums reconcile with the national denominator, but metadata are absent.
- **Recommended next step:** locate the source files/code and record institution, table, release and checksum before figures.

### MD-P05 — Blank UF public-security subfunctions

- **Question:** do the 16 UF-year blank subfunction cells mean zero, non-reporting or inclusion in `demais_subfunções`?
- **Why it matters:** Excel `SUM` silently treats them as zero and definitions may not be comparable across UFs.
- **Alternatives:** certify zero; flag/impute missing; or rely only on the published total after confirming source treatment.
- **Evidence:** totals are mechanically correct over available cells, but neither workbook nor appendix defines blank semantics.
- **Recommended next step:** check the cited FBSP source tables and encode an explicit status flag.

### MD-P06 — Intergovernmental transfers in public-security expenditure

- **Question:** are the Union, state/DF and municipal public-security components consolidated for intergovernmental transfers, or are they gross expenditures that may count the same transferred resource in more than one sphere?
- **Why it matters:** it changes the interpretation of the total and may create double counting across government levels.
- **Alternatives:** (a) certify a consolidated total; (b) publish the gross total with an explicit overlap warning; (c) reconstruct a consolidated series from the source accounts.
- **Evidence:** the current workbook provides a total and, for 2016–2025, the three sphere values, but neither the workbook nor the available methodological appendix states the transfer treatment clearly enough to certify consolidation.
- **Recommended next step:** recover the STN/FBSP aggregation rules used upstream and document the treatment before publication. Until then, keep `PENDING` in the Figure 5 note.

## Entry template

Add new decisions using:

```text
ID:
Date:
Issue:
Decision:
Alternatives considered:
Evidence:
Rationale:
Affected variables/files/figures:
Comparability effect:
Approved by:
Status:
Supersedes:
```

## Revision classifications

Use one or more of these tags when historical values change:

- `SOURCE_REVISION`
- `CONCEPTUAL_REVISION`
- `CODING_CORRECTION`
- `CLASSIFICATION_CHANGE`
- `PRICE_BASE_REVISION`
- `GEOGRAPHIC_CHANGE`
- `IMPUTATION_CHANGE`
- `COVERAGE_CHANGE`
