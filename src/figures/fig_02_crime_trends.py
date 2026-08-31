"""Figures 2A–2D: comparable Brazilian reported-crime trends."""

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
    save_figure,
    style_axis,
    write_csv,
)
from src.data.build_sinesp_panel import (
    ANO_FINAL_SINESP,
    ANO_INICIAL_SINESP,
    FIGURE_YEARS,
    NATIONAL_PANEL_PATH,
    PARTIAL_COVERAGE_CRIMES,
    PARTIAL_NATIONAL_PANEL_PATH,
    SELECTED_CRIMES,
)


CONFIG = {
    "input_file": NATIONAL_PANEL_PATH,
    "output_stems": {
        "count": "fig_02a_crimes_registrados",
        "rate": "fig_02b_taxas_criminalidade",
    },
    "data_files": {
        "count": FIGURE_DATA_DIR / "fig_02a_crimes_registrados.csv",
        "rate": FIGURE_DATA_DIR / "fig_02b_taxas_criminalidade.csv",
    },
    "titles": {
        "count": "Figura 2A. Brasil: tendências da criminalidade — vítimas registradas",
        "rate": "Figura 2B. Brasil: tendências da criminalidade — taxas de vítimas registradas",
    },
    "subtitle": (
        f"{ANO_INICIAL_SINESP}–{ANO_FINAL_SINESP} | seis indicadores com 27 UFs e 12 meses em todos os anos"
    ),
    "source_note": (
        "Fonte: Cálculos dos autores com dados do Sinesp VDE/Ministério da Justiça e Segurança "
        "Pública e Projeções da População do IBGE, Revisão 2024. Os seis indicadores contam "
        "vítimas, não ocorrências; estupro e estupro de vulnerável são séries distintas e não são "
        "somados. Feminicídio é uma classificação legal recente e sua trajetória também pode "
        "refletir consolidação do registro."
    ),
    "axis_labels": {
        "count": "Mil vítimas registradas",
        "rate": "Vítimas por 100 mil habitantes",
    },
    "display_labels": {crime: crime for crime in SELECTED_CRIMES},
    "crime_order": SELECTED_CRIMES,
    "colors": {
        "Homicídio doloso": "#4D4D4D",
        "Latrocínio": "#882255",
        "Tentativa de homicídio": "#0072B2",
        "Estupro": "#E69F00",
        "Estupro de vulnerável": "#56B4E9",
        "Feminicídio": "#CC79A7",
    },
    "layout": (3, 2),
}

PARTIAL_CONFIG = {
    "input_file": PARTIAL_NATIONAL_PANEL_PATH,
    "output_stems": {
        "count": "fig_02c_crimes_cobertura_parcial",
        "rate": "fig_02d_taxas_cobertura_parcial",
    },
    "data_files": {
        "count": FIGURE_DATA_DIR / "fig_02c_crimes_cobertura_parcial.csv",
        "rate": FIGURE_DATA_DIR / "fig_02d_taxas_cobertura_parcial.csv",
    },
    "titles": {
        "count": "Figura 2C. Cobertura parcial: tendências de crimes patrimoniais registrados",
        "rate": "Figura 2D. Cobertura parcial: taxas de crimes patrimoniais registrados",
    },
    "subtitle": (
        f"{ANO_INICIAL_SINESP}–{ANO_FINAL_SINESP} | painel balanceado específico para cada indicador"
    ),
    "source_note": (
        "Fonte: Cálculos dos autores com dados do Sinesp VDE/Ministério da Justiça e "
        "Segurança Pública e Projeções da População do IBGE, Revisão 2024. "
        "Cada série usa sua maior amostra de UFs com 12 meses em todos os anos. Os valores são "
        "ocorrências registradas nesses painéis e não totais nacionais; ausências de reporte nunca "
        "foram convertidas em zero."
    ),
    "dynamic_sample_note": True,
    "axis_labels": {
        "count": "Mil ocorrências registradas",
        "rate": "Ocorrências por 100 mil habitantes",
    },
    "display_labels": {crime: crime for crime in PARTIAL_COVERAGE_CRIMES},
    "crime_order": PARTIAL_COVERAGE_CRIMES,
    "colors": {
        "Furto de veículo": "#0072B2",
        "Roubo de veículo": "#56B4E9",
        "Roubo de carga": "#E69F00",
        "Roubo a instituição financeira": "#D55E00",
    },
    "layout": (2, 2),
}


FIELDS = (
    "year",
    "crime",
    "measurement_concept",
    "geographic_sample",
    "reporting_ufs",
    "population_coverage_pct",
    "population",
    "count",
    "rate_per_100k",
    "plotted_value",
    "plot_unit",
)
PARTIAL_FIELDS = FIELDS[:6] + ("excluded_uf_codes",) + FIELDS[6:]


