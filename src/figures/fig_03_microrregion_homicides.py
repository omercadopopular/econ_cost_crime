"""Figure 3: distribution of homicide rates across fixed 2015 IBGE microrregions."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

from .common import (
    FIGURE_DATA_DIR,
    apply_project_style,
    br_tick,
    decorate_figure,
    save_figure,
    style_axis,
    write_csv,
)
from src.data.homicide_config import ANO_FINAL_SIM, PANEL_PATH


CONFIG = {
    "input_file": PANEL_PATH,
    "output_stem": "fig_03_homicidios_microrregioes",
    "data_file": FIGURE_DATA_DIR / "fig_03_microrregion_homicides.csv",
    "title": "Figura 3. Brasil: distribuição das taxas de homicídio por microrregião",
    "subtitle_template": (
        "{year} | taxa por 100 mil habitantes; cada bolha é uma microrregião e sua área representa a população"
    ),
    "source_note": (
        "Fonte: Cálculos dos autores com dados finais do SIM/Ministério da Saúde e do IBGE. "
        "Homicídios: CAUSABAS X85–X99, Y00–Y09, Y35 e Y36, por município de residência, todas as idades. "
        "Geografia fixa das 558 microrregiões IBGE de 2015; óbitos sem município de residência informado são excluídos."
    ),
    "axis_labels": ("Percentil na distribuição das microrregiões", "Homicídios por 100 mil habitantes"),
    "bubble_area_divisor": 7500.0,
    "color": "#0072B2",
    "capital_microrregion_codes": (
        "35061",  # São Paulo
        "33018",  # Rio de Janeiro
        "31030",  # Belo Horizonte
        "43026",  # Porto Alegre
        "23016",  # Fortaleza
        "41037",  # Curitiba
        "29021",  # Salvador
        "26017",  # Recife
        "53001",  # Brasília
        "52010",  # Goiânia
        "13007",  # Manaus
        "15007",  # Belém
        "21002",  # Aglomeração Urbana de São Luís
    ),
    "maximum_capital_labels": 10,
    "required_capital_labels": ("23016", "21002"),  # Fortaleza e São Luís
    "capital_display_labels": {"21002": "São Luís (MA)"},
    "capital_label_offsets": {
        "35061": (10, -3),
        "53001": (10, -15),
        "31030": (10, 12),
        "43026": (-10, -18),
        "41037": (-10, 17),
        "52010": (10, -18),
        "21002": (10, 15),
        "33018": (10, -17),
        "23016": (10, 10),
        "26017": (-10, 10),
        "29021": (-10, 10),
    },
}


FIELDS = (
    "year",
    "microrregion_code",
    "microrregion_name",
    "uf",
    "macroregion",
    "homicide_count",
    "population",
    "homicide_rate_per_100k",
    "percentile_unweighted",
    "bubble_area_points2",
)


def _read_panel() -> list[dict[str, str]]:
    with CONFIG["input_file"].open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def prepare_data() -> list[dict[str, str]]:
    rows = [row for row in _read_panel() if int(row["year"]) == ANO_FINAL_SIM]
    if len(rows) != 558:
        raise ValueError(f"Figure 3 requires 558 microrregions in {ANO_FINAL_SIM}; found {len(rows)}.")
    if len({row["microrregion_code"] for row in rows}) != 558:
        raise ValueError("Figure 3 microrregion key is not unique.")
    prepared: list[dict[str, object]] = []
    for row in sorted(rows, key=lambda item: float(item["percentile_unweighted"])):
        population = float(row["population"])
        prepared.append(
            {
                "year": ANO_FINAL_SIM,
                "microrregion_code": row["microrregion_code"],
                "microrregion_name": row["microrregion_name"],
                "uf": row["uf"],
                "macroregion": row["macroregion"],
                "homicide_count": int(row["homicide_count"]),
                "population": population,
                "homicide_rate_per_100k": float(row["homicide_rate_per_100k"]),
                "percentile_unweighted": float(row["percentile_unweighted"]),
                "bubble_area_points2": population / CONFIG["bubble_area_divisor"],
            }
        )
    write_csv(CONFIG["data_file"], prepared, FIELDS)
    with CONFIG["data_file"].open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def _label_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    capital_codes = set(CONFIG["capital_microrregion_codes"])
    capitals = [row for row in rows if row["microrregion_code"] in capital_codes]
    if len(capitals) != len(capital_codes):
        found = {row["microrregion_code"] for row in capitals}
        raise ValueError(f"Missing configured capital microrregions: {sorted(capital_codes - found)}")
    ranked = sorted(capitals, key=lambda row: float(row["population"]), reverse=True)
    selected = {row["microrregion_code"]: row for row in ranked[: CONFIG["maximum_capital_labels"]]}
    selected.update(
        {row["microrregion_code"]: row for row in capitals if row["microrregion_code"] in CONFIG["required_capital_labels"]}
    )
    return sorted(selected.values(), key=lambda row: float(row["population"]), reverse=True)


def plot(rows: list[dict[str, str]]) -> tuple[Path, Path]:
    apply_project_style()
    x = [float(row["percentile_unweighted"]) for row in rows]
    y = [float(row["homicide_rate_per_100k"]) for row in rows]
    sizes = [float(row["bubble_area_points2"]) for row in rows]
    fig, ax = plt.subplots(figsize=(11.7, 6.7))
    ax.scatter(
        x,
        y,
        s=sizes,
        color=CONFIG["color"],
        alpha=0.36,
        edgecolors="#0A4F78",
        linewidths=0.45,
        zorder=3,
    )
    legend_populations = (100_000, 1_000_000, 5_000_000)
    handles = [
        ax.scatter(
            [],
            [],
            s=value / CONFIG["bubble_area_divisor"],
            color=CONFIG["color"],
            alpha=0.36,
            edgecolors="#0A4F78",
            linewidths=0.45,
        )
        for value in legend_populations
    ]
    ax.legend(
        handles,
        ("100 mil", "1 milhão", "5 milhões"),
        title="População",
        loc="upper left",
        frameon=False,
        labelspacing=1.4,
        borderpad=0.3,
    )
    ax.set_xlabel(CONFIG["axis_labels"][0])
    ax.set_ylabel(CONFIG["axis_labels"][1])
    ax.set_xlim(0, 102)
    ax.set_ylim(bottom=0)
    ax.set_xticks(range(0, 101, 10))
    ax.yaxis.set_major_formatter(br_tick(0))
    style_axis(ax)
    label_rows = _label_rows(rows)
    for row in label_rows:
        code = row["microrregion_code"]
        offset = CONFIG["capital_label_offsets"][code]
        label = CONFIG["capital_display_labels"].get(code, f"{row['microrregion_name']} ({row['uf']})")
        ax.annotate(
            label,
            xy=(float(row["percentile_unweighted"]), float(row["homicide_rate_per_100k"])),
            xytext=offset,
            textcoords="offset points",
            ha="right" if offset[0] < 0 else "left",
            va="bottom" if offset[1] >= 0 else "top",
            fontsize=7.0,
            fontweight="bold",
            color="#303030",
            arrowprops={"arrowstyle": "-", "color": "#8A8A8A", "lw": 0.5},
            bbox={"boxstyle": "round,pad=0.14", "fc": "white", "ec": "none", "alpha": 0.86},
            zorder=5,
        )
    decorate_figure(
        fig,
        title=CONFIG["title"],
        subtitle=CONFIG["subtitle_template"].format(year=ANO_FINAL_SIM),
        source_note=CONFIG["source_note"],
    )
    fig.subplots_adjust(left=0.095, right=0.985, top=0.86, bottom=0.16)
    return save_figure(fig, output_stem=CONFIG["output_stem"], data_path=CONFIG["data_file"])


def main() -> int:
    plot(prepare_data())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
