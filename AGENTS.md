# Repository instructions

## Project purpose

This repository updates the 2018 report *Custos Econômicos da Criminalidade no Brasil*. The principal deliverable is `docs/report.md`, written in Brazilian Portuguese for a policy audience. The update must preserve comparability with the original report while documenting every methodological revision, source change, imputation, and break in the time series.

The report is an accounting exercise. Do not present the accounting total as a causal welfare estimate unless a separate, defensible identification and valuation argument supports that interpretation.

## Task routing

Read only the context needed for the current task:

- report prose: `docs/REPORT-SPEC.md`, `docs/REFERENCE-FILES.md`, `docs/writing-style.md`, and the relevant methodological material;
- figures: `docs/FIGURE-SPECS.md`, `docs/graphing-style.md`, `docs/DATA-DICTIONARY.md`, and the relevant methodological material;
- calculations or data revisions: `docs/DATA-DICTIONARY.md`, `docs/METHODOLOGY-DECISIONS.md`, `docs/appendix.pdf`, and the associated source files or code;
- project planning or handoff: `docs/STATUS.md`.

Do not rescan every PDF or external repository on every run. If a required context document is missing, incomplete, or stale, update it as part of the task. Mark unresolved fields explicitly as `PENDING`; never fill them by assumption.

## Core references and source hierarchy

The principal repository inputs are:

1. `data/output/tabela_final_cec_brasil.xlsx`: national time series;
2. `data/output/tabela_final_cec_ufs.xlsx`: state-level time series;
3. `docs/appendix.pdf`: methodological appendix;
4. `docs/bib/original-report.pdf`: 2018 report, used for historical methodology, framing, and style;
5. pinned versions of legacy code and external references recorded in `docs/REFERENCE-FILES.md`.

Use the following authority order unless a task states otherwise:

1. validated data and metadata in this repository;
2. the methodological appendix and recorded methodology decisions;
3. the original report for historical interpretation and exposition;
4. primary official sources;
5. international organizations, peer-reviewed research, and established research institutions;
6. other reputable secondary sources, used only when the preceding sources are unavailable.

Do not silently reconcile conflicting values or definitions. Record the conflict in `docs/STATUS.md`, identify the competing sources, and state which definition is used and why. Do not replace a repository series with an external estimate without explicit authorization.

For first-draft writing, treat the two final workbooks as authoritative numerical outputs. Do not edit them manually. When a task concerns recalculation, trace the series to its source inputs and production code.

## Data and methodological guardrails

- Treat `data/raw/` as immutable. For every download, record the source institution, stable URL, access date, reference period, release or vintage, and checksum.
- Keep extraction, cleaning, construction, analysis, and graphing in separate stages. Production figures must not download data from the internet.
- Use repository-relative paths through `pathlib.Path`; never hard-code a local user path.
- Do not infer undocumented units, price bases, denominators, sheet meanings, geographic vintages, or missing-value conventions. Record them in `docs/DATA-DICTIONARY.md`.
- Distinguish observed, revised, provisional, imputed, interpolated, extrapolated, and model-based values. Never fill a missing observation silently.
- Use one explicit monetary convention in each result: nominal reais, constant reais with a documented base year and deflator, or percentage of GDP with a documented GDP series and vintage.
- Treat 2025 as the target terminal year, not as an assumption that complete 2025 data exist. When 2025 is unavailable or incomplete, use the latest complete common year, label it clearly, and do not mix terminal years inside an aggregate without an explicit method.
- Preserve the conceptual distinction between resource costs, public or private expenditures, transfers, insurance premiums or payouts, material losses, and estimated losses of productive capacity.
- Check for overlap and double counting across components. Document any overlap that the 2018 methodology intentionally retains.
- Before extending a historical series, reproduce the published values over the overlapping period or prepare a reconciliation table. Classify each revision as a source revision, conceptual revision, coding correction, classification change, price-base revision, geographic change, or imputation change.
- Use causal language only when supported by an identification strategy. Otherwise describe levels, changes, correlations, composition, and accounting contributions.
- Do not revise a substantive method merely to make a series smoother or a result more intuitive.

## Writing and citations

- Write report text in Brazilian Portuguese using a professional, economic, and policy-oriented tone.
- Explain methods in plain language without sacrificing precision.
- Every quantitative claim must be traceable to a table, figure, repository file, or external source.
- Format numbers for Brazilian readers and normally use at most one decimal place: `3,2%`, `R$ 125,4 bilhões`, and `18,7 por 100 mil habitantes`.
- Distinguish calculations by the authors from statistics reproduced from another institution.
- Use citation keys and the repository bibliography where available. Record complete ABNT-compatible metadata, including access dates for online sources. Prefer archived local copies or commit-specific links over mutable branch URLs.
- Do not invent citations, quotations, institutional positions, or explanations for unexplained data movements.
- Draft substantive sections first. Draft the conclusion after the results sections, the introduction after the conclusion, and the executive summary last.

## Code conventions

- Put reusable production code under `src/`; notebooks are for exploration and must not be the only source of a published result.
- Use one entry-point script per numbered figure under `src/figures/`, with shared formatting and validation helpers in common modules.
- At the top of each figure script, define a compact configuration block containing input paths, output paths, title, subtitle, source note, axis labels, display-label mappings, and figure-specific parameters.
- Keep raw variable names out of publication-facing labels.
- Make runs deterministic. Set a random seed whenever randomness is used.
- Fail loudly on missing columns, duplicate keys, impossible shares, unexpected year coverage, or missing geographic units.
- Do not make unrelated refactors or alter upstream data as a side effect of a writing or graphing task.

## Figure requirements

- Follow `docs/FIGURE-SPECS.md` and `docs/graphing-style.md`.
- Save each final figure as both `figs/fig_XX_slug.pdf` and `figs/fig_XX_slug.png`. Lettered companion versions may use `fig_02a_...` and `fig_02b_...`.
- Each figure must include a Portuguese title, subtitle, labeled axes, readable legend, units, and a source or method note.
- Use a shared visual style and an accessible palette. Do not encode essential distinctions by color alone.
- Prefer aligned panels to dual y-axes.
- Save a figure-ready CSV under `data/figure_data/` whenever feasible so every plotted value can be audited.
- After generating a figure, inspect the PNG visually; a successful script exit is not sufficient validation.

## Report integration

Use a non-executable placeholder while drafting:

```markdown
<!-- FIGURA 01: ../figs/fig_01_slug.pdf -->
```

Do not copy numerical values from a chart by eye. Generate prose statistics from the underlying table or figure-ready dataset.

## Validation

For every affected dataset, table, or figure, run the checks relevant to the task:

- expected years and geographic units are present;
- key fields are unique at their intended level;
- units, price bases, and denominators are consistent;
- component shares and totals satisfy their accounting identities within a documented tolerance;
- national and state files are not confused;
- missing, revised, imputed, or provisional observations are visible and documented;
- generated PDF and PNG files exist, are nonempty, and use the same figure-ready data;
- all statistics quoted in revised prose can be reproduced from a named source.

Use the setup, validation, figure, and report commands documented in `README.md`, `pyproject.toml`, or `Makefile`. If those interfaces do not yet exist, establish them before describing the pipeline as reproducible.

## Definition of done

A task is complete only when:

1. the requested files have been created or updated without unrelated changes;
2. relevant scripts and validation checks have run successfully;
3. generated outputs have been inspected;
4. sources, assumptions, methodological deviations, and unresolved issues are documented;
5. `docs/STATUS.md` reflects the new state of the project; and
6. the final response lists changed files, commands run, validation results, and remaining limitations.
