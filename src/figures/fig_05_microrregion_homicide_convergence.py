"""Diagnostic: beta convergence in microrregion homicide rates, 2016--2024."""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt

from .common import (
    FIGURE_DATA_DIR,
    REPO_ROOT,
    apply_project_style,
    br_tick,
    decorate_figure,
    read_csv,
    save_figure,
    style_axis,
    write_csv,
)


CONFIG = {
    "input_file": FIGURE_DATA_DIR / "fig_04_microrregion_homicide_change.csv",
    "data_file": FIGURE_DATA_DIR / "fig_05_microrregion_homicide_convergence.csv",
    "audit_file": REPO_ROOT / "data" / "audit" / "microrregion_homicide_convergence.json",
    "output_stem": "fig_05_convergencia_homicidios_microrregioes",
    "title": "Figura 5. Brasil: convergência das taxas de homicídio entre microrregiões",
    "subtitle": (
        "Taxa inicial em 2016 e variação absoluta até 2024 | "
        "área das bolhas proporcional à população em 2016"
    ),
    "source_note": (
        "Fonte: Cálculos dos autores com dados finais do SIM/Ministério da Saúde e do IBGE. "
        "Homicídios: CAUSABAS X85–X99, Y00–Y09, Y35 e Y36, por município de residência, "
        "todas as idades; geografia fixa das 558 microrregiões IBGE de 2015. "
        "Linha tracejada: ajuste linear descritivo ponderado pela população de 2016. "
        "A relação negativa não identifica causalidade e pode incorporar reversão à média."
    ),
    "axis_labels": (
        "Taxa de homicídios em 2016 (por 100 mil habitantes)",
        "Variação da taxa, 2016–2024 (por 100 mil habitantes)",
    ),
    "bubble_area_divisor": 7500.0,
    "bubble_color": "#0072B2",
    "fit_color": "#D55E00",
}


FIELDS = (
    "microrregion_code",
    "microrregion_name",
    "uf",
    "macroregion",
    "start_year",
    "end_year",
    "rate_2016_per_100k",
    "rate_2024_per_100k",
    "delta_rate_2016_2024_per_100k",
    "population_2016",
    "population_2024",
    "bubble_area_points2",
    "population_weighted_fitted_delta",
    "rate_average_2015_2017_per_100k",
    "delta_average_2015_2017_to_2022_2024_per_100k",
)


def _weighted_fit(x: list[float], y: list[float], weights: list[float]) -> dict[str, float]:
    if not (len(x) == len(y) == len(weights)) or len(x) < 2:
        raise ValueError("Regression inputs must have the same length and at least two observations.")
    if any(weight <= 0 or not math.isfinite(weight) for weight in weights):
        raise ValueError("Regression weights must be positive and finite.")
    weight_sum = sum(weights)
    x_mean = sum(weight * value for weight, value in zip(weights, x)) / weight_sum
    y_mean = sum(weight * value for weight, value in zip(weights, y)) / weight_sum
    covariance = sum(weight * (xi - x_mean) * (yi - y_mean) for xi, yi, weight in zip(x, y, weights))
    variance_x = sum(weight * (xi - x_mean) ** 2 for xi, weight in zip(x, weights))
    variance_y = sum(weight * (yi - y_mean) ** 2 for yi, weight in zip(y, weights))
    if variance_x <= 0 or variance_y <= 0:
        raise ValueError("Regression inputs have zero weighted variance.")
    slope = covariance / variance_x
    intercept = y_mean - slope * x_mean
    correlation = covariance / math.sqrt(variance_x * variance_y)
    return {
        "intercept": intercept,
        "slope": slope,
        "correlation": correlation,
        "r_squared": correlation**2,
        "x_mean": x_mean,
        "y_mean": y_mean,
    }


def _unweighted_fit(x: list[float], y: list[float]) -> dict[str, float]:
    return _weighted_fit(x, y, [1.0] * len(x))


