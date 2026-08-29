# Custos Econômicos da Criminalidade no Brasil

This repository supports the update of the 2018 report *Custos Econômicos da Criminalidade no Brasil*.

## Current contents

- `AGENTS.md`: durable repository-wide instructions;
- `data/output/`: current national and state final workbooks;
- `docs/appendix.pdf`: methodological appendix;
- `docs/bib/original-report.pdf`: 2018 report;
- `docs/REPORT-SPEC.md`: report structure and drafting sequence;
- `docs/FIGURE-SPECS.md`: analytical specifications for Figures 1–14;
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

Validate the two final workbooks from the repository root:

```powershell
python -m src.validation.validate_data
python -m src.validation.validate_data --json-out data/audit/workbook_validation.json
```

The validator has no third-party Python dependency. It exits with status 1 when it finds a genuine mechanical inconsistency and reports economically ambiguous or explicitly deferred matters as warnings. The current workbooks return status 0; the national–UF MP and productive-loss discrepancies are non-blocking warnings that require upstream updates or pre-publication review. See `docs/STATUS.md`.

Install the pinned figure dependency and build Figures 5–14 from the repository root:

```powershell
python -m pip install -r requirements-figures.txt
python -B -m src.figures.build_local_figures
```

The build writes the publication-facing CSVs to `data/figure_data/`, PDF and PNG outputs to
`figs/`, updates the output manifest, and runs the figure-specific checks. A validation-only run is:

```powershell
python -B -m src.figures.validate_figures
```

Each figure can also be rebuilt independently, for example:

```powershell
python -B -m src.figures.fig_05_public_security
```

The source-data and workbook-production pipelines have not yet been recovered. Figures 5–14 are
reproducible from the final workbooks, but the repository must not be described as fully reproducible
from raw inputs until those upstream interfaces run successfully from a clean environment.
