"""Figure 9: modeled loss of productive capacity due to homicides."""

from __future__ import annotations

from .common import COMPONENT_COLORS, FIGURE_DATA_DIR, NATIONAL_LONG_FIELDS, plot_two_panel_series, read_csv, write_csv
from .data_helpers import NATIONAL_WORKBOOK, index_by_year, make_component_rows, national_summary, require_number, sheet_records


CONFIG = {
    "input_file": NATIONAL_WORKBOOK,
    "sheet": "perdas_produtivas_br",
    "output_stem": "fig_09_perda_capacidade_produtiva",
    "data_file": FIGURE_DATA_DIR / "fig_09_productive_capacity.csv",
    "title": "Brasil: perda de capacidade produtiva por homicídios",
    "subtitle_template": "{start}–{end} | estimativa modelada de renda esperada perdida",
    "source_note": (
        "Fonte: Cálculos dos autores com SIM/DATASUS, PNAD Contínua 2025 e Tábua de Mortalidade "
        "IBGE 2024. Valores em reais de dezembro de 2025. Estimativa modelada do valor presente da "
        "renda esperada do trabalho, com crescimento real de 2%, desconto de 3% e horizonte até 90 anos; "
        "não é gasto observado nem valoração integral da vida. Em 2025, aplica o total agregado de 40.775 "
        "homicídios ao perfil idade–região de 2024. Ver Apêndice Metodológico."
    ),
    "axis_labels": ("R$ bilhões de dez./2025", "Percentual do PIB"),
    "display_labels": {"renda_total_perdida": "Perda de capacidade produtiva"},
    "component_order": ("Perda de capacidade produtiva",),
    "parameters": {"growth_rate": 0.02, "discount_rate": 0.03, "terminal_age": 90},
}


def prepare_data() -> list[dict[str, str]]:
    columns = ("ano", "total_de_homicidios", "renda_total_perdida")
    source = index_by_year(sheet_records(CONFIG["input_file"], CONFIG["sheet"], required_columns=columns, key_columns=("ano",)))
    summary = national_summary()
    rows: list[dict[str, object]] = []
    for year in sorted(source):
        value = require_number(source[year]["renda_total_perdida"], context=f"productive loss {year}")
        rows.extend(make_component_rows(
            year=year,
            components={"Perda de capacidade produtiva": value},
            gdp=require_number(summary[year]["pib_deflacionado"], context=f"GDP {year}"),
            reported_total=require_number(summary[year]["perdas_produtivas"], context=f"productive summary {year}"),
            nature={"Perda de capacidade produtiva": "Perda modelada de renda esperada"},
        ))
    write_csv(CONFIG["data_file"], rows, NATIONAL_LONG_FIELDS)
    return read_csv(CONFIG["data_file"])


def main() -> int:
    rows = prepare_data()
    years = sorted({int(row["ano"]) for row in rows})
    plot_two_panel_series(
        rows,
        title=CONFIG["title"],
        subtitle=CONFIG["subtitle_template"].format(start=min(years), end=max(years)),
        source_note=CONFIG["source_note"],
        series_label="Perda modelada",
        color=COMPONENT_COLORS["Perda de capacidade produtiva"],
        modeled=True,
        output_stem=CONFIG["output_stem"],
        data_path=CONFIG["data_file"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

