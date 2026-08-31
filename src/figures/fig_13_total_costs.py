"""Figure 13: national accounting total and its seven components."""

from __future__ import annotations

from .common import COMPONENT_COLORS, FIGURE_DATA_DIR, NATIONAL_LONG_FIELDS, plot_component_panels, read_csv, write_csv
from .data_helpers import make_component_rows, national_summary, require_number


CONFIG = {
    "input_file": "data/output/tabela_final_cec_brasil.xlsx",
    "sheet": "custo_total_violencia",
    "output_stem": "fig_13_custos_economicos_criminalidade",
    "data_file": FIGURE_DATA_DIR / "fig_13_total_costs.csv",
    "title": "Figura 13. Brasil: custos econômicos medidos da criminalidade",
    "subtitle_template": "{start}–{end} | total contábil, participação no PIB e percentual do total",
    "source_note": (
        "Fonte: Cálculos dos autores a partir das séries finais do projeto. Valores em reais de dezembro de "
        "2025. O agregado contábil combina gastos públicos e privados, transferência previdenciária, prêmios "
        "e sinistros de seguros, perdas materiais e perdas produtivas modeladas, com possíveis sobreposições; "
        "não é uma estimativa causal de perda de bem-estar. Em 2025, a perda produtiva nacional usa o total "
        "agregado de homicídios e o perfil idade–região de 2024."
    ),
    "axis_labels": ("R$ bilhões de dez./2025", "Percentual do PIB", "Percentual do total"),
    "display_labels": {
        "servicos_medicos": "Serviços médico-terapêuticos",
        "encarceramento": "Encarceramento e auxílio-reclusão",
        "processos_judiciais": "Custos judiciais",
        "perdas_produtivas": "Perda de capacidade produtiva",
        "seguros_&_danos_materiais": "Seguros e perdas materiais",
        "seguranca_privada": "Segurança privada",
        "seguranca_publica": "Segurança pública",
    },
    "component_order": (
        "Serviços médico-terapêuticos", "Encarceramento e auxílio-reclusão", "Custos judiciais",
        "Perda de capacidade produtiva", "Seguros e perdas materiais", "Segurança privada", "Segurança pública",
    ),
    "parameters": {"currency_tolerance_brl": 2.0, "percentage_tolerance_pp": 1e-8},
}


NATURE = {
    "Serviços médico-terapêuticos": "Gasto hospitalar + perda temporária modelada",
    "Encarceramento e auxílio-reclusão": "Gasto público + transferência previdenciária",
    "Custos judiciais": "Despesa atribuída + serviço jurídico valorado",
    "Perda de capacidade produtiva": "Perda modelada de renda esperada",
    "Seguros e perdas materiais": "Prêmios, sinistros e perdas materiais",
    "Segurança privada": "Custo do trabalho privado",
    "Segurança pública": "Gasto público",
}


def prepare_data() -> list[dict[str, str]]:
    summary = national_summary()
    rows: list[dict[str, object]] = []
    for year in sorted(summary):
        record = summary[year]
        components = {
            label: require_number(record[raw], context=f"{raw} {year}")
            for raw, label in CONFIG["display_labels"].items()
        }
        rows.extend(make_component_rows(
            year=year,
            components=components,
            gdp=require_number(record["pib_deflacionado"], context=f"GDP {year}"),
            reported_total=require_number(record["custo_total_violencia"], context=f"reported total {year}"),
            nature=NATURE,
        ))
    write_csv(CONFIG["data_file"], rows, NATIONAL_LONG_FIELDS)
    return read_csv(CONFIG["data_file"])


def main() -> int:
    rows = prepare_data()
    years = sorted({int(row["ano"]) for row in rows})
    plot_component_panels(
        rows,
        component_order=CONFIG["component_order"],
        colors=[COMPONENT_COLORS[label] for label in CONFIG["component_order"]],
        title=CONFIG["title"],
        subtitle=CONFIG["subtitle_template"].format(start=min(years), end=max(years)),
        source_note=CONFIG["source_note"],
        output_stem=CONFIG["output_stem"],
        data_path=CONFIG["data_file"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