def _read_input() -> list[dict[str, str]]:
    with CONFIG["input_file"].open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def prepare_data() -> dict[str, list[dict[str, object]]]:
    indexed = {
        (row["crime"], int(row["year"])): row
        for row in _read_input()
        if row["crime"] in CONFIG["crime_order"] and int(row["year"]) in FIGURE_YEARS
    }
    expected = {(crime, year) for crime in CONFIG["crime_order"] for year in FIGURE_YEARS}
    if set(indexed) != expected:
        raise ValueError(f"Figure 2 input mismatch: missing={sorted(expected - set(indexed))[:20]}")
    common: list[dict[str, object]] = []
    for crime in CONFIG["crime_order"]:
        for year in FIGURE_YEARS:
            row = indexed[(crime, year)]
            if row["reporting_ufs"] != "27" or row["balanced_sample_ufs"] != "27":
                raise ValueError(f"Figure 2 requires complete Brazil coverage: {crime}, {year}, {row}")
            count = int(row["balanced_sample_total"])
            if count != int(row["raw_reported_total"]):
                raise ValueError(f"Raw and balanced totals differ despite 27-UF coverage: {crime}, {year}")
            population = int(row["balanced_sample_population"])
            rate = float(row["balanced_sample_rate_per_100k"])
            if abs(rate - 100000.0 * count / population) > 1e-10:
                raise ValueError(f"Figure 2 rate identity fails: {crime}, {year}")
            common.append(
                {
                    "year": year,
                    "crime": crime,
                    "measurement_concept": row["measurement_concept"],
                    "geographic_sample": "Brasil — 27 UFs",
                    "reporting_ufs": 27,
                    "population_coverage_pct": 100.0,
                    "population": population,
                    "count": count,
                    "rate_per_100k": rate,
                }
            )
    outputs: dict[str, list[dict[str, object]]] = {}
    for mode in ("count", "rate"):
        rows: list[dict[str, object]] = []
        for row in common:
            item = dict(row)
            item["plotted_value"] = row["count"] if mode == "count" else row["rate_per_100k"]
            item["plot_unit"] = "vítimas" if mode == "count" else "vítimas por 100 mil habitantes"
            rows.append(item)
        write_csv(CONFIG["data_files"][mode], rows, FIELDS)
        outputs[mode] = rows
    return outputs


def prepare_partial_data() -> dict[str, list[dict[str, object]]]:
    with PARTIAL_CONFIG["input_file"].open("r", encoding="utf-8", newline="") as stream:
        source = list(csv.DictReader(stream))
    indexed = {
        (row["crime"], int(row["year"])): row
        for row in source
        if row["crime"] in PARTIAL_CONFIG["crime_order"] and int(row["year"]) in FIGURE_YEARS
    }
    expected = {
        (crime, year) for crime in PARTIAL_CONFIG["crime_order"] for year in FIGURE_YEARS
    }
    if set(indexed) != expected:
        raise ValueError(
            f"Figure 2C/2D input mismatch: missing={sorted(expected - set(indexed))[:20]}"
        )
    common: list[dict[str, object]] = []
    for crime in PARTIAL_CONFIG["crime_order"]:
        crime_rows = [indexed[(crime, year)] for year in FIGURE_YEARS]
        sample_codes = {row["sample_codes"] for row in crime_rows}
        sample_sizes = {row["sample_ufs"] for row in crime_rows}
        excluded_codes = {row["excluded_uf_codes"] for row in crime_rows}
        if len(sample_codes) != 1 or len(sample_sizes) != 1 or len(excluded_codes) != 1:
            raise ValueError(f"Figure 2C/2D sample changes within the series: {crime}")
        sample = next(iter(sample_codes)).split()
        excluded = next(iter(excluded_codes)).split()
        if len(sample) != int(next(iter(sample_sizes))) or set(sample) & set(excluded):
            raise ValueError(f"Figure 2C/2D sample metadata are inconsistent: {crime}")
        for year in FIGURE_YEARS:
            row = indexed[(crime, year)]
            count = int(row["count"])
            population = int(row["sample_population"])
            rate = float(row["rate_per_100k"])
            if abs(rate - 100000.0 * count / population) > 1e-10:
                raise ValueError(f"Figure 2C/2D rate identity fails: {crime}, {year}")
            common.append(
                {
                    "year": year,
                    "crime": crime,
                    "measurement_concept": row["measurement_concept"],
                    "geographic_sample": row["sample_codes"],
                    "reporting_ufs": int(row["sample_ufs"]),
                    "population_coverage_pct": float(row["sample_population_share_brazil_pct"]),
                    "excluded_uf_codes": row["excluded_uf_codes"],
                    "population": population,
                    "count": count,
                    "rate_per_100k": rate,
                }
            )
    outputs: dict[str, list[dict[str, object]]] = {}
    for mode in ("count", "rate"):
        rows: list[dict[str, object]] = []
        for row in common:
            item = dict(row)
            item["plotted_value"] = row["count"] if mode == "count" else row["rate_per_100k"]
            item["plot_unit"] = (
                "ocorrências" if mode == "count" else "ocorrências por 100 mil habitantes"
            )
            rows.append(item)
        write_csv(PARTIAL_CONFIG["data_files"][mode], rows, PARTIAL_FIELDS)
        outputs[mode] = rows
    return outputs


