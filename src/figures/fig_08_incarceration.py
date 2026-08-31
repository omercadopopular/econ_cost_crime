"""Figure 8: custody/reintegration expenditure and auxílio-reclusão."""

from __future__ import annotations

from .common import FIGURE_DATA_DIR, NATIONAL_LONG_FIELDS, component_colors, plot_component_panels, read_csv, write_csv
from .data_helpers import NATIONAL_WORKBOOK, index_by_year, make_component_rows, national_summary, require_number, sheet_records


CONFIG = {
    "input_file": NATIONAL_WORKBOOK,
    "sheet": "encarceramento_br",
    "output_stem": "fig_08_encarceramento_auxilio_reclusao",
    "data_file": FIGURE_DATA_DIR / "fig_08_incarceration.csv",
    "title": "Figura 8. Brasil: encarceramento e auxílio-reclusão",
    "subtitle_template": "{start}–{end} | valores reais, participação no PIB e percentual do total",
    "source_note": (
        "Fonte: Cálculos dos autores com dados do SIGA Brasil, STN/Siconfi, AEPS e BEPS. Valores em reais "
        "de dezembro de 2025, corrigidos pelo IPCA. Custódia e reintegração são despesas públicas líquidas "
        "das transferências federais identificadas às UFs; auxílio-reclusão é transferência previdenciária, "
        "mantida no total contábil. Ver Apêndice Metodológico."
    ),
    "axis_labels": ("R$ bilhões de dez./2025", "Percentual do PIB", "Percentual do total"),
    "display_labels": {
        "custodia_&_reintegracao_deflaciodo": "Custódia e reintegração social",
        "auxilio_reclusao_deflaciodo": "Auxílio-reclusão (transferência)",
    },
    "component_order": ("Custódia e reintegração social", "Auxílio-reclusão (transferência)"),
    "parameters": {"federal_transfer_modes_excluded": (30, 31)},
}


def prepare_data() -> list[dict[str, str]]:
    columns = ("ano", "custodia_&_reintegracao_deflaciodo", "auxilio_reclusao_deflaciodo")
    source = index_by_year(sheet_records(CONFIG["input_file"], CONFIG["sheet"], required_columns=columns, key_columns=("ano",)))
    summary = national_summary()
    rows: list[dict[str, object]] = []
    for year in sorted(source):
        components = {
            label: require_number(source[year][raw], context=f"{raw} {year}")
            for raw, label in CONFIG["display_labels"].items()
        }
        rows.extend(make_component_rows(
            year=year,
            components=components,
            gdp=require_number(summary[year]["pib_deflacionado"], context=f"GDP {year}"),
            reported_total=require_number(summary[year]["encarceramento"], context=f"incarceration total {year}"),
            nature={
                "Custódia e reintegração social": "Gasto público",
                "Auxílio-reclusão (transferência)": "Transferência previdenciária",
            },
        ))
    write_csv(CONFIG["data_file"], rows, NATIONAL_LONG_FIELDS)
    return read_csv(CONFIG["data_file"])


def main() -> int:
    rows = prepare_data()
    years = sorted({int(row["ano"]) for row in rows})
    plot_component_panels(
        rows,
        component_order=CONFIG["component_order"],
        colors=component_colors(CONFIG["component_order"], "incarceration"),
        title=CONFIG["title"],
        subtitle=CONFIG["subtitle_template"].format(start=min(years), end=max(years)),
        source_note=CONFIG["source_note"],
        output_stem=CONFIG["output_stem"],
        data_path=CONFIG["data_file"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
