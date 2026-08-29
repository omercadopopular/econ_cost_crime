# Reference files

**Status date:** 2026-08-29

This file inventories the core materials. “Available” means only that the file or link exists. “Audited” records the scope of the checks performed; it does not establish missing upstream lineage.

| Item | Path or pinned version | Role | Current status | Required next check |
|---|---|---|---|---|
| Original report | `docs/bib/original-report.pdf` (76 pages) | Historical methodology, framing, terminology and visual reference; not a numerical target | Methodological sections and appendices audited; selected cost figures visually audited for the Figures 5–14 production system | A full table and prose-style inventory remains for later drafting tasks |
| National final workbook | `data/output/tabela_final_cec_brasil.xlsx`; SHA-256 `E9824EF3E77E184EB7BC9850694169CD84CFB30BDD91DA238CB615E9FE5D135A` | Authoritative national component series and aggregates | Eight sheets inventoried; 1996–2025; aggregate formula and 2025 productive-loss link corrected | Recover GDP metadata and upstream production lineage |
| State final workbook | `data/output/tabela_final_cec_ufs.xlsx`; SHA-256 `4815CC84EFDDAD1274F358336622ACBE1D7861D3F778FADCE09D9D8B0135C8C` | Authoritative UF-level component series and aggregates | Eleven sheets inventoried; relevant sheets contain all 27 UFs in 2016 e 2025; incarceration is propagated, `uf_sigla` has no `#NAME?`, and the AC–2025 homicide identity is corrected | Update productive-loss 2025 upstream; recover GDP/population metadata |
| Methodological appendix | `docs/appendix.pdf` (43 pages) | Construction of each component | Audited and mapped to output variables in `DATA-DICTIONARY.md` | Correct the claim that productive losses uniformly reach 2025; document the UF incarceration workbook method and missing denominator metadata |
| Editable appendix source | `docs/appendix.docx` | Source document for methodological revisions | Available | Confirm it is synchronized with the PDF before editing |
| Workbook validator | `src/validation/validate_data.py`; reader in `src/validation/workbook_reader.py` | Reproducible structural, numerical, identity and national–UF checks | Implemented and run; hard errors and economic warnings are separated | Rerun after upstream workbook regeneration until hard-error count is zero |
| Machine-readable audit | `data/audit/workbook_validation.json` | Hashes, sheet inventory, tolerances, reconciliation statistics and findings | Generated from the current workbooks | Regenerate with every workbook revision |
| Legacy crime-cost code | `https://github.com/omercadopopular/cgoes/tree/58a66930acf715a0999328dfdffc6fc1f92193ca/EconCostsViolenceBrazil` | Historical transformations and regional homicide workflow | Pinned reference; not yet validated against published outputs | Identify exact scripts used for each published result and record runtime dependencies |
| Legacy Sinesp code | `https://github.com/omercadopopular/cgoes/blob/58a66930acf715a0999328dfdffc6fc1f92193ca/sinesp/sinesp.py` | Starting point for reported-crime trends | Pinned reference; update required | Audit definitions, endpoints, coverage, and current Sinesp interface |
| Historical graph template | `https://github.com/omercadopopular/Modelos_Graficos/blob/b60f7cb3d0b2ef4c97cb665167ecdd6ffdcc0737/Histograma.ipynb` | Visual reference only | Pinned notebook audited: `fivethirtyeight`, strong horizontal grid, left-aligned title/subtitle, source note and institutional footer | The updated figures retain the hierarchy, grid and spacing on a white background and use the accessible project palette; legacy branding is not reproduced |

## Source-use rules

- Before relying on a reference, record its release or vintage and whether it is primary, derived, or legacy material.
- Do not treat legacy scripts as authoritative when they conflict with the current workbooks and recorded methodology. Use the 2018 publication to classify material conceptual changes, not to force point-estimate equality.
- External sources used in the final report require complete bibliography metadata and an access date.
- When a remote source is essential for reproducibility, save an authorized local snapshot or record a stable archival or commit-specific link.
- Update this file when a new source becomes central to a calculation, figure, or claim.
