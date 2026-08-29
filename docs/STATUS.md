# Project status

**Updated:** 2026-08-29

## Current state

The repository contains the two final workbooks, the methodological appendix in PDF and DOCX formats, the 2018 report, and the initial report and figure specifications. The source-data and production-code pipeline has not yet been inventoried in this repository.

## Completed initialization

- Root repository instructions established.
- Report structure separated from persistent agent rules.
- Figure specifications separated and corrected.
- Core reference inventory initialized with pinned legacy-code links.
- Data-dictionary and methodology-decision templates established.
- Initial writing and graphing conventions established.
- Appendix filenames standardized.

## Priority next steps

| Priority | Task | Completion condition |
|---|---|---|
| 1 | Audit both final workbooks | Every sheet, key, variable, unit, price base, denominator, year, status flag, and identity is recorded in `docs/DATA-DICTIONARY.md` |
| 2 | Extract the methodological appendix | Every report component is mapped to source data, formula, imputation, and caveat |
| 3 | Reproduce the 2018 overlap | A reconciliation table explains every material difference between published and updated historical values |
| 4 | Establish source-data lineage | Each final series points to raw/interim inputs and production code; missing inputs are listed |
| 5 | Verify terminal years | 2025 completeness is assessed separately for workbooks, UNODC, Sinesp, SIM, GDP, and population |
| 6 | Build production interfaces | Reproducible validation, figure, and report commands are documented and tested |
| 7 | Produce Figures 1–14 | PDF, PNG, figure-ready data, source notes, and validation checks exist |
| 8 | Draft Sections 3–5 | All claims are reproducible and comparability limitations are explicit |

## Open risks

- Workbook schemas and formulas have not yet been independently validated.
- The relationship between the national total and the sum of UF estimates is unknown.
- The constant-price base, GDP vintage, and population vintage still require documentation.
- Some 2025 source series may be provisional or unavailable.
- Legacy code may not reproduce the published report without obsolete dependencies or unavailable source files.
- Transfers and potentially overlapping accounting components require explicit treatment in the aggregate.

## Working rule

Update this file after each substantive task. Move completed items to a dated completion record, retain unresolved limitations, and identify the next executable step rather than a general aspiration.
