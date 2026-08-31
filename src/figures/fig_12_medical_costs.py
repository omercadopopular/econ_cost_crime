"""Figure 12: hospital and temporary productive costs of violent injuries."""

from __future__ import annotations

from .common import COMPONENT_COLORS, FIGURE_DATA_DIR, NATIONAL_LONG_FIELDS, plot_two_panel_series, read_csv, write_csv
from .data_helpers import NATIONAL_WORKBOOK, index_by_year, make_component_rows, national_summary, require_number, sheet_records


CONFIG = {
    "input_file": NATIONAL_WORKBOOK,
    "sheet": "servicos_medicos_br",
    "output_stem": "fig_12_custos_medico_terapeuticos",
    "data_file": FIGURE_DATA_DIR / "fig_12_medical_costs.csv",
    "title": "Figura 12. Brasil: custos médico-terapêuticos da violência",
    "subtitle_template": "{start}–{end} | internações no SUS e perda produtiva durante a permanência",
    "source_note": (
        "Fonte: Cálculos dos autores com microdados do SIH/SUS e perfis de renda da PNAD Contínua 2025. "
        "Valores em reais de dezembro de 2025. A medida soma o valor das AIHs por agressão e a perda "
        "produtiva temporária dos dias de internação não fatal; exclui atendimento ambulatorial, rede privada "
        "e afastamento após a alta. 1996–1997 reproduzem 1998; há imputações mensais documentadas."
    ),
    "axis_labels": ("R$ bilhões de dez./2025", "Percentual do PIB"),
    "display_labels": {"gasto_total": "Serviços médico-terapêuticos"},
    "component_order": ("Serviços médico-terapêuticos",),
    "parameters": {"coverage": "SIH/SUS", "imputed_years": (1996, 1997)},
}


def prepare_data() -> list[dict[str, str]]:
    source = index_by_year(sheet_records(
        CONFIG["input_file"], CONFIG["sheet"],
        required_columns=("ano", "internacoes_agressao", "gasto_total"), key_columns=("ano",)
    ))
    summary = national_summary()
    rows: list[dict[str, object]] = []
    for year in sorted(source):
        value = require_number(source[year]["gasto_total"], context=f"medical total {year}")
        component_rows = make_component_rows(
            year=year,
            components={"Serviços médico-terapêuticos": value},
            gdp=require_number(summary[year]["pib_deflacionado"], context=f"GDP {year}"),
            reported_total=require_number(summary[year]["servicos_medicos"], context=f"medical summary {year}"),
            nature={"Serviços médico-terapêuticos": "Gasto hospitalar + perda temporária modelada"},
        )
        for row in component_rows:
            raw_admissions = source[year]["internacoes_agressao"]
            row["internacoes_agressao"] = "" if raw_admissions in (None, "", "-") else require_number(
                raw_admissions, context=f"violent-injury admissions {year}"
            )
        rows.extend(component_rows)
    write_csv(CONFIG["data_file"], rows, (*NATIONAL_LONG_FIELDS, "internacoes_agressao"))
    return read_csv(CONFIG["data_file"])


def main() -> int:
    rows = prepare_data()
    years = sorted({int(row["ano"]) for row in rows})
    plot_two_panel_series(
        rows,
        title=CONFIG["title"],
        subtitle=CONFIG["subtitle_template"].format(start=min(years), end=max(years)),
        source_note=CONFIG["source_note"],
        series_label="Custo hospitalar e perda temporária",
        color=COMPONENT_COLORS["Serviços médico-terapêuticos"],
        modeled=False,
        output_stem=CONFIG["output_stem"],
        data_path=CONFIG["data_file"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
