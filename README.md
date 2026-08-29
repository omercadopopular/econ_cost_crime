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
- Reconcile updated historical values with the published 2018 estimates.
- Document units, price bases, denominators, vintages, imputations, and breaks in series.
- Distinguish expenditures, transfers, material losses, and model-based losses.
- Generate published results through reusable code and retain figure-ready data.

## Reproducible commands

The production pipeline has not yet been added. Once implemented, document a stable interface here, preferably:

```bash
make setup
make validate-data
make figures
make report
make check
```

Do not describe the repository as fully reproducible until these commands or equivalent interfaces run successfully from a clean environment.
