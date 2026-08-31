"""Figure 9: insurance expenditures and material losses."""

from __future__ import annotations

from .common import FIGURE_DATA_DIR, NATIONAL_LONG_FIELDS, component_colors, plot_component_panels, read_csv, write_csv
from .data_helpers import NATIONAL_WORKBOOK, index_by_year, make_component_rows, national_summary, require_number, sheet_records


CONFIG = {
    "input_file": NATIONAL_WORKBOOK,
    "sheet": "seguros_&_danos_materiais_br",
    "output_stem": "fig_09_seguros_perdas_materiais",
    "data_file": FIGURE_DATA_DIR / "fig_09_insurance_material_losses.csv",
    "title": "Figura 9. Brasil: seguros e perdas materiais",
    "subtitle_template": "{start}–{end} | cenário contábil amplo",
    "source_note": (
        "Fonte: Cálculos dos autores com dados mensais do SES/Susep, FBSP, SSP-SP, ISP-RJ, AutoSeg/Susep "
        "e IBGE. Valores em reais de dezembro de 2025, corrigidos pelo IPCA. O cenário amplo combina "
        "prêmios diretos, sinistros patrimoniais/de carga e perdas de veículos não recuperados; esses objetos "
        "têm interpretações distintas e podem se sobrepor. Ver Apêndice Metodológico."
    ),
    "axis_labels": ("R$ bilhões de dez./2025", "Percentual do PIB", "Percentual do total"),
    "display_labels": {
        "seguro_automotivo_deflaciodo": "Prêmios — automóveis",
        "seguro_patrimonial_deflaciodo": "Prêmios — patrimônio",
        "seguro_transporte_carga_deflaciodo": "Prêmios — transporte e carga",
        "perda_patrimonial_deflaciodo": "Perdas — patrimônio",
        "perda_transporte_carga_deflaciodo": "Perdas — transporte e carga",
        "perda_automobilista_deflaciodo": "Perdas — veículos",
    },
    "component_order": (
        "Prêmios — automóveis", "Prêmios — patrimônio", "Prêmios — transporte e carga",
        "Perdas — patrimônio", "Perdas — transporte e carga", "Perdas — veículos",
    ),
    "parameters": {"scenario": "amplo", "aggregation": "monthly_to_annual"},
}


def prepare_data() -> list[dict[str, str]]:
    columns = ("ano", "cerio", "gasto_total", *CONFIG["display_labels"].keys())
    source_records = sheet_records(CONFIG["input_file"], CONFIG["sheet"], required_columns=columns, key_columns=("ano", "cerio"))
    source = index_by_year(record for record in source_records if record["cerio"] == CONFIG["parameters"]["scenario"])
    summary = national_summary()
    rows: list[dict[str, object]] = []
    for year in sorted(source):
        components = {
            label: require_number(source[year][raw], context=f"{raw} {year}")
            for raw, label in CONFIG["display_labels"].items()
        }
        nature = {
            label: ("Prêmio de seguro" if label.startswith("Prêmios") else "Perda material/sinistro")
            for label in components
        }
        rows.extend(make_component_rows(
            year=year,
            components=components,
            gdp=require_number(summary[year]["pib_deflacionado"], context=f"GDP {year}"),
            reported_total=require_number(source[year]["gasto_total"], context=f"insurance total {year}"),
            nature=nature,
        ))
    write_csv(CONFIG["data_file"], rows, NATIONAL_LONG_FIELDS)
    return read_csv(CONFIG["data_file"])


def main() -> int:
    rows = prepare_data()
    years = sorted({int(row["ano"]) for row in rows})
    plot_component_panels(
        rows,
        component_order=CONFIG["component_order"],
        colors=component_colors(CONFIG["component_order"], "insurance"),
        title=CONFIG["title"],
        subtitle=CONFIG["subtitle_template"].format(start=min(years), end=max(years)),
        source_note=CONFIG["source_note"],
        output_stem=CONFIG["output_stem"],
        data_path=CONFIG["data_file"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
