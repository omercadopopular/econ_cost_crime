"""Figure 5: national public-security expenditure by government level."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from .common import (
    FIGURE_DATA_DIR,
    apply_project_style,
    br_tick,
    component_colors,
    decorate_figure,
    percent_tick,
    read_csv,
    save_figure,
    style_axis,
    write_csv,
)
from .data_helpers import (
    NATIONAL_WORKBOOK,
    assert_close,
    index_by_year,
    is_number,
    make_component_rows,
    national_summary,
    require_number,
    sheet_records,
)


CONFIG = {
    "input_file": NATIONAL_WORKBOOK,
    "sheet": "seguranca_publica_br",
    "output_stem": "fig_05_seguranca_publica",
    "data_file": FIGURE_DATA_DIR / "fig_05_public_security.csv",
    "title": "Brasil: gastos com segurança pública",
    "axis_labels": ("R$ bilhões de dez./2025", "Percentual do PIB", "Percentual do total"),
    "display_labels": {"uniao": "União", "ufs": "Estados e Distrito Federal", "municipios": "Municípios"},
    "component_order": ("União", "Estados e Distrito Federal", "Municípios"),
    "source_note_template": (
        "Fonte: Cálculos dos autores com dados da STN e do Fórum Brasileiro de Segurança Pública. "
        "Valores em reais de dezembro de 2025, corrigidos pelo IPCA. A decomposição por esfera está "
        "disponível no arquivo a partir de {decomposition_start}; o total nacional é mostrado antes disso sem rateio "
        "das parcelas. Tratamento de transferências entre esferas: PENDING. Ver Apêndice Metodológico."
    ),
    "parameters": {"preferred_start": 1996, "decomposition_rule": "todas as três parcelas numéricas"},
}


FIELDS = (
    "ano",
    "serie",
    "componente",
    "natureza_contabil",
    "valor_reais_dez_2025",
    "pib_reais_dez_2025",
    "participacao_pib_pct",
    "composicao_pct",
    "total_calculado_reais_dez_2025",
    "total_reportado_reais_dez_2025",
)


def prepare_data() -> list[dict[str, str]]:
    records = sheet_records(
        CONFIG["input_file"],
        CONFIG["sheet"],
        required_columns=("ano", "uniao", "ufs", "municipios", "gasto_total_deflaciodo"),
        key_columns=("ano",),
    )
    public = index_by_year(records)
    summary = national_summary()
    all_years = sorted(set(public) & set(summary))
    ano_final = max(
        year
        for year in all_years
        if is_number(public[year]["gasto_total_deflaciodo"])
        and is_number(summary[year]["pib_deflacionado"])
    )
    rows: list[dict[str, object]] = []
    for year in all_years:
        total = require_number(public[year]["gasto_total_deflaciodo"], context=f"public total {year}")
        gdp = require_number(summary[year]["pib_deflacionado"], context=f"GDP {year}")
        assert_close(total, float(summary[year]["seguranca_publica"]), context=f"public summary link {year}")
        rows.append(
            {
                "ano": year,
                "serie": "total",
                "componente": "Total",
                "natureza_contabil": "Gasto público",
                "valor_reais_dez_2025": total,
                "pib_reais_dez_2025": gdp,
                "participacao_pib_pct": 100.0 * total / gdp,
                "composicao_pct": 100.0,
                "total_calculado_reais_dez_2025": total,
                "total_reportado_reais_dez_2025": total,
            }
        )
        if all(is_number(public[year][field]) for field in ("uniao", "ufs", "municipios")):
            nominal = {
                CONFIG["display_labels"][field]: require_number(public[year][field], context=f"{field} {year}")
                for field in ("uniao", "ufs", "municipios")
            }
            nominal_total = sum(nominal.values())
            if nominal_total <= 0:
                raise ValueError(f"Non-positive public-security sphere total in {year}.")
            implied_factor = total / nominal_total
            real_components = {label: value * implied_factor for label, value in nominal.items()}
            component_rows = make_component_rows(
                year=year,
                components=real_components,
                gdp=gdp,
                reported_total=total,
                nature={label: "Gasto público" for label in real_components},
            )
            for row in component_rows:
                row["serie"] = "decomposição"
                rows.append(row)
    write_csv(CONFIG["data_file"], rows, FIELDS)
    loaded = read_csv(CONFIG["data_file"])
    if max(int(row["ano"]) for row in loaded) != ano_final:
        raise AssertionError("Terminal year changed during Figure 5 CSV round-trip.")
    return loaded


def plot(rows: list[dict[str, str]]) -> tuple[Path, Path]:
    apply_project_style()
    total_rows = sorted((row for row in rows if row["serie"] == "total"), key=lambda row: int(row["ano"]))
    component_rows = [row for row in rows if row["serie"] == "decomposição"]
    total_years = [int(row["ano"]) for row in total_rows]
    component_years = sorted({int(row["ano"]) for row in component_rows})
    order = CONFIG["component_order"]
    indexed = {(int(row["ano"]), row["componente"]): row for row in component_rows}
    colors = component_colors(order, "public")

    fig, axes = plt.subplots(3, 1, figsize=(11.7, 10.2), sharex=True)
    series_by_panel = []
    for field, scale in (("valor_reais_dez_2025", 1e9), ("participacao_pib_pct", 1.0), ("composicao_pct", 1.0)):
        series_by_panel.append(
            [[float(indexed[(year, label)][field]) / scale for year in component_years] for label in order]
        )
    panel_titles = ("A. Valores reais", "B. Participação no PIB", "C. Percentual do total")
    for ax, series, panel_title, ylabel in zip(axes, series_by_panel, panel_titles, CONFIG["axis_labels"]):
        bottom = [0.0] * len(component_years)
        for label, values, color in zip(order, series, colors):
            ax.bar(
                component_years,
                values,
                bottom=bottom,
                width=0.78,
                label=label,
                color=color,
                alpha=1.0,
                edgecolor="white",
                linewidth=0.35,
                zorder=2,
            )
            bottom = [base + value for base, value in zip(bottom, values)]
        ax.set_title(panel_title, loc="left", pad=7)
        ax.set_ylabel(ylabel)
        ax.set_xlim(min(total_years) - 0.6, max(total_years) + 0.6)
        ax.set_ylim(bottom=0)
        ax.yaxis.set_major_formatter(br_tick(1) if ax is axes[0] else percent_tick(1))
        style_axis(ax)
    axes[0].bar(
        total_years,
        [float(row["valor_reais_dez_2025"]) / 1e9 for row in total_rows],
        width=0.78,
        color="#D1D1D1",
        edgecolor="white",
        linewidth=0.35,
        label="Total sem decomposição",
        zorder=1,
    )
    axes[1].bar(
        total_years,
        [float(row["participacao_pib_pct"]) for row in total_rows],
        width=0.78,
        color="#D1D1D1",
        edgecolor="white",
        linewidth=0.35,
        label="Total sem decomposição",
        zorder=1,
    )
    axes[0].plot(
        total_years,
        [float(row["valor_reais_dez_2025"]) / 1e9 for row in total_rows],
        color="#111111",
        linewidth=2.0,
        label="Total",
        zorder=5,
    )
    axes[1].plot(
        total_years,
        [float(row["participacao_pib_pct"]) for row in total_rows],
        color="#111111",
        linewidth=2.0,
        label="Total",
        zorder=5,
    )
    axes[0].set_ylim(0, max(float(row["valor_reais_dez_2025"]) / 1e9 for row in total_rows) * 1.08)
    axes[1].set_ylim(0, max(float(row["participacao_pib_pct"]) for row in total_rows) * 1.08)
    axes[2].set_ylim(0, 100)
    axes[2].set_xlabel("Ano")
    axes[2].set_xticks(total_years)
    axes[2].tick_params(axis="x", labelrotation=90)
    if min(component_years) > min(total_years):
        axes[2].annotate(
            f"Decomposição por esfera disponível a partir de {min(component_years)}",
            xy=(min(component_years), 4),
            xytext=(min(total_years) + 0.5, 20),
            arrowprops={"arrowstyle": "->", "color": "#777777", "lw": 0.8},
            fontsize=8,
            color="#555555",
        )
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper left",
        bbox_to_anchor=(0.075, 0.915),
        ncol=5,
        frameon=False,
        handlelength=1.7,
        columnspacing=1.2,
    )
    subtitle = (
        f"{min(total_years)}–{max(total_years)} | total em todo o período; "
        f"percentuais por esfera desde {min(component_years)}"
    )
    decorate_figure(
        fig,
        title=CONFIG["title"],
        subtitle=subtitle,
        source_note=CONFIG["source_note_template"].format(decomposition_start=min(component_years)),
    )
    fig.subplots_adjust(left=0.10, right=0.985, top=0.855, bottom=0.14, hspace=0.34)
    return save_figure(fig, output_stem=CONFIG["output_stem"], data_path=CONFIG["data_file"])


def main() -> int:
    rows = prepare_data()
    plot(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