def prepare_data() -> tuple[list[dict[str, str]], dict[str, object]]:
    source = read_csv(CONFIG["input_file"])
    if len(source) != 558 or len({row["microrregion_code"] for row in source}) != 558:
        raise ValueError("Convergence diagnostic requires 558 unique microrregions.")
    if {int(row["start_year"]) for row in source} != {2016} or {int(row["end_year"]) for row in source} != {2024}:
        raise ValueError("Convergence diagnostic requires the common 2016 and 2024 endpoints.")

    x = [float(row["rate_start_per_100k"]) for row in source]
    y = [float(row["delta_rate_per_100k"]) for row in source]
    weights = [float(row["population_start"]) for row in source]
    smooth_x = [float(row["rate_average_2015_2017_per_100k"]) for row in source]
    smooth_y = [float(row["delta_average_rate_per_100k"]) for row in source]
    if any(not math.isfinite(value) for value in (*x, *y, *weights, *smooth_x, *smooth_y)):
        raise ValueError("Convergence inputs contain non-finite values.")
    if any(value < 0 for value in x) or any(weight <= 0 for weight in weights):
        raise ValueError("Convergence inputs contain an impossible rate or population.")

    weighted = _weighted_fit(x, y, weights)
    unweighted = _unweighted_fit(x, y)
    smooth_weighted = _weighted_fit(smooth_x, smooth_y, weights)
    prepared: list[dict[str, object]] = []
    for row, rate_start, delta, population in zip(source, x, y, weights):
        rate_end = float(row["rate_end_per_100k"])
        if not math.isclose(rate_end - rate_start, delta, rel_tol=0.0, abs_tol=1e-10):
            raise ValueError(f"Change identity failed for microrregion {row['microrregion_code']}.")
        prepared.append(
            {
                "microrregion_code": row["microrregion_code"],
                "microrregion_name": row["microrregion_name"],
                "uf": row["uf"],
                "macroregion": row["macroregion"],
                "start_year": 2016,
                "end_year": 2024,
                "rate_2016_per_100k": rate_start,
                "rate_2024_per_100k": rate_end,
                "delta_rate_2016_2024_per_100k": delta,
                "population_2016": population,
                "population_2024": float(row["population_end"]),
                "bubble_area_points2": population / CONFIG["bubble_area_divisor"],
                "population_weighted_fitted_delta": weighted["intercept"] + weighted["slope"] * rate_start,
                "rate_average_2015_2017_per_100k": float(row["rate_average_2015_2017_per_100k"]),
                "delta_average_2015_2017_to_2022_2024_per_100k": float(row["delta_average_rate_per_100k"]),
            }
        )
    write_csv(CONFIG["data_file"], prepared, FIELDS)
    diagnostics: dict[str, object] = {
        "unit": "microrregion",
        "n": len(prepared),
        "start_year": 2016,
        "end_year": 2024,
        "population_weight": "population_2016",
        "endpoint_unweighted": unweighted,
        "endpoint_population_weighted": weighted,
        "smoothed_population_weighted": smooth_weighted,
        "share_with_rate_decline": sum(delta < 0 for delta in y) / len(y),
        "interpretation": (
            "A negative slope is consistent with descriptive beta convergence, but the endpoint "
            "specification mechanically includes the initial rate in the dependent variable and "
            "can reflect regression to the mean."
        ),
    }
    CONFIG["audit_file"].parent.mkdir(parents=True, exist_ok=True)
    temporary = CONFIG["audit_file"].with_suffix(".json.tmp")
    temporary.write_text(json.dumps(diagnostics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(CONFIG["audit_file"])
    return read_csv(CONFIG["data_file"]), diagnostics


def plot(rows: list[dict[str, str]], diagnostics: dict[str, object]) -> tuple[Path, Path]:
    apply_project_style()
    x = [float(row["rate_2016_per_100k"]) for row in rows]
    y = [float(row["delta_rate_2016_2024_per_100k"]) for row in rows]
    sizes = [float(row["bubble_area_points2"]) for row in rows]
    fit = diagnostics["endpoint_population_weighted"]
    if not isinstance(fit, dict):
        raise TypeError("Population-weighted diagnostics are malformed.")

    fig, ax = plt.subplots(figsize=(11.7, 6.9))
    ax.scatter(
        x,
        y,
        s=sizes,
        color=CONFIG["bubble_color"],
        alpha=0.34,
        edgecolors="#0A4F78",
        linewidths=0.45,
        zorder=3,
    )
    ax.axhline(0, color="#4D4D4D", linewidth=1.0, zorder=2)
    fit_x = [min(x), max(x)]
    fit_y = [float(fit["intercept"]) + float(fit["slope"]) * value for value in fit_x]
    ax.plot(
        fit_x,
        fit_y,
        color=CONFIG["fit_color"],
        linewidth=2.0,
        linestyle=(0, (5, 3)),
        label="Ajuste linear ponderado pela população",
        zorder=4,
    )
    legend_populations = (100_000, 1_000_000, 5_000_000)
    bubble_handles = [
        ax.scatter(
            [],
            [],
            s=value / CONFIG["bubble_area_divisor"],
            color=CONFIG["bubble_color"],
            alpha=0.34,
            edgecolors="#0A4F78",
            linewidths=0.45,
        )
        for value in legend_populations
    ]
    fit_handle = ax.get_lines()[-1]
    ax.legend(
        [*bubble_handles, fit_handle],
        ["100 mil", "1 milhão", "5 milhões", "Ajuste ponderado"],
        title="População em 2016",
        loc="lower left",
        frameon=False,
        ncol=4,
        columnspacing=1.3,
        handlelength=2.4,
    )
    ax.text(
        0.985,
        0.965,
        "Inclinação ponderada: " + f"{float(fit['slope']):.2f}".replace(".", ",") + "\n"
        "Correlação ponderada: " + f"{float(fit['correlation']):.2f}".replace(".", ","),
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=8.5,
        color="#303030",
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": "#B7B7B7"},
        zorder=5,
    )
    ax.set_xlabel(CONFIG["axis_labels"][0])
    ax.set_ylabel(CONFIG["axis_labels"][1])
    ax.xaxis.set_major_formatter(br_tick(0))
    ax.yaxis.set_major_formatter(br_tick(0))
    style_axis(ax)
    decorate_figure(
        fig,
        title=CONFIG["title"],
        subtitle=CONFIG["subtitle"],
        source_note=CONFIG["source_note"],
    )
    fig.subplots_adjust(left=0.10, right=0.985, top=0.86, bottom=0.17)
    return save_figure(fig, output_stem=CONFIG["output_stem"], data_path=CONFIG["data_file"])


def main() -> int:
    rows, diagnostics = prepare_data()
    plot(rows, diagnostics)
    weighted = diagnostics["endpoint_population_weighted"]
    smooth = diagnostics["smoothed_population_weighted"]
    if not isinstance(weighted, dict) or not isinstance(smooth, dict):
        raise TypeError("Convergence diagnostics are malformed.")
    print(
        "CONVERGENCE "
        f"n={diagnostics['n']} "
        f"weighted_slope={float(weighted['slope']):.6f} "
        f"weighted_correlation={float(weighted['correlation']):.6f} "
        f"smoothed_weighted_slope={float(smooth['slope']):.6f} "
        f"decline_share={float(diagnostics['share_with_rate_decline']):.6f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
