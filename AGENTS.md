# AGENTS.md

## Project purpose

This repository updates the 2018 report *Custos Econômicos da Criminalidade no Brasil*. The principal deliverable is `docs/report.md`, written in Brazilian Portuguese for a policy audience. The update should preserve comparability with the original report while documenting every methodological revision, source change, imputation, and break in the time series.

## Scope of this file

This file contains durable repository-wide rules only. Detailed report and figure requirements live in:

- `docs/REPORT-SPEC.md`: report structure, section order, and drafting sequence;
- `docs/FIGURE-SPECS.md`: specifications for Figures 1–14;
- `docs/REFERENCE-FILES.md`: inventory and summaries of core references;
- `docs/writing-style.md`: prose and citation conventions;
- `docs/graphing-style.md`: visual conventions;
- `docs/DATA-DICTIONARY.md`: workbook, sheet, variable, unit, and coverage definitions;
- `docs/METHODOLOGY-DECISIONS.md`: decisions that differ from, clarify, or extend the 2018 methodology;
- `docs/STATUS.md`: completed work, unresolved issues, missing sources, and next steps.

Read only the documents relevant to the current task. Do not rescan every PDF or external link on every run. When a required context document is missing or stale, create or update that document before modifying the associated deliverable.

## Authoritative inputs and source hierarchy

The core references are:

1. `data/output/tabela_final_cec_brasil.xlsx`: national time series;
2. `data/output/tabela_final_cec_ufs.xlsx`: state-level time series;
3. `docs/appendix.pdf`: methodological appendix;
4. `docs/bib/original-report.pdf`: original report, used for historical methodology, framing, and style;
5. pinned snapshots or commit-specific versions of the original code and other external source materials listed in `docs/REFERENCE-FILES.md`.

Use the following authority order unless the task states otherwise:

1. validated data and metadata in this repository;
2. the methodological appendix and recorded methodology decisions;
3. the original report for historical interpretation and exposition;
4. primary official sources;
5. international organizations, peer-reviewed research, and established research institutions.

Do not silently reconcile conflicting values or definitions. Record the conflict in `docs/STATUS.md`, identify the competing sources, and state which definition is used and why. Do not replace a repository series with an external estimate without explicit authorization.

For first-draft writing, treat the two final workbooks as authoritative outputs. Do not edit them manually. When a task concerns recalculation, trace the series to its source inputs and code instead.

## Data and methodological guardrails

- Treat `data/raw/` as immutable. Store downloads with source, URL, access date, reference period, and checksum.
- Keep extraction and cleaning separate from analysis and graphing. Production figures must not download data from the internet.
- Use repository-relative paths through `pathlib.Path`; never hard-code a local user path.
- Do not infer undocumented units, price bases, denominators, sheet meanings, or missing-value conventions. Add them to `docs/DATA-DICTIONARY.md`.
- Distinguish observed, revised, provisional, imputed, interpolated, extrapolated, and model-based values. Never fill missing observations silently.
- Define and apply one monetary convention consistently: nominal reais, constant reais with an explicit base year and deflator, or percentage of GDP with an explicit GDP series.
- Treat 2025 as the target terminal year unless the report specification is changed. When 2025 is unavailable or incomplete, use the latest complete observation and label it clearly; do not mix terminal years inside an aggregate without an explicit method.
- Preserve the conceptual distinction between resource costs, public or private expenditures, transfers, insured losses, and estimated losses of productive capacity. Do not describe an accounting total as a causal welfare effect without a defensible argument.
- Check for double counting across components and document any overlap that the original methodology intentionally retains.
- Before extending a historical series, reproduce the published historical values over the overlapping period or provide a reconciliation table explaining revisions.
- Use causal language only when supported by an identification strategy. Otherwise describe levels, changes, correlations, composition, and accounting contributions.

## Writing and citations

- Write report text in Brazilian Portuguese using a professional, economic, and policy-oriented tone.
- Explain methods in plain language without sacrificing precision.
- Every quantitative claim must be traceable to a table, figure, repository file, or external source.
- Format numbers for Brazilian readers and normally use at most one decimal place: for example, `3,2%`, `R$ 125,4 bilhões`, and `18,7 por 100 mil habitantes`.
- Distinguish clearly between calculations by the authors and statistics reproduced from another institution.
- Use citation keys and the repository bibliography where available. Record complete ABNT-compatible metadata, including access dates for online sources. Prefer archived local copies or stable, versioned links over mutable branch URLs.
- Do not invent citations, quotations, institutional positions, or explanations for unexplained data movements.
- Draft the substantive sections first. Draft the conclusion after the results sections, the introduction after the conclusion, and the executive summary last.

## Code conventions

- Put reusable production code under `src/`; notebooks are for exploration and must not be the only source of a published result.
- Use one entry-point script per numbered figure under `src/figures/`, with shared formatting and validation helpers in a common module.
- At the top of each figure script, define a compact configuration block containing input paths, output paths, title, subtitle, source note, axis labels, display-label mappings, and any figure-specific parameters.
- Keep raw variable names out of publication-facing labels.
- Make runs deterministic. Set a random seed whenever randomness is used.
- Fail loudly on missing columns, duplicate keys, impossible shares, unexpected year coverage, or missing geographic units.
- Do not make unrelated refactors or alter upstream data as a side effect of a writing or graphing task.

## Figure requirements

- Follow `docs/FIGURE-SPECS.md` and `docs/graphing-style.md`.
- Save each figure as both `figs/fig_XX_slug.pdf` and `figs/fig_XX_slug.png`.
- Each figure must include a Portuguese title, subtitle, labeled axes, readable legend, units, and a source/method note.
- Use a shared visual style and an accessible palette. Do not encode essential distinctions by color alone.
- Prefer separate panels to dual y-axes unless the figure specification explicitly requires a dual axis and the scales are unambiguous.
- When useful, save a figure-ready data file under `data/figure_data/` so every plotted value can be audited.
- After generating a figure, inspect the PNG visually; do not consider a successful script exit sufficient validation.

## Report integration

Use a simple, non-executable placeholder while drafting:

```markdown
<!-- FIGURA 01: ../figs/fig_01_slug.pdf -->
```

Do not copy numerical values from a chart by eye. Generate prose statistics from the underlying table or a figure-ready dataset.

## Validation

For every affected dataset, table, or figure, run the checks relevant to the task:

- expected years and geographic units are present;
- key fields are unique at their intended level;
- units and price bases are consistent;
- component shares and totals satisfy their accounting identities within a stated numerical tolerance;
- national and state files are not confused;
- missing or provisional observations are visible and documented;
- generated PDF and PNG files exist, are nonempty, and correspond to the same data;
- all statistics quoted in revised prose can be reproduced from a named source.

Use the setup, validation, figure, and report commands documented in `README.md`, `pyproject.toml`, or `Makefile`. If those interfaces do not yet exist, establish them before treating the pipeline as reproducible.

## Definition of done

A task is complete only when:

1. the requested files have been created or updated without unrelated changes;
2. relevant scripts and validation checks have run successfully;
3. generated outputs have been inspected;
4. sources, assumptions, methodological deviations, and unresolved issues are documented;
5. `docs/STATUS.md` reflects the new state of the project; and
6. the final response lists changed files, commands run, validation results, and any remaining limitations.
