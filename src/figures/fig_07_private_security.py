"""Figure 7: formal and informal private-security costs."""

from __future__ import annotations

from .common import FIGURE_DATA_DIR, NATIONAL_LONG_FIELDS, component_colors, plot_component_panels, read_csv, write_csv
from .data_helpers import NATIONAL_WORKBOOK, index_by_year, make_component_rows, national_summary, require_number, sheet_records


CONFIG = {
    "input_file": NATIONAL_WORKBOOK,
    "sheet": "seguranca_privada_br",
    "output_stem": "fig_07_seguranca_privada",
    "data_file": FIGURE_DATA_DIR / "fig_07_private_security.csv",
    "title": "Figura 7. Brasil: gastos com segurança privada",
    "subtitle_template": "{start}–{end} | valores reais, participação no PIB e percentual do total",
    "source_note": (
        "Fonte: Cálculos dos autores com dados da PNAD, PNAD Contínua/IBGE e Fenavist. Valores em reais "
        "de dezembro de 2025; a parcela formal incorpora multiplicador de custo do trabalho de 1,86. "
        "Há quebra de pesquisa e conceito em 2012; a passagem de preços médios para dezembro de 2025 "
        "permanece PENDING. Ver Apêndice Metodológico."
    ),
    "axis_labels": ("R$ bilhões de dez./2025", "Percentual do PIB", "Percentual do total"),
    "display_labels": {"formal": "Setor formal", "informal": "Provisão informal"},
    "component_order": ("Setor formal", "Provisão informal"),
    "parameters": {"pnad_break": 2012, "formal_multiplier": 1.86},
}


def prepare_data() -> list[dict[str, str]]:
    columns = (
        "ano", "custo_trabalho_formal_pnad_antiga", "custo_trabalho_formal_pnadc",
        "massa_salarial_informal_deflacionada_pnad_antiga", "massa_salarial_informal_deflacionada_pnadc",
    )
    source = index_by_year(sheet_records(CONFIG["input_file"], CONFIG["sheet"], required_columns=columns, key_columns=("ano",)))
    summary = national_summary()
    rows: list[dict[str, object]] = []
    for year in sorted(source):
        suffix = "pnad_antiga" if year <= 2011 else "pnadc"
        components = {
            "Setor formal": require_number(source[year][f"custo_trabalho_formal_{suffix}"], context=f"formal {year}"),
            "Provisão informal": require_number(source[year][f"massa_salarial_informal_deflacionada_{suffix}"], context=f"informal {year}"),
        }
        rows.extend(make_component_rows(
            year=year,
            components=components,
            gdp=require_number(summary[year]["pib_deflacionado"], context=f"GDP {year}"),
            reported_total=require_number(summary[year]["seguranca_privada"], context=f"private total {year}"),
            nature={label: "Custo do trabalho" for label in components},
        ))
    write_csv(CONFIG["data_file"], rows, NATIONAL_LONG_FIELDS)
    return read_csv(CONFIG["data_file"])


def main() -> int:
    rows = prepare_data()
    years = sorted({int(row["ano"]) for row in rows})
    plot_component_panels(
        rows,
        component_order=CONFIG["component_order"],
        colors=component_colors(CONFIG["component_order"], "private"),
        title=CONFIG["title"],
        subtitle=CONFIG["subtitle_template"].format(start=min(years), end=max(years)),
        source_note=CONFIG["source_note"],
        output_stem=CONFIG["output_stem"],
        data_path=CONFIG["data_file"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
