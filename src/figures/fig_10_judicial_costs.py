"""Figure 10: crime-attributed costs in State Justice."""

from __future__ import annotations

from .common import FIGURE_DATA_DIR, NATIONAL_LONG_FIELDS, component_colors, plot_component_panels, read_csv, write_csv
from .data_helpers import NATIONAL_WORKBOOK, index_by_year, make_component_rows, national_summary, require_number, sheet_records


CONFIG = {
    "input_file": NATIONAL_WORKBOOK,
    "sheet": "processos_judiciais_br",
    "output_stem": "fig_10_custos_judiciais",
    "data_file": FIGURE_DATA_DIR / "fig_10_judicial_costs.csv",
    "title": "Brasil: custos judiciais associados à criminalidade",
    "subtitle_template": "{start}–{end} | Justiça Estadual, valores reais e percentual do total",
    "source_note": (
        "Fonte: Cálculos dos autores com dados do CNJ, CNMP e tabelas de honorários da OAB. Valores em "
        "reais de dezembro de 2025. Tribunais e Ministérios Públicos são despesas atribuídas à matéria "
        "criminal; serviços de defesa são valorados por casos novos e honorários normativos, não pelo "
        "orçamento das Defensorias. O eixo exclui a Justiça Federal e tribunais superiores. Ver Apêndice Metodológico."
    ),
    "axis_labels": ("R$ bilhões de dez./2025", "Percentual do PIB", "Percentual do total"),
    "display_labels": {
        "gastos_deflaciodos_tjs": "Tribunais de Justiça",
        "gastos_deflaciodos_mps": "Ministérios Públicos",
        "gastos_deflaciodos_defesa": "Serviços de defesa criminal",
    },
    "component_order": ("Tribunais de Justiça", "Ministérios Públicos", "Serviços de defesa criminal"),
    "parameters": {"institutional_scope": "Justiça Estadual"},
}


def prepare_data() -> list[dict[str, str]]:
    columns = ("ano", *CONFIG["display_labels"].keys())
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
            reported_total=require_number(summary[year]["processos_judiciais"], context=f"judicial total {year}"),
            nature={
                "Tribunais de Justiça": "Despesa pública atribuída",
                "Ministérios Públicos": "Despesa pública atribuída",
                "Serviços de defesa criminal": "Serviço jurídico valorado",
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
        colors=component_colors(CONFIG["component_order"], "justice"),
        title=CONFIG["title"],
        subtitle=CONFIG["subtitle_template"].format(start=min(years), end=max(years)),
        source_note=CONFIG["source_note"],
        output_stem=CONFIG["output_stem"],
        data_path=CONFIG["data_file"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
