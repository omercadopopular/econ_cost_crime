# Reference files

**Status date:** 2026-08-29

This file inventories the core materials. “Available” means only that the file or link exists; it does not mean that its schema, methodology, or historical consistency has been validated.

| Item | Path or pinned version | Role | Current status | Required next check |
|---|---|---|---|---|
| Original report | `docs/bib/original-report.pdf` | Historical estimates, framing, terminology, and visual reference | Available; systematic content/style audit pending | Record table and figure inventory, historical price base, cited sources, and claims to reproduce |
| National final workbook | `data/output/tabela_final_cec_brasil.xlsx` | National component series and aggregates | Available; schema audit pending | Inventory sheets, keys, years, units, formulas, missing values, and terminal-year completeness |
| State final workbook | `data/output/tabela_final_cec_ufs.xlsx` | UF-level component series and aggregates | Available; schema audit pending | Inventory sheets, 27-UF coverage, keys, years, units, formulas, and comparability across UFs |
| Methodological appendix | `docs/appendix.pdf` | Construction of each component | Available; structured method extraction pending | Map each output variable to source, formula, unit, deflator, coverage, and imputation |
| Editable appendix source | `docs/appendix.docx` | Source document for methodological revisions | Available | Confirm it is synchronized with the PDF before editing |
| Legacy crime-cost code | `https://github.com/omercadopopular/cgoes/tree/58a66930acf715a0999328dfdffc6fc1f92193ca/EconCostsViolenceBrazil` | Historical transformations and regional homicide workflow | Pinned reference; not yet validated against published outputs | Identify exact scripts used for each published result and record runtime dependencies |
| Legacy Sinesp code | `https://github.com/omercadopopular/cgoes/blob/58a66930acf715a0999328dfdffc6fc1f92193ca/sinesp/sinesp.py` | Starting point for reported-crime trends | Pinned reference; update required | Audit definitions, endpoints, coverage, and current Sinesp interface |
| Historical graph template | `https://github.com/omercadopopular/Modelos_Graficos/blob/b60f7cb3d0b2ef4c97cb665167ecdd6ffdcc0737/Histograma.ipynb` | Visual reference only | Pinned reference; style audit pending | Retain useful conventions but replace obsolete or inaccessible design choices |

## Source-use rules

- Before relying on a reference, record its release or vintage and whether it is primary, derived, or legacy material.
- Do not treat legacy scripts as authoritative when they conflict with the published report or current data. Reconcile the discrepancy.
- External sources used in the final report require complete bibliography metadata and an access date.
- When a remote source is essential for reproducibility, save an authorized local snapshot or record a stable archival or commit-specific link.
- Update this file when a new source becomes central to a calculation, figure, or claim.
