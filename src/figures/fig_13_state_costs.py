"""Figure 13: cross-UF burden and composition in the latest complete year."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from .common import (
    COMPONENT_COLORS,
    FIGURE_DATA_DIR,
    annotate_repelled,
    apply_project_style,
    br_tick,
    decorate_figure,
    percent_tick,
    read_csv,
    save_figure,
    style_axis,
    write_csv,
)
from .data_helpers import (
    PERCENTAGE_TOLERANCE,
    UF_CODES,
    UF_WORKBOOK,
    assert_close,
    latest_complete_uf_year,
    require_number,
    uf_graph_records,
)


CONFIG = {
    "input_file": UF_WORKBOOK,
    "sheet": "graficos_ufs",
    "output_stem": "fig_13_custos_economicos_ufs",
    "data_file": FIGURE_DATA_DIR / "fig_13_state_costs.csv",
    "title": "UFs: nível e composição dos custos econômicos da criminalidade",
    "subtitle_template": "{year} | 27 UFs; valores estaduais em revisão",
    "source_note": (
        "Fonte: Cálculos dos autores a partir da planilha final por UF. PIB per capita e valores monetários "
        "em reais de dezembro de 2025; metadados de vintage de PIB e população permanecem PENDING. "
        "Resultados estaduais preliminares: o encarceramento usa construção distinta da nacional e as perdas "
        "produtivas de 2025 serão atualizadas; não comparar a soma das UFs ao total nacional sem essas ressalvas."
    ),
    "axis_labels": ("PIB per capita real (R$ mil de dez./2025)", "Custos medidos (% do PIB estadual)"),
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
    "parameters": {"required_ufs": 27, "currency_tolerance_brl": 2.0},
}


FIELDS = (
    "ano",
    "uf",
    "pib_estadual_reais_dez_2025",
    "populacao",
    "pib_per_capita_reais_dez_2025",
    "custo_total_reais_dez_2025",
    "custo_total_pib_pct",
    "componente",
    "valor_reais_dez_2025",
    "participacao_pib_pct",
    "composicao_total_pct",
    "status_ano",
)

SHARE_FIELDS = {
    "servicos_medicos": "servicos_medicos_%_pib",
    "encarceramento": "encarceramento_%_pib",
    "processos_judiciais": "processos_judiciais_%_pib",
    "perdas_produtivas": "perdas_produtivas_%_pib",
    "seguros_&_danos_materiais": "seguros_&_danos_materiais_%_pib",
    "seguranca_privada": "seguranca_privada_%_pib",
    "seguranca_publica": "seguranca_publica_%_pib",
}


def prepare_data() -> list[dict[str, str]]:
    numeric_fields = (
        "pib_estadual", "populacao", "pib_per_capita", "custo_total_crime", "custo_total_%_pib",
        *CONFIG["display_labels"].keys(), *SHARE_FIELDS.values(),
    )
    ano_final = latest_complete_uf_year(numeric_fields)
    source = [record for record in uf_graph_records() if int(record["ano"]) == ano_final]
    if {str(record["uf"]) for record in source} != UF_CODES:
        raise ValueError(f"Figure 13 does not contain all 27 UFs in {ano_final}.")

    rows: list[dict[str, object]] = []
    for record in sorted(source, key=lambda item: str(item["uf"])):
        uf = str(record["uf"])
        gdp = require_number(record["pib_estadual"], context=f"GDP {uf}-{ano_final}")
        population = require_number(record["populacao"], context=f"population {uf}-{ano_final}")
        gdp_pc = require_number(record["pib_per_capita"], context=f"GDPpc {uf}-{ano_final}")
        total = require_number(record["custo_total_crime"], context=f"total {uf}-{ano_final}")
        total_share = require_number(record["custo_total_%_pib"], context=f"total share {uf}-{ano_final}")
        assert_close(gdp_pc, gdp / population, context=f"GDPpc identity {uf}-{ano_final}", absolute=0.01)
        assert_close(total_share, 100.0 * total / gdp, context=f"total GDP share {uf}-{ano_final}", absolute=PERCENTAGE_TOLERANCE)

        components = {
            raw: require_number(record[raw], context=f"{raw} {uf}-{ano_final}")
            for raw in CONFIG["display_labels"]
        }
        assert_close(sum(components.values()), total, context=f"UF total identity {uf}-{ano_final}")
        for raw, value in components.items():
            stored_share = require_number(record[SHARE_FIELDS[raw]], context=f"{SHARE_FIELDS[raw]} {uf}-{ano_final}")
            assert_close(
                stored_share,
                100.0 * value / gdp,
                context=f"UF component GDP share {raw} {uf}-{ano_final}",
                absolute=PERCENTAGE_TOLERANCE,
            )
            rows.append(
                {
                    "ano": ano_final,
                    "uf": uf,
                    "pib_estadual_reais_dez_2025": gdp,
                    "populacao": population,
                    "pib_per_capita_reais_dez_2025": gdp_pc,
                    "custo_total_reais_dez_2025": total,
                    "custo_total_pib_pct": total_share,
                    "componente": CONFIG["display_labels"][raw],
                    "valor_reais_dez_2025": value,
                    "participacao_pib_pct": stored_share,
                    "composicao_total_pct": 100.0 * value / total,
                    "status_ano": "Preliminar: perdas produtivas UF e conceito de encarceramento em revisão",
                }
            )
    write_csv(CONFIG["data_file"], rows, FIELDS)
    return read_csv(CONFIG["data_file"])


def plot(rows: list[dict[str, str]]) -> tuple[Path, Path]:
    apply_project_style()
    year = int(rows[0]["ano"])
    order = CONFIG["component_order"]
    colors = [COMPONENT_COLORS[label] for label in order]
    indexed = {(row["uf"], row["componente"]): row for row in rows}
    base_by_uf = {row["uf"]: row for row in rows}
    ufs = sorted(base_by_uf)

    fig, (ax_scatter, ax_bars) = plt.subplots(
        2,
        1,
        figsize=(11.7, 15.2),
        gridspec_kw={"height_ratios": (1.0, 2.25)},
    )

    x = [float(base_by_uf[uf]["pib_per_capita_reais_dez_2025"]) / 1000.0 for uf in ufs]
    y = [float(base_by_uf[uf]["custo_total_pib_pct"]) for uf in ufs]
    ax_scatter.scatter(x, y, s=35, color="#0072B2", edgecolor="white", linewidth=0.8, zorder=3)
    x_pad = (max(x) - min(x)) * 0.08
    y_pad = (max(y) - min(y)) * 0.15
    ax_scatter.set_xlim(max(0, min(x) - x_pad), max(x) + x_pad)
    ax_scatter.set_ylim(max(0, min(y) - y_pad), max(y) + y_pad)
    ax_scatter.set_title("A. Renda estadual e peso dos custos medidos", loc="left", pad=8)
    ax_scatter.set_xlabel(CONFIG["axis_labels"][0])
    ax_scatter.set_ylabel(CONFIG["axis_labels"][1])
    ax_scatter.xaxis.set_major_formatter(br_tick(0))
    ax_scatter.yaxis.set_major_formatter(percent_tick(1))
    style_axis(ax_scatter)
    annotate_repelled(ax_scatter, x, y, ufs, fontsize=7.1)

    ordered_ufs = sorted(ufs, key=lambda uf: float(base_by_uf[uf]["custo_total_pib_pct"]))
    positions = list(range(len(ordered_ufs)))
    left = [0.0] * len(ordered_ufs)
    for label, color in zip(order, colors):
        values = [float(indexed[(uf, label)]["participacao_pib_pct"]) for uf in ordered_ufs]
        ax_bars.barh(
            positions,
            values,
            left=left,
            color=color,
            edgecolor="white",
            linewidth=0.35,
            height=0.76,
            label=label,
        )
        left = [base + value for base, value in zip(left, values)]
    totals = [float(base_by_uf[uf]["custo_total_pib_pct"]) for uf in ordered_ufs]
    ax_bars.scatter(totals, positions, marker="D", s=13, color="#111111", zorder=4, label="Total")
    for total, position in zip(totals, positions):
        ax_bars.text(total + 0.06, position, format(total, ".1f").replace(".", ","), va="center", fontsize=6.3)
    ax_bars.set_yticks(positions, ordered_ufs)
    ax_bars.set_xlim(0, max(totals) * 1.13)
    ax_bars.set_xlabel("Contribuição ao custo medido (percentual do PIB estadual)")
    ax_bars.set_title("B. Componentes do custo medido, ordenados pelo peso total", loc="left", pad=8)
    ax_bars.xaxis.set_major_formatter(percent_tick(1))
    style_axis(ax_bars, y_grid=False)
    ax_bars.grid(axis="x", color="#B7B7B7", linewidth=1.15, alpha=1.0)
    ax_bars.set_axisbelow(True)
    ax_bars.legend(loc="lower right", frameon=False, ncol=2, fontsize=7.3)

    decorate_figure(
        fig,
        title=CONFIG["title"],
        subtitle=CONFIG["subtitle_template"].format(year=year),
        source_note=CONFIG["source_note"],
        note_width=165,
    )
    fig.text(
        0.075,
        0.918,
        "RESULTADOS ESTADUAIS PRELIMINARES",
        ha="left",
        va="top",
        fontsize=8.2,
        fontweight="bold",
        color="#A65300",
    )
    fig.subplots_adjust(left=0.095, right=0.97, top=0.875, bottom=0.09, hspace=0.25)
    return save_figure(fig, output_stem=CONFIG["output_stem"], data_path=CONFIG["data_file"])


def main() -> int:
    rows = prepare_data()
    plot(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
