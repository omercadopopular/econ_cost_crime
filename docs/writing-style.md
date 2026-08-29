# Writing style

**Status:** Initial project standard. Refine this file after a systematic style audit of `docs/bib/original-report.pdf`; do not claim that audit has occurred until it has.

## Language and audience

- Write in Brazilian Portuguese for readers familiar with public policy but not necessarily with the underlying data systems.
- Use direct, analytical prose. Prefer short paragraphs organized around one claim.
- Define technical or institutional terms at first use.
- Avoid slogans, moralizing language, and unsupported claims of causality.
- Use “custos econômicos mensurados” or another precise accounting term when “custos sociais” would imply a broader welfare concept.

## Recommended paragraph structure

For empirical results, use:

1. claim or comparison;
2. magnitude and reference period;
3. source or construction;
4. interpretation;
5. limitation or comparability qualification when material.

For methodological passages, use:

1. object being measured;
2. source data;
3. transformation or valuation;
4. economic interpretation;
5. limitation.

## Numbers and terminology

- Use Brazilian number formatting and normally one decimal place.
- Use `R$ X bilhões`, `% do PIB`, and `por 100 mil habitantes` consistently.
- State whether reais are nominal or constant and give the base year.
- Use `PIB per capita` when the variable is GDP per capita; do not relabel it as household income.
- Distinguish `homicídios registrados`, `mortes por agressão`, and other mortality or police-report concepts.
- Distinguish expenditures, transfers, premiums or claims, material losses, and modeled income losses.

## Claims and evidence

- Put the source close to the claim it supports.
- Do not infer motives or mechanisms from descriptive trends.
- Do not explain a discontinuity until the source, method, and coverage have been checked.
- Separate source-derived facts, author calculations, and interpretation.
- Flag provisional observations and breaks in series in the main text when they affect the conclusion.

## Citations

- Use the repository bibliography and stable citation keys where available.
- Maintain ABNT-compatible metadata: author or institution, title, publication, place or publisher when applicable, year, stable URL, and access date.
- Cite the original report when reproducing its framework or historical estimates.
- Prefer primary official sources over secondary summaries.
- Do not cite a mutable branch URL when a release, archive, or commit-specific link is available.

## Editing checklist

Before marking prose ready:

- every number is reproducible;
- periods and units are explicit;
- the subject of each comparison is unambiguous;
- causal language is justified or removed;
- the accounting interpretation is accurate;
- repeated methodological detail is cross-referenced rather than duplicated;
- headings and figure references match `docs/REPORT-SPEC.md` and `docs/FIGURE-SPECS.md`.
