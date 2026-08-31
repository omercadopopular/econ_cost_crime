"""Figure 4: absolute change in homicide rates across fixed 2015 microrregions."""

from __future__ import annotations

import csv
import math
from pathlib import Path
from statistics import correlation, median

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.colors import TwoSlopeNorm
from matplotlib.cm import ScalarMappable

from .common import FIGURE_DATA_DIR, apply_project_style, decorate_figure, save_figure, write_csv
from .geography_helpers import shape_reader, shape_rings
from src.data.homicide_config import (
    ANO_FINAL_SIM,
    ANO_INICIAL,
    MICROREGION_SHAPE_SOURCE,
    PANEL_PATH,
    STATE_SHAPE_SOURCE,
)


CONFIG = {
    "input_file": PANEL_PATH,
    "geometry_file": MICROREGION_SHAPE_SOURCE["target"],
    "state_geometry_file": STATE_SHAPE_SOURCE["target"],
    "output_stem": "fig_04_variacao_homicidios_microrregioes",
    "data_file": FIGURE_DATA_DIR / "fig_04_microrregion_homicide_change.csv",
    "title": "Figura 4. Brasil: mudança nas taxas de homicídio por microrregião",
    "subtitle_template": (
        "Variação absoluta entre {start} e {end}, em homicídios por 100 mil habitantes | geografia fixa de 2015"
    ),
    "source_note_template": (
        "Fonte: Cálculos dos autores com dados finais do SIM/Ministério da Saúde e do IBGE. "
        "Homicídios: CAUSABAS X85–X99, Y00–Y09, Y35 e Y36, por município de residência. "
        "Óbitos sem município informado são excluídos. "
        "Escala visual centrada em zero e limitada a ±{limit:g}; "
        "{clipped} microrregiões além dos limites mantêm seus valores verdadeiros no CSV."
    ),
    "axis_labels": ("Longitude", "Latitude"),
    "cmap": "RdBu_r",
    "scale_quantile": 0.98,
    "scale_rounding": 5.0,
    "smooth_start_years": (2015, 2016, 2017),
    "smooth_end_years": (2022, 2023, 2024),
    # 0.008 degree is below one display pixel at the publication dimensions.
    "geometry_simplification_degrees": 0.008,
}


FIELDS = (
    "microrregion_code",
    "microrregion_name",
    "uf",
    "macroregion",
    "start_year",
    "end_year",
    "homicides_start",
    "population_start",
    "rate_start_per_100k",
    "homicides_end",
    "population_end",
    "rate_end_per_100k",
    "delta_rate_per_100k",
    "rate_average_2015_2017_per_100k",
    "rate_average_2022_2024_per_100k",
    "delta_average_rate_per_100k",
    "visual_scale_limit",
    "visual_value_clipped",
    "visually_clipped",
)


def _read_panel() -> list[dict[str, str]]:
    with CONFIG["input_file"].open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def _quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def prepare_data() -> list[dict[str, str]]:
    panel = _read_panel()
    index = {(row["microrregion_code"], int(row["year"])): row for row in panel}
    codes = sorted({row["microrregion_code"] for row in panel})
    required_years = {
        ANO_INICIAL,
        ANO_FINAL_SIM,
        *CONFIG["smooth_start_years"],
        *CONFIG["smooth_end_years"],
    }
    expected = {(code, year) for code in codes for year in required_years}
    if len(codes) != 558 or not expected.issubset(index):
        missing = sorted(expected - set(index))[:20]
        raise ValueError(f"Figure 4 fixed panel is incomplete: codes={len(codes)}, missing={missing}")
    raw: list[dict[str, object]] = []
    for code in codes:
        start = index[(code, ANO_INICIAL)]
        end = index[(code, ANO_FINAL_SIM)]

        def pooled_rate(years: tuple[int, ...]) -> float:
            deaths = sum(int(index[(code, year)]["homicide_count"]) for year in years)
            population = sum(float(index[(code, year)]["population"]) for year in years)
            return 100000.0 * deaths / population

        rate_start = float(start["homicide_rate_per_100k"])
        rate_end = float(end["homicide_rate_per_100k"])
        smooth_start = pooled_rate(CONFIG["smooth_start_years"])
        smooth_end = pooled_rate(CONFIG["smooth_end_years"])
        raw.append(
            {
                "microrregion_code": code,
                "microrregion_name": end["microrregion_name"],
                "uf": end["uf"],
                "macroregion": end["macroregion"],
                "start_year": ANO_INICIAL,
                "end_year": ANO_FINAL_SIM,
                "homicides_start": int(start["homicide_count"]),
                "population_start": float(start["population"]),
                "rate_start_per_100k": rate_start,
                "homicides_end": int(end["homicide_count"]),
                "population_end": float(end["population"]),
                "rate_end_per_100k": rate_end,
                "delta_rate_per_100k": rate_end - rate_start,
                "rate_average_2015_2017_per_100k": smooth_start,
                "rate_average_2022_2024_per_100k": smooth_end,
                "delta_average_rate_per_100k": smooth_end - smooth_start,
            }
        )
    q = _quantile([abs(float(row["delta_rate_per_100k"])) for row in raw], CONFIG["scale_quantile"])
    step = CONFIG["scale_rounding"]
    limit = math.ceil(q / step) * step
    for row in raw:
        value = float(row["delta_rate_per_100k"])
        row["visual_scale_limit"] = limit
        row["visual_value_clipped"] = max(-limit, min(limit, value))
        row["visually_clipped"] = int(abs(value) > limit)
    write_csv(CONFIG["data_file"], raw, FIELDS)
    with CONFIG["data_file"].open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def smoothing_diagnostic(rows: list[dict[str, str]]) -> dict[str, float]:
    endpoint = [float(row["delta_rate_per_100k"]) for row in rows]
    smoothed = [float(row["delta_average_rate_per_100k"]) for row in rows]
    return {
        "pearson_correlation": correlation(endpoint, smoothed),
        "same_direction_share": sum((a >= 0) == (b >= 0) for a, b in zip(endpoint, smoothed)) / len(rows),
        "median_absolute_difference": median(abs(a - b) for a, b in zip(endpoint, smoothed)),
    }


