"""Figure 1: Brazil in the international homicide-rate distribution."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

from .common import (
    FIGURE_DATA_DIR,
    apply_project_style,
    br_tick,
    decorate_figure,
    format_br,
    percent_tick,
    save_figure,
    style_axis,
    write_csv,
)
from src.data.build_unodc_homicide_panel import (
    COMPARISON_YEARS,
    COUNTRY_COMPARISON_PATH,
)


CONFIG = {
    "input_file": COUNTRY_COMPARISON_PATH,
    "output_stem": "fig_01_distribuicao_mundial_homicidios",
    "data_file": FIGURE_DATA_DIR / "fig_01_distribuicao_mundial_homicidios.csv",
    "title": "Figura 1. Mundo: distribuição das taxas de homicídio",
    "subtitle": (
        "Taxas em 2016 e 2024 por país/território | distribuição não ponderada"
    ),
    "source_note": (
        "Fonte: Cálculos dos autores com dados do UNODC Data Portal, Intentional Homicide "
        "(versão de julho de 2026). Indicador: vítimas de homicídio intencional por 100 mil "
        "habitantes. Amostra comum de {sample_size} unidades oficiais de reporte país/território "
        "observadas nas duas datas; percentis por posto médio, sem ponderação "
        "populacional. A cobertura anual do UNODC chega a 95 unidades em 2024; não houve "
        "interpolação nem emenda com fonte nacional."
    ),
    "axis_labels": {
        "x": "Percentil entre países/territórios",
        "y": "Homicídios intencionais por 100 mil habitantes",
    },
    "year_order": COMPARISON_YEARS,
    "country_color": "#8A8A8A",
    "brazil_color": "#D55E00",
}


FIELDS = (
    "year",
    "iso3",
    "country",
    "region",
    "subregion",
    "homicide_rate_per_100k",
    "percentile_unweighted",
    "is_brazil",
    "sample_reporting_units",
)


def prepare_data() -> list[dict[str, object]]:
    with CONFIG["input_file"].open("r", encoding="utf-8", newline="") as stream:
        source = list(csv.DictReader(stream))
    included = [row for row in source if row["included_common_sample"] == "1"]
    year_counts = {
        year: sum(int(row["year"]) == year for row in included)
        for year in CONFIG["year_order"]
    }
    if len(set(year_counts.values())) != 1 or min(year_counts.values()) < 80:
        raise ValueError(f"Figure 1 requires one defensible common sample: {year_counts}")
    expected = {
        (int(row["year"]), row["iso3"])
        for row in included
    }
    if len(expected) != len(included):
        raise ValueError("Duplicate country-year observations in Figure 1 input.")
    rows: list[dict[str, object]] = []
    for row in included:
        year = int(row["year"])
        rate = float(row["homicide_rate_per_100k"])
        percentile = float(row["percentile_unweighted"])
        if not (0 <= rate <= 250 and 0 <= percentile <= 100):
            raise ValueError(f"Invalid Figure 1 value: {row}")
        rows.append(
            {
                "year": year,
                "iso3": row["iso3"],
                "country": row["country"],
                "region": row["region"],
                "subregion": row["subregion"],
                "homicide_rate_per_100k": rate,
                "percentile_unweighted": percentile,
                "is_brazil": int(row["iso3"] == "BRA"),
                "sample_reporting_units": year_counts[year],
            }
        )
    write_csv(CONFIG["data_file"], rows, FIELDS)
    return rows


def plot(rows: list[dict[str, object]]) -> tuple[Path, Path]:
    apply_project_style()
    sample_size = len({str(row["iso3"]) for row in rows})
    fig, axes = plt.subplots(1, 2, figsize=(11.7, 6.8), sharex=True, sharey=True)
    y_max = max(float(row["homicide_rate_per_100k"]) for row in rows) * 1.12
    for panel, (ax, year) in enumerate(zip(axes, CONFIG["year_order"]), start=1):
        series = sorted(
            (row for row in rows if row["year"] == year),
            key=lambda row: float(row["percentile_unweighted"]),
        )
        others = [row for row in series if not row["is_brazil"]]
        brazil = next(row for row in series if row["is_brazil"])
        ax.scatter(
            [float(row["percentile_unweighted"]) for row in others],
            [float(row["homicide_rate_per_100k"]) for row in others],
            s=24,
            marker="o",
            facecolor=CONFIG["country_color"],
            edgecolor="white",
            linewidth=0.35,
            alpha=0.72,
            zorder=3,
            label="Demais unidades",
        )
        bx = float(brazil["percentile_unweighted"])
        by = float(brazil["homicide_rate_per_100k"])
        ax.scatter(
            [bx], [by], s=105, marker="D", facecolor=CONFIG["brazil_color"],
            edgecolor="white", linewidth=0.8, zorder=5, label="Brasil",
        )
        ax.vlines(bx, 0, by, colors=CONFIG["brazil_color"], linestyles=(0, (3, 3)), linewidth=1.0)
        ax.annotate(
            f"Brasil: {format_br(by, 1)}\npercentil {format_br(bx, 1)}",
            xy=(bx, by),
            xytext=(-8, 12),
            textcoords="offset points",
            ha="right",
            va="bottom",
            fontsize=8.3,
            fontweight="bold",
            color="#303030",
            arrowprops={"arrowstyle": "-", "color": CONFIG["brazil_color"], "lw": 0.8},
        )
        ax.set_title(f"{chr(64 + panel)}. {year}", loc="left", pad=8)
        ax.set_xlabel(CONFIG["axis_labels"]["x"])
        ax.set_ylabel(CONFIG["axis_labels"]["y"] if panel == 1 else "")
        ax.set_xlim(-2, 102)
        ax.set_ylim(0, y_max)
        ax.set_xticks([0, 20, 40, 60, 80, 100])
        ax.xaxis.set_major_formatter(percent_tick(0))
        ax.yaxis.set_major_formatter(br_tick(0))
        style_axis(ax)
    axes[1].legend(loc="upper left", ncol=1)
    decorate_figure(
        fig,
        title=CONFIG["title"],
        subtitle=CONFIG["subtitle"],
        source_note=CONFIG["source_note"].format(sample_size=sample_size),
    )
    fig.subplots_adjust(left=0.085, right=0.985, top=0.86, bottom=0.16, wspace=0.10)
    return save_figure(
        fig,
        output_stem=CONFIG["output_stem"],
        data_path=CONFIG["data_file"],
    )


def main() -> int:
    return 0 if plot(prepare_data()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
