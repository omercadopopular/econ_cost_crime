"""Figure 14: arrows between 2016 and terminal-year UF levels."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from .common import FIGURE_DATA_DIR, annotate_repelled, apply_project_style, br_tick, decorate_figure, percent_tick, read_csv, save_figure, style_axis, write_csv
from .data_helpers import UF_CODES, UF_WORKBOOK, latest_complete_uf_year, require_number, uf_graph_records


CONFIG = {
    "input_file": UF_WORKBOOK,
    "sheet": "graficos_ufs",
    "output_stem": "fig_14_trajetoria_renda_custo_ufs",
    "data_file": FIGURE_DATA_DIR / "fig_14_state_trajectories.csv",
    "title": "UFs: trajetória da renda e do custo da criminalidade",
    "subtitle_template": "{start}–{end} | setas entre níveis; valores estaduais em revisão",
    "source_note": (
        "Fonte: Cálculos dos autores a partir da planilha final por UF. Eixo horizontal em PIB per capita real "
        "de dezembro de 2025; eixo vertical em percentual do PIB estadual. As setas descrevem trajetórias, não "
        "efeitos causais. Metadados de vintage de PIB/população permanecem PENDING. Resultados estaduais "
        "preliminares: perdas produtivas de 2025 e o conceito de encarceramento por UF serão revistos."
    ),
    "axis_labels": ("PIB per capita real (R$ mil de dez./2025)", "Custos medidos (% do PIB estadual)"),
    "display_labels": {"start": "2016", "end": "ANO_FINAL_UF"},
    "component_order": (),
    "parameters": {"start_year": 2016, "required_ufs": 27, "plot_levels": True},
}


FIELDS = (
    "uf",
    "ano",
    "ponto",
    "pib_estadual_reais_dez_2025",
    "populacao",
    "pib_per_capita_reais_dez_2025",
    "custo_total_reais_dez_2025",
    "custo_total_pib_pct",
    "status_ano",
)


def prepare_data() -> list[dict[str, str]]:
    required = ("pib_estadual", "populacao", "pib_per_capita", "custo_total_crime", "custo_total_%_pib")
    end_year = latest_complete_uf_year(required)
    start_year = CONFIG["parameters"]["start_year"]
    if end_year <= start_year:
        raise ValueError(f"Figure 14 needs an end year after {start_year}; found {end_year}.")
    source = [record for record in uf_graph_records() if int(record["ano"]) in {start_year, end_year}]
    keys = {(str(record["uf"]), int(record["ano"])) for record in source}
    expected = {(uf, year) for uf in UF_CODES for year in (start_year, end_year)}
    if keys != expected:
        raise ValueError(f"Figure 14 UF-year coverage mismatch: missing={sorted(expected - keys)}")

    rows: list[dict[str, object]] = []
    for record in sorted(source, key=lambda item: (str(item["uf"]), int(item["ano"]))):
        year = int(record["ano"])
        rows.append(
            {
                "uf": str(record["uf"]),
                "ano": year,
                "ponto": "início" if year == start_year else "fim",
                "pib_estadual_reais_dez_2025": require_number(record["pib_estadual"], context=f"GDP {record['uf']}-{year}"),
                "populacao": require_number(record["populacao"], context=f"population {record['uf']}-{year}"),
                "pib_per_capita_reais_dez_2025": require_number(record["pib_per_capita"], context=f"GDPpc {record['uf']}-{year}"),
                "custo_total_reais_dez_2025": require_number(record["custo_total_crime"], context=f"total {record['uf']}-{year}"),
                "custo_total_pib_pct": require_number(record["custo_total_%_pib"], context=f"share {record['uf']}-{year}"),
                "status_ano": "Preliminar: perdas produtivas UF e conceito de encarceramento em revisão",
            }
        )
    write_csv(CONFIG["data_file"], rows, FIELDS)
    return read_csv(CONFIG["data_file"])


def plot(rows: list[dict[str, str]]) -> tuple[Path, Path]:
    apply_project_style()
    years = sorted({int(row["ano"]) for row in rows})
    start_year, end_year = years
    indexed = {(row["uf"], int(row["ano"])): row for row in rows}
    ufs = sorted({row["uf"] for row in rows})

    start_x = [float(indexed[(uf, start_year)]["pib_per_capita_reais_dez_2025"]) / 1000.0 for uf in ufs]
    start_y = [float(indexed[(uf, start_year)]["custo_total_pib_pct"]) for uf in ufs]
    end_x = [float(indexed[(uf, end_year)]["pib_per_capita_reais_dez_2025"]) / 1000.0 for uf in ufs]
    end_y = [float(indexed[(uf, end_year)]["custo_total_pib_pct"]) for uf in ufs]

    fig, ax = plt.subplots(figsize=(11.7, 8.3))
    all_x = start_x + end_x
    all_y = start_y + end_y
    x_pad = (max(all_x) - min(all_x)) * 0.08
    y_pad = (max(all_y) - min(all_y)) * 0.12
    ax.set_xlim(max(0, min(all_x) - x_pad), max(all_x) + x_pad)
    ax.set_ylim(max(0, min(all_y) - y_pad), max(all_y) + y_pad)
    for sx, sy, ex, ey in zip(start_x, start_y, end_x, end_y):
        ax.annotate(
            "",
            xy=(ex, ey),
            xytext=(sx, sy),
            arrowprops={
                "arrowstyle": "-|>",
                "color": "#496A81",
                "lw": 1.0,
                "alpha": 0.62,
                "mutation_scale": 9,
                "shrinkA": 2,
                "shrinkB": 2,
            },
            zorder=2,
        )
    ax.scatter(start_x, start_y, marker="s", s=30, facecolor="white", edgecolor="#4D4D4D", linewidth=1.0, zorder=3)
    ax.scatter(end_x, end_y, marker="o", s=34, color="#D55E00", edgecolor="white", linewidth=0.6, zorder=4)
    annotate_repelled(ax, end_x, end_y, ufs, fontsize=7.0)
    ax.set_xlabel(CONFIG["axis_labels"][0])
    ax.set_ylabel(CONFIG["axis_labels"][1])
    ax.xaxis.set_major_formatter(br_tick(0))
    ax.yaxis.set_major_formatter(percent_tick(1))
    style_axis(ax)
    ax.legend(
        handles=[
            Line2D([0], [0], marker="s", color="none", markerfacecolor="white", markeredgecolor="#4D4D4D", label=str(start_year)),
            Line2D([0], [0], marker="o", color="none", markerfacecolor="#D55E00", markeredgecolor="white", label=str(end_year)),
            Line2D([0], [0], color="#496A81", marker=">", markevery=[1], label="Direção da trajetória"),
        ],
        loc="upper right",
        frameon=False,
        ncol=3,
    )
    decorate_figure(
        fig,
        title=CONFIG["title"],
        subtitle=CONFIG["subtitle_template"].format(start=start_year, end=end_year),
        source_note=CONFIG["source_note"],
    )
    fig.text(
        0.985,
        0.974,
        "RESULTADOS ESTADUAIS PRELIMINARES",
        ha="right",
        va="top",
        fontsize=8.2,
        fontweight="bold",
        color="#A65300",
    )
    fig.subplots_adjust(left=0.10, right=0.975, top=0.89, bottom=0.16)
    return save_figure(fig, output_stem=CONFIG["output_stem"], data_path=CONFIG["data_file"])


def main() -> int:
    rows = prepare_data()
    plot(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