def plot(rows: list[dict[str, str]]) -> tuple[Path, Path]:
    apply_project_style()
    values = {row["microrregion_code"]: float(row["visual_value_clipped"]) for row in rows}
    limit = float(rows[0]["visual_scale_limit"])
    clipped = sum(int(row["visually_clipped"]) for row in rows)
    norm = TwoSlopeNorm(vmin=-limit, vcenter=0.0, vmax=limit)
    cmap = plt.get_cmap(CONFIG["cmap"])
    micro_reader = shape_reader(CONFIG["geometry_file"])
    polygons: list[list[tuple[float, float]]] = []
    colors: list[tuple[float, float, float, float]] = []
    for record, shape in zip(micro_reader.iterRecords(), micro_reader.iterShapes()):
        code = str(record["CD_GEOCMI"]).zfill(5)
        if code not in values:
            raise ValueError(f"No Figure 4 value for geometry {code}.")
        for ring in shape_rings(shape, simplify_tolerance=CONFIG["geometry_simplification_degrees"]):
            polygons.append(ring)
            colors.append(cmap(norm(values[code])))
    state_reader = shape_reader(CONFIG["state_geometry_file"])
    state_lines = [
        ring
        for shape in state_reader.iterShapes()
        for ring in shape_rings(shape, simplify_tolerance=CONFIG["geometry_simplification_degrees"])
    ]
    fig, ax = plt.subplots(figsize=(11.7, 8.0))
    ax.add_collection(
        PolyCollection(
            polygons,
            facecolors=colors,
            edgecolors="white",
            linewidths=0.18,
            antialiased=True,
            zorder=2,
        )
    )
    ax.add_collection(LineCollection(state_lines, colors="#4A4A4A", linewidths=0.65, zorder=3))
    ax.set_xlim(-74.5, -32.0)
    ax.set_ylim(-34.5, 6.0)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    scalar = ScalarMappable(norm=norm, cmap=cmap)
    colorbar = fig.colorbar(
        scalar,
        ax=ax,
        orientation="horizontal",
        fraction=0.045,
        pad=0.025,
        shrink=0.62,
        aspect=35,
    )
    colorbar.outline.set_visible(False)
    colorbar.set_label("Variação absoluta na taxa de homicídios por 100 mil habitantes")
    colorbar.ax.tick_params(length=0, labelsize=8)
    colorbar.ax.text(0.0, -1.65, "Queda", transform=colorbar.ax.transAxes, ha="left", va="top", fontsize=8, fontweight="bold")
    colorbar.ax.text(1.0, -1.65, "Aumento", transform=colorbar.ax.transAxes, ha="right", va="top", fontsize=8, fontweight="bold")
    decorate_figure(
        fig,
        title=CONFIG["title"],
        subtitle=CONFIG["subtitle_template"].format(start=ANO_INICIAL, end=ANO_FINAL_SIM),
        source_note=CONFIG["source_note_template"].format(limit=limit, clipped=clipped),
    )
    fig.subplots_adjust(left=0.055, right=0.965, top=0.875, bottom=0.13)
    return save_figure(fig, output_stem=CONFIG["output_stem"], data_path=CONFIG["data_file"])


def main() -> int:
    rows = prepare_data()
    diagnostic = smoothing_diagnostic(rows)
    print(
        "SMOOTHING "
        f"correlation={diagnostic['pearson_correlation']:.4f} "
        f"same_direction={diagnostic['same_direction_share']:.4f} "
        f"median_abs_difference={diagnostic['median_absolute_difference']:.4f}"
    )
    plot(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
