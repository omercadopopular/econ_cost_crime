# Report specification

## Deliverable, audience, and scope

The principal deliverable is `docs/report.md`. Write it in Brazilian Portuguese for an informed policy audience. The report updates *Custos Econômicos da Criminalidade no Brasil* (2018) for the Inter-American Dialogue.

The update has three objectives:

1. extend the national and state series through the latest complete year, with 2025 as the target;
2. explain how the level and composition of measured costs changed since the original report; and
3. document material conceptual and methodological differences from 2018 without treating the published point estimates as numerical targets.

The report is primarily a descriptive accounting exercise. It should distinguish measured expenditures and losses from a causal social-welfare calculation.

## Required analytical structure

For every cost component, the text should answer five questions:

1. **What is measured?** Define the component and its accounting interpretation.
2. **How is it constructed?** Explain the source data and method in plain language.
3. **What changed?** Describe the main level, GDP-share, composition, and regional trends supported by the data.
4. **How does the update compare with 2018?** Identify source revisions, methodological changes, and breaks in comparability.
5. **What are the limitations?** State coverage gaps, imputations, possible overlap, and interpretive caveats.

Every quantitative statement must be generated from a named table, figure-ready file, or validated workbook calculation. Do not hard-code 2025 in prose until the relevant series has been verified as complete.

## Drafting sequence

Draft in this order:

1. Sections 3–5;
2. Section 6, conclusion;
3. Section 2, introduction;
4. Section 1, executive summary.

Do not draft the executive summary from planned results.

## Report outline

### 1. Sumário executivo

Complete last. State the principal findings, magnitudes, changes since 2018, regional heterogeneity, and the most important measurement caveats. Avoid introducing evidence not developed in the report.

### 2. Introdução

Complete second to last. Motivate the economic relevance of criminality, define the accounting perimeter, explain what is new relative to the 2018 report, and preview the findings and structure.

### 3. Homicídios e criminalidade no Brasil

Cover:

- Brazil's homicide rate relative to the international distribution;
- national trends in reported crimes over the most recent comparable period;
- differences across states and substate areas;
- changes in the geographic concentration of homicides;
- data-coverage and reporting limitations.

Integrate Figures 1–4. State disaggregation belongs here when it explains crime incidence; place it in Section 5 when it is used to interpret regional cost burdens.

### 4. Estimando os custos econômicos da criminalidade

Open the section by defining the accounting perimeter and distinguishing resource costs, expenditures, transfers, insured or material losses, and estimated productive-capacity losses. Explain potential overlap before presenting the aggregate.

#### 4.1 Custos de segurança pública e privada

Explain public-security expenditures by level of government and private-security costs by formal and informal provision. Integrate Figures 5 and 6.

#### 4.2 Custos de encarceramento

Explain custody and reintegration expenditures and the separate accounting treatment of `auxílio-reclusão`. Integrate Figure 7.

#### 4.3 Custos de seguros e perdas materiais

Explain insurance-related costs and estimated material losses, preserving their different economic interpretations. Integrate Figure 8.

#### 4.4 Perda de capacidade produtiva

Explain the valuation of premature mortality or injury-related productive-capacity losses, including the assumptions that drive the estimate. Integrate Figure 9.

#### 4.5 Custos dos processos judiciais

Explain the crime-attributable portions of courts, public prosecutors, and defense or legal-aid institutions. Integrate Figure 10.

#### 4.6 Serviços médico-terapêuticos e recuperação de feridos

Explain the construction of health-service costs attributable to violence and their coverage limitations. Integrate Figure 11.

#### 4.7 Custos econômicos totais

Aggregate the components only after explaining denominator consistency, overlap, and the treatment of transfers. Discuss changes in levels, GDP share, and composition. Integrate Figure 12.

### 5. Padrões regionais

Describe how the measured burden varies across states and over time. Relate the GDP share of costs to real GDP per capita without interpreting the association causally. Discuss whether convergence in income is accompanied by convergence in the crime-cost burden. Integrate Figures 13 and 14.

### 6. Conclusão

Complete after Sections 3–5. Summarize the robust findings, explain what the accounting exercise does and does not establish, and identify the principal measurement priorities for future updates.

## Historical comparability

Treat the final workbooks as the numerical ground truth and the 2018 report as a conceptual and historical benchmark. Do not prepare a point-by-point numerical reconciliation merely because overlapping estimates differ modestly. State generally that updated historical values may reflect source, deflator and method revisions, and flag changes that materially alter interpretation.

Prepare a targeted reconciliation only when a discrepancy is large or unusual enough to indicate a possible coding error, unit error, accounting inconsistency or genuine methodological break. For such cases, record the affected component/year, competing values, reason class and evidence. Relevant reason classes are source revision, conceptual revision, coding correction, classification change, price-base revision, geographic change and imputation change.

## Figure insertion

While drafting, insert figures with comments rather than executable text:

```markdown
<!-- FIGURA 05: ../figs/fig_05_seguranca_publica.pdf -->
```

Reference every displayed figure in the surrounding prose and explain the comparison the reader should take from it. Do not narrate every plotted observation.

## Completion standard

A section is ready for review only when:

- its definitions agree with `docs/DATA-DICTIONARY.md`;
- its methodological statements agree with `docs/appendix.pdf` and `docs/METHODOLOGY-DECISIONS.md`;
- all numerical claims are reproducible;
- limitations and comparability breaks are explicit; and
- its status is updated in `docs/STATUS.md`.