def _partial_sample_note(rows: list[dict[str, object]]) -> str:
    details: list[str] = []
    for crime in PARTIAL_CONFIG["crime_order"]:
        endpoint = next(
            row for row in rows
            if row["crime"] == crime and int(row["year"]) == ANO_FINAL_SINESP
        )
        excluded = str(endpoint["excluded_uf_codes"]).split()
        if not excluded:
            exclusion_clause = "nenhuma UF excluída"
        elif len(excluded) == 1:
            exclusion_clause = f"excluída {excluded[0]}"
        else:
            excluded_text = ", ".join(excluded[:-1]) + " e " + excluded[-1]
            exclusion_clause = f"excluídas {excluded_text}"
        details.append(
            f"{str(crime).lower()}: {int(endpoint['reporting_ufs'])} UFs, "
            f"{format_br(float(endpoint['population_coverage_pct']), 1)}% da população em "
            f"{ANO_FINAL_SINESP}; {exclusion_clause}"
        )
    return "Cobertura por indicador — " + "; ".join(details) + "."


def _plot(
    rows: list[dict[str, object]], mode: str, figure_config: dict[str, object]
) -> tuple[Path, Path]:
    apply_project_style()
    nrows, ncols = figure_config["layout"]
    height = 9.2 if nrows == 3 else 7.2
    fig, axes = plt.subplots(nrows, ncols, figsize=(11.7, height), sharex=True)
    years = list(FIGURE_YEARS)
    for ax, crime in zip(axes.flat, figure_config["crime_order"]):
        series = sorted((row for row in rows if row["crime"] == crime), key=lambda row: int(row["year"]))
        raw_values = [float(row["plotted_value"]) for row in series]
        values = [value / 1000.0 for value in raw_values] if mode == "count" else raw_values
        bars = ax.bar(
            years,
            values,
            width=0.72,
            color=figure_config["colors"][crime],
            edgecolor="white",
            linewidth=0.35,
            zorder=3,
        )
        ax.set_title(figure_config["display_labels"][crime], loc="left", pad=6, fontsize=10.5)
        ax.set_ylabel(figure_config["axis_labels"][mode])
        ax.set_xticks(years)
        ax.set_xticklabels([str(year) for year in years], rotation=90)
        ax.tick_params(axis="x", labelbottom=True)
        tick_decimals = 1 if mode == "rate" or max(values) < 10 else 0
        ax.yaxis.set_major_formatter(br_tick(tick_decimals))
        upper = max(values) * 1.23 if max(values) > 0 else 1.0
        ax.set_ylim(0, upper)
        for bar, value in zip(bars, values):
            if mode == "rate":
                label = "<0,1" if 0 < value < 0.05 else format_br(value, 1)
            else:
                label = "<1" if 0 < value < 1 else format_br(value, 0)
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                value + upper * 0.018,
                label,
                ha="center",
                va="bottom",
                fontsize=6.4,
                fontweight="bold",
                color="#303030",
            )
        style_axis(ax)
    source_note = str(figure_config["source_note"])
    if figure_config.get("dynamic_sample_note"):
        source_note += " " + _partial_sample_note(rows)
    decorate_figure(
        fig,
        title=figure_config["titles"][mode],
        subtitle=figure_config["subtitle"],
        source_note=source_note,
    )
    bottom = 0.20 if figure_config.get("dynamic_sample_note") else 0.15
    fig.subplots_adjust(left=0.085, right=0.985, top=0.88, bottom=bottom, hspace=0.55, wspace=0.20)
    return save_figure(
        fig,
        output_stem=figure_config["output_stems"][mode],
        data_path=figure_config["data_files"][mode],
    )


def main() -> int:
    data = prepare_data()
    partial = prepare_partial_data()
    _plot(data["count"], "count", CONFIG)
    _plot(data["rate"], "rate", CONFIG)
    _plot(partial["count"], "count", PARTIAL_CONFIG)
    _plot(partial["rate"], "rate", PARTIAL_CONFIG)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
