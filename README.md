# Custos Econômicos da Criminalidade no Brasil

This repository supports the update of the 2018 report *Custos Econômicos da Criminalidade no Brasil*.

## Current contents

- `AGENTS.md`: durable repository-wide instructions;
- `data/output/`: current national and state final workbooks;
- `docs/appendix.docx`: editable source of the methodological appendix;
- `docs/appendix.md`: reproducibly generated methodological appendix, with TeX notation;
- `docs/appendix.pdf`: prior standalone rendering of the methodological appendix;
- `docs/bib/original-report.pdf`: 2018 report;
- `docs/REPORT-SPEC.md`: report structure and drafting sequence;
- `docs/FIGURE-SPECS.md`: analytical specifications for Figures 1–15;
- `docs/DATA-DICTIONARY.md`: workbook and variable metadata;
- `docs/METHODOLOGY-DECISIONS.md`: decision log;
- `docs/STATUS.md`: current progress and open issues.

## Working principles

- Do not edit the final workbooks manually.
- Use the final workbooks as numerical ground truth; use the 2018 report as a conceptual benchmark and investigate only material or mechanically suspicious differences.
- Document units, price bases, denominators, vintages, imputations, and breaks in series.
- Distinguish expenditures, transfers, material losses, and model-based losses.
- Generate published results through reusable code and retain figure-ready data.

## Reproducible commands

Create the local Python environment once and install the pinned runtime
dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

All commands below may then be run with `.\.venv\Scripts\python.exe` in place
of `python`. The virtual environment is intentionally excluded from Git.

Validate the two final workbooks from the repository root:

```powershell
python -m src.validation.validate_data
python -m src.validation.validate_data --json-out data/audit/workbook_validation.json
```

The validator has no third-party Python dependency. It exits with status 1 when it finds a genuine mechanical inconsistency and reports economically ambiguous or explicitly deferred matters as warnings. The current workbooks return status 0; the national–UF MP and productive-loss discrepancies are non-blocking warnings that require upstream updates or pre-publication review. See `docs/STATUS.md`.

Acquire and retain the official SIM/IBGE inputs for Figures 3–5 once (these three commands require internet access):

```powershell
python -B -m src.data.download_sim_homicides
python -B -m src.data.download_ibge_population
python -B -m src.data.download_ibge_geography
```

Each acquisition is versioned and checksum-recorded in `data/raw/source_manifest.json`; an existing retained vintage is verified and never overwritten silently. Once those raw files are local, rebuild the microrregion data and Figures 3–5 without internet access:

```powershell
python -B -m src.data.build_microrregion_homicides
python -B -m src.validation.validate_homicide_data --data-only
python -B -m src.figures.build_homicide_figures
```

The final command builds both PDF/PNG outputs and figure-ready CSVs, then runs full homicide/figure validation. Individual figure entry points are also available:

```powershell
python -B -m src.figures.fig_03_microrregion_homicides
python -B -m src.figures.fig_04_microrregion_homicide_change
python -B -m src.figures.fig_05_microrregion_homicide_convergence
python -B -m src.validation.validate_homicide_data
```

Figure 5 uses the retained Figure 4 endpoints. It plots the 2016
rate against the absolute 2016–2024 rate change, sizes bubbles by 2016 population, and records
unweighted, population-weighted and endpoint-smoothed results under `data/audit/`.

Build Figures 6–15 from the repository root after installing `requirements.txt`:

```powershell
.\.venv\Scripts\python.exe -B -m src.figures.build_local_figures
```

The build writes the publication-facing CSVs to `data/figure_data/`, PDF and PNG outputs to
`figs/`, updates the output manifest, and runs the figure-specific checks. A validation-only run is:

```powershell
python -B -m src.figures.validate_figures
```

Each figure can also be rebuilt independently, for example:

```powershell
python -B -m src.figures.fig_06_public_security
```

Acquire and retain the official Sinesp, IBGE UF-population and UNODC inputs for Figures 1 and
2A–2D once (internet access is required only for these acquisition commands):

```powershell
python -B -m src.data.download_sinesp
python -B -m src.data.download_ibge_population_uf
python -B -m src.data.download_unodc_homicides
```

Rebuild the external-data figures from the retained raw vintages, without downloading:

```powershell
python -B -m src.data.build_sinesp_panel
python -B -m src.figures.fig_02_crime_trends
python -B -m src.data.build_unodc_homicide_panel
python -B -m src.figures.fig_01_world_homicides
python -B -m src.validation.validate_external_figures
```

The combined offline entry point performs the same build and validation sequence:

```powershell
python -B -m src.figures.build_external_figures
```

The workbook-production pipelines have not yet been recovered. Figures 1–5 are reproducible from
retained official raw inputs, and Figures 6–15 are reproducible from the final workbooks. The entire
report must not be described as reproducible from raw inputs until the workbook-producing interfaces
also run successfully from a clean environment.

Recalculate the quantitative ledger for report Sections 3–5 and verify the draft's numerical claims:

```powershell
python -B -m src.validation.validate_report_sections_3_5 --check-draft
```

This standard-library-only check writes `data/audit/report_sections_3_5_claims.csv` and fails if a
decimal value in the drafted sections cannot be reconciled with the figure-ready data. It also checks
the state rankings, trajectory groups and national component ordering used in the prose.

Validate the complete first draft, all figure placeholders and the source-attribution audit:

```powershell
python -B -m src.validation.validate_report
```

This command reuses the quantitative ledger, checks every decimal rendering in Sections 1–6,
confirms that Figures 1–15 are introduced and have nonempty PDF/PNG outputs, rejects drafting
artifacts and raw variable names, and writes `data/audit/report_headline_statistics.csv` and
`data/audit/report_citation_audit.csv`.

Regenerate the Markdown appendix from its editable DOCX source:

```powershell
python -B -m src.report.convert_appendix
```

Compile the report and methodological appendix, including figure placeholders, Markdown
footnotes, tables and TeX equations, with XeLaTeX:

```powershell
python -B -m src.report.build_report
```

The command writes the combined review copy to `docs/report.pdf` and retains the generated TeX
and XeLaTeX logs under `build/report/` for diagnosis.

Generate the corresponding editable Word review draft:

```powershell
python -B -m src.report.build_word
```

This command requires Microsoft Word for Windows. It writes `docs/report.docx`, embeds the 18
figures and 57 typeset appendix equations, creates native Word footnotes, and exports a diagnostic
PDF under `build/report/` for visual inspection.

Build the parallel English figure set, PDF, and Word report from the same
retained analytical data:

```powershell
.\.venv\Scripts\python.exe -B -m src.figures.build_english_figures
.\.venv\Scripts\python.exe -B -m src.report.build_report --language en
.\.venv\Scripts\python.exe -B -m src.report.build_word --language en
```

The English report is written to `docs/report-en.md`, `docs/report-en.pdf`, and
`docs/report-en.docx`; parallel figure CSVs are under `data/figure_data/en/`.
The full 57-equation methodological appendix remains incorporated in the
Portuguese edition and is not silently mixed into the English publication.

Assemble and test the bilingual static hotsite:

```powershell
.\.venv\Scripts\python.exe -B -m src.site.build_site
.\.venv\Scripts\python.exe -m http.server 8765 --directory site
```

The website uses Portuguese by default, provides an English toggle, serves all
18 interactive visualizations from the exact retained CSVs, and exposes report
and data downloads. A push to `main` triggers `.github/workflows/pages.yml`,
which uploads `site/` to GitHub Pages.
