# Data dictionary

**Status:** initialization template. Workbook schemas have not yet been audited.

Do not infer any field below. Populate it from the workbook, methodological appendix, production code, or source metadata. Use `PENDING` until verified.

## Workbook inventory

| File | Sheet | Grain | Primary key | Year coverage | Geographic coverage | Monetary convention | Status |
|---|---|---|---|---|---|---|---|
| `data/output/tabela_final_cec_brasil.xlsx` | `PENDING` | National annual series (`PENDING`) | `PENDING` | `PENDING` | Brazil | `PENDING` | Schema audit pending |
| `data/output/tabela_final_cec_ufs.xlsx` | `PENDING` | UF-year series (`PENDING`) | `PENDING` | `PENDING` | 26 states and Federal District (`PENDING` verification) | `PENDING` | Schema audit pending |

Add one row per sheet after inspection.

## Variable-level fields

For every variable used in the report, record:

| Field | Required content |
|---|---|
| `workbook` | Repository-relative path |
| `sheet` | Exact sheet name |
| `variable` | Exact stored name |
| `display_label_ptbr` | Publication-quality Portuguese label |
| `concept` | Economic or accounting concept |
| `component` | Public security, private security, incarceration, insurance/material losses, productive capacity, judicial, medical-therapeutic, total, GDP, population, or other |
| `unit_stored` | Exact stored unit |
| `unit_display` | Intended figure/table unit |
| `price_basis` | Nominal or real; if real, base year |
| `deflator` | Series, source, vintage, and transformation |
| `denominator` | GDP, population, component total, aggregate total, or none |
| `geography` | Brazil, UF, municipality, fixed microrregion, or other |
| `geography_vintage` | Classification and crosswalk |
| `time_coverage` | First and last available years |
| `status_flags` | Observed, revised, provisional, imputed, interpolated, extrapolated, or model-based |
| `source` | Institution and source series |
| `construction` | Formula or code reference |
| `missing_rule` | Meaning and treatment of blank, zero, NA, or suppressed values |
| `validation` | Identity, range, or reconciliation checks |
| `notes` | Caveats, breaks, overlap, or conceptual distinctions |

## Mandatory denominator definitions

Before producing figures, document:

1. the GDP series and vintage used for national GDP shares;
2. the state GDP series and vintage used for UF GDP shares;
3. the population series and vintage used for rates and GDP per capita;
4. the deflator and base year used for constant reais;
5. whether “share of total” refers to a component total or the aggregate measured cost;
6. whether transfers and intergovernmental flows are gross or consolidated.

## Accounting identities

Record the exact formulas and numerical tolerance for:

- each component total;
- the aggregate national cost;
- the aggregate UF cost;
- component shares that should sum to 100%;
- any national total that should reconcile with the sum of UFs.

Do not assume that a national estimate must equal the sum of state estimates when their construction or coverage differs; document the intended relationship first.
