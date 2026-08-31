"""Shared visual system, CSV I/O, output checks, and plotting helpers."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import textwrap
from typing import Any, Iterable, Mapping, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter


REPO_ROOT = Path(__file__).resolve().parents[2]
FIGURE_DIR = REPO_ROOT / "figs"
FIGURE_DATA_DIR = REPO_ROOT / "data" / "figure_data"
MANIFEST_PATH = FIGURE_DATA_DIR / "local_figures_manifest.json"

NATIONAL_LONG_FIELDS = (
    "ano",
    "componente",
    "natureza_contabil",
    "valor_reais_dez_2025",
    "pib_reais_dez_2025",
    "participacao_pib_pct",
    "composicao_pct",
    "total_calculado_reais_dez_2025",
    "total_reportado_reais_dez_2025",
)

COMPONENT_COLORS = {
    "Serviços médico-terapêuticos": "#56B4E9",
    "Encarceramento e auxílio-reclusão": "#CC79A7",
    "Custos judiciais": "#009E73",
    "Perda de capacidade produtiva": "#D55E00",
    "Seguros e perdas materiais": "#E69F00",
    "Segurança privada": "#0072B2",
    "Segurança pública": "#4D4D4D",
}

SUBCOMPONENT_PALETTES = {
    "public": ("#4D4D4D", "#0072B2", "#E69F00"),
    "private": ("#0072B2", "#56B4E9"),
    "incarceration": ("#CC79A7", "#882255"),
    "insurance": ("#0072B2", "#56B4E9", "#009E73", "#E69F00", "#D55E00", "#CC79A7"),
    "justice": ("#009E73", "#0072B2", "#CC79A7"),
}


def apply_project_style() -> None:
    """Apply the report-page adaptation of the 2018 visual language."""

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9.5,
            "axes.titlesize": 11,
            "axes.titleweight": "bold",
            "axes.labelsize": 9.5,
            "axes.edgecolor": "none",
            "axes.linewidth": 0,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8.5,
            "legend.fontsize": 8.5,
            "legend.frameon": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "axes.axisbelow": True,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def format_br(value: float, decimals: int = 1) -> str:
    formatted = f"{value:,.{decimals}f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def br_tick(decimals: int = 1) -> FuncFormatter:
    return FuncFormatter(lambda value, _position: format_br(value, decimals))


def percent_tick(decimals: int = 1) -> FuncFormatter:
    return FuncFormatter(lambda value, _position: f"{format_br(value, decimals)}%")


def style_axis(ax: Axes, *, y_grid: bool = True) -> None:
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="both", colors="#292929", length=0, pad=4)
    for label in ax.get_yticklabels():
        label.set_fontweight("bold")
    if y_grid:
        ax.grid(axis="y", color="#B7B7B7", linewidth=1.15, alpha=1.0)
        ax.grid(axis="x", visible=False)
        ax.set_axisbelow(True)


def decorate_figure(
    fig: Figure,
    *,
    title: str,
    subtitle: str,
    source_note: str,
    note_width: int = 155,
) -> None:
    fig.suptitle(title, x=0.075, y=0.975, ha="left", va="top", fontsize=17, fontweight="bold")
    fig.text(0.075, 0.940, subtitle, ha="left", va="top", fontsize=11, color="#303030")
    wrapped = textwrap.fill(source_note, width=note_width)
    fig.text(0.075, 0.018, wrapped, ha="left", va="bottom", fontsize=7.4, color="#303030")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_csv(path: Path, rows: Iterable[Mapping[str, Any]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    materialized = list(rows)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="raise")
        writer.writeheader()
        writer.writerows(materialized)
    temp.replace(path)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def _update_manifest(stem: str, data_path: Path, pdf_path: Path, png_path: Path) -> None:
    FIGURE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {}
    if MANIFEST_PATH.exists():
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    rows = read_csv(data_path)
    years = sorted(
        {
            int(float(value))
            for row in rows
            for value in (
                row.get("ano"), row.get("year"), row.get("start_year"), row.get("end_year"),
                row.get("period_start"), row.get("period_end"),
            )
            if value not in (None, "")
        }
    )
    if not years:
        raise ValueError(f"Figure-ready data have no recognizable year field: {data_path}")
    manifest[stem] = {
        "data_file": str(data_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "data_sha256": sha256(data_path),
        "pdf_file": str(pdf_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "pdf_sha256": sha256(pdf_path),
        "png_file": str(png_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "png_sha256": sha256(png_path),
        "row_count": len(rows),
        "year_min": min(years),
        "year_max": max(years),
    }
    temp = MANIFEST_PATH.with_suffix(".json.tmp")
    temp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(MANIFEST_PATH)


def save_figure(fig: Figure, *, output_stem: str, data_path: Path) -> tuple[Path, Path]:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = FIGURE_DIR / f"{output_stem}.pdf"
    png_path = FIGURE_DIR / f"{output_stem}.png"
    fig.savefig(pdf_path, bbox_inches="tight")
    fig.savefig(png_path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    for path in (data_path, pdf_path, png_path):
        if not path.exists() or path.stat().st_size == 0:
            raise RuntimeError(f"Expected nonempty output was not produced: {path}")
    _update_manifest(output_stem, data_path, pdf_path, png_path)
    return pdf_path, png_path


def component_colors(order: Sequence[str], palette_name: str | None = None) -> list[str]:
    if all(label in COMPONENT_COLORS for label in order):
        return [COMPONENT_COLORS[label] for label in order]
    if palette_name is None or palette_name not in SUBCOMPONENT_PALETTES:
        raise ValueError(f"No color mapping for components: {order}")
    palette = SUBCOMPONENT_PALETTES[palette_name]
    if len(order) > len(palette):
        raise ValueError(f"Palette {palette_name} is too short for {order}.")
    return list(palette[: len(order)])


def plot_component_panels(
    rows: Sequence[Mapping[str, str]],
    *,
    component_order: Sequence[str],
    colors: Sequence[str],
    title: str,
    subtitle: str,
    source_note: str,
    output_stem: str,
    data_path: Path,
) -> tuple[Path, Path]:
    apply_project_style()
    years = sorted({int(row["ano"]) for row in rows})
    indexed = {(int(row["ano"]), row["componente"]): row for row in rows}
    expected = {(year, label) for year in years for label in component_order}
    if set(indexed) != expected:
        missing = sorted(expected - set(indexed))[:10]
        extra = sorted(set(indexed) - expected)[:10]
        raise ValueError(f"Unexpected plotting keys; missing={missing}, extra={extra}")

    value_series = [
        [float(indexed[(year, label)]["valor_reais_dez_2025"]) / 1e9 for year in years]
        for label in component_order
    ]
    gdp_series = [
        [float(indexed[(year, label)]["participacao_pib_pct"]) for year in years]
        for label in component_order
    ]
    composition_series = [
        [float(indexed[(year, label)]["composicao_pct"]) for year in years]
        for label in component_order
    ]
    maximum_gdp_share = max(sum(values) for values in zip(*gdp_series))
    gdp_decimals = 2 if maximum_gdp_share < 0.5 else 1

    fig, axes = plt.subplots(3, 1, figsize=(11.7, 10.2), sharex=True)
    panels = (
        (value_series, "A. Valores reais", "R$ bilhões de dez./2025"),
        (gdp_series, "B. Participação no PIB", "Percentual do PIB"),
        (composition_series, "C. Percentual do total", "Percentual do total"),
    )
    for ax, (series, panel_title, ylabel) in zip(axes, panels):
        bottom = [0.0] * len(years)
        for label, values, color in zip(component_order, series, colors):
            ax.bar(
                years,
                values,
                bottom=bottom,
                width=0.78,
                label=label,
                color=color,
                alpha=1.0,
                edgecolor="white",
                linewidth=0.35,
            )
            bottom = [base + value for base, value in zip(bottom, values)]
        ax.set_title(panel_title, loc="left", pad=7)
        ax.set_ylabel(ylabel)
        ax.set_xlim(min(years) - 0.6, max(years) + 0.6)
        ax.set_ylim(bottom=0)
        if ax is axes[0]:
            ax.yaxis.set_major_formatter(br_tick(1))
        elif ax is axes[1]:
            ax.yaxis.set_major_formatter(percent_tick(gdp_decimals))
        else:
            ax.yaxis.set_major_formatter(percent_tick(1))
        style_axis(ax)
    axes[2].set_ylim(0, 100)
    axes[2].set_xlabel("Ano")
    axes[2].set_xticks(years)
    axes[2].tick_params(axis="x", labelrotation=90)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper left",
        bbox_to_anchor=(0.075, 0.915),
        ncol=min(4, len(labels)),
        frameon=False,
        handlelength=1.8,
        columnspacing=1.3,
    )
    decorate_figure(fig, title=title, subtitle=subtitle, source_note=source_note)
    axes_top = 0.82 if len(component_order) > 4 else 0.855
    fig.subplots_adjust(left=0.10, right=0.985, top=axes_top, bottom=0.13, hspace=0.34)
    return save_figure(fig, output_stem=output_stem, data_path=data_path)


def plot_two_panel_series(
    rows: Sequence[Mapping[str, str]],
    *,
    title: str,
    subtitle: str,
    source_note: str,
    series_label: str,
    color: str,
    modeled: bool,
    output_stem: str,
    data_path: Path,
) -> tuple[Path, Path]:
    apply_project_style()
    ordered = sorted(rows, key=lambda row: int(row["ano"]))
    years = [int(row["ano"]) for row in ordered]
    values = [float(row["valor_reais_dez_2025"]) / 1e9 for row in ordered]
    shares = [float(row["participacao_pib_pct"]) for row in ordered]
    value_decimals = 2 if max(values) < 1.0 else 1
    share_decimals = 4 if max(shares) < 0.01 else (2 if max(shares) < 1.0 else 1)
    fig, axes = plt.subplots(2, 1, figsize=(11.7, 7.5), sharex=True)
    for ax, series, panel_title, ylabel, formatter in (
        (axes[0], values, "A. Valores reais", "R$ bilhões de dez./2025", br_tick(value_decimals)),
        (axes[1], shares, "B. Participação no PIB", "Percentual do PIB", percent_tick(share_decimals)),
    ):
        ax.bar(
            years,
            series,
            color=color,
            width=0.72,
            alpha=0.82 if modeled else 1.0,
            edgecolor=color if modeled else "white",
            linewidth=0.9 if modeled else 0.45,
            hatch="///" if modeled else None,
            label=series_label,
        )
        ax.set_title(panel_title, loc="left", pad=7)
        ax.set_ylabel(ylabel)
        ax.set_xlim(min(years) - 0.6, max(years) + 0.6)
        ax.set_ylim(bottom=0)
        ax.yaxis.set_major_formatter(formatter)
        style_axis(ax)
    axes[0].legend(loc="upper left", frameon=False)
    axes[1].set_xlabel("Ano")
    axes[1].set_xticks(years)
    axes[1].tick_params(axis="x", labelrotation=90)
    decorate_figure(fig, title=title, subtitle=subtitle, source_note=source_note)
    fig.subplots_adjust(left=0.10, right=0.985, top=0.865, bottom=0.17, hspace=0.34)
    return save_figure(fig, output_stem=output_stem, data_path=data_path)


def annotate_repelled(
    ax: Axes,
    x: Sequence[float],
    y: Sequence[float],
    labels: Sequence[str],
    *,
    fontsize: float = 7.0,
) -> None:
    """Place short labels with deterministic screen-space repulsion."""

    ax.figure.canvas.draw()
    transform = ax.transData
    inverse = transform.inverted()
    anchors = [list(transform.transform((xi, yi))) for xi, yi in zip(x, y)]
    positions = [[point[0] + 8.0, point[1] + 3.0] for point in anchors]
    bbox = ax.get_window_extent()
    for _ in range(220):
        moved = False
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                dx = positions[i][0] - positions[j][0]
                dy = positions[i][1] - positions[j][1]
                if abs(dx) < 18.0 and abs(dy) < 11.0:
                    push = (11.0 - abs(dy)) / 2.0 + 0.5
                    direction = 1.0 if dy >= 0 else -1.0
                    positions[i][1] += push * direction
                    positions[j][1] -= push * direction
                    moved = True
        for i, position in enumerate(positions):
            position[0] += 0.015 * (anchors[i][0] + 8.0 - position[0])
            position[1] += 0.015 * (anchors[i][1] + 3.0 - position[1])
            position[0] = min(max(position[0], bbox.x0 + 7), bbox.x1 - 14)
            position[1] = min(max(position[1], bbox.y0 + 7), bbox.y1 - 7)
        if not moved:
            break
    for anchor, position, label in zip(anchors, positions, labels):
        tx, ty = inverse.transform(position)
        px, py = inverse.transform(anchor)
        ax.annotate(
            label,
            xy=(px, py),
            xytext=(tx, ty),
            textcoords="data",
            ha="left",
            va="center",
            fontsize=fontsize,
            fontweight="bold",
            color="#303030",
            arrowprops={"arrowstyle": "-", "color": "#A0A0A0", "lw": 0.45},
            bbox={"boxstyle": "round,pad=0.12", "fc": "white", "ec": "none", "alpha": 0.82},
            clip_on=True,
        )
