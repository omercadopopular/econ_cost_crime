# Graphing style

**Status:** Audited against selected figures in `docs/bib/original-report.pdf` and the pinned historical template in `docs/REFERENCE-FILES.md`.

## Visual hierarchy

- Use a concise Portuguese title stating the object and geography.
- Use a subtitle for period, unit, and the comparison being made.
- Put the source and essential method note below the plotting area.
- Keep backgrounds, gridlines, and borders unobtrusive.
- Use readable type at the final report dimensions; do not rely on notebook-scale viewing.
- Apply one consistent font family and sizing hierarchy across all figures, subject to repository licensing and portability.
- Preserve the useful hierarchy of the 2018 publication and its historical notebook: white
  background, bold left-aligned title, explanatory subtitle, compact legend above the data,
  prominent horizontal reference grid, and a separate source/method note below the plot.

## Axes and units

- Label every axis and state units explicitly.
- Use Brazilian number formatting in tick labels.
- Start bar-chart axes at zero unless a clearly documented analytical reason requires otherwise.
- Use bars for annual cost series, with every year printed and rotated 90 degrees. This follows
  the principal historical cost figures and makes each annual observation explicit.
- Prefer aligned panels to dual y-axes.
- Keep comparable panels on common scales when that aids comparison; when scales differ, label them clearly rather than forcing visual equivalence.
- Avoid unnecessary scientific notation.

## Color and encodings

- Use a restrained, colorblind-accessible palette.
- Do not encode an essential distinction by color alone; combine color with line style, marker, direct label, or panel structure.
- Use a stable component-to-color mapping across Figures 6–14.
- For change maps, use a diverging scale centered at zero and a distinct missing-data treatment.
- Bubble charts must map magnitude to marker area, not radius.

## Labels and legends

- Map all internal variable names to publication-quality Portuguese.
- Prefer direct labels when they remain legible.
- Order legend entries to match stack, line, or panel order.
- Use UF abbreviations consistently and manage overlap explicitly.
- Do not use unexplained acronyms.

## Layout and output

- Design for the report page before exporting.
- Use tight but non-crowded spacing and reserve room for source notes.
- Export vector PDF and high-resolution PNG from the same figure object and data.
- Use transparent or white backgrounds consistently.
- Do not inherit the notebook's grey plotting background. Its `fivethirtyeight` conventions are
  adapted through hierarchy, grid, typography and spacing rather than copied literally.
- Save figure-ready data whenever feasible.
- Inspect the final PNG and PDF for clipping, unreadable labels, incorrect accents, broken glyphs, and inconsistent panel sizes.

## Source-note pattern

Use a concise pattern such as:

> Fonte: Cálculos dos autores com dados de [instituições/séries]. Valores em reais constantes de [ano-base], deflacionados por [índice], quando aplicável. Ver Apêndice Metodológico.

Add only figure-specific qualifications that materially affect interpretation.

## Historical references

The original report and historical notebook are references, not immutable templates. Preserve useful visual continuity, but do not reproduce obsolete formatting, low-resolution output, inaccessible colors, or ambiguous dual axes.
