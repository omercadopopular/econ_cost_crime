"""Build and validate the quantitative ledger for report Sections 3--5.

Every empirical statement is recalculated from the figure-ready CSV files. The
module uses only the Python standard library, like the main workbook validator.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
FIGURE_DATA = ROOT / "data" / "figure_data"
INTERIM_DATA = ROOT / "data" / "interim"
DEFAULT_LEDGER = ROOT / "data" / "audit" / "report_sections_3_5_claims.csv"
REPORT = ROOT / "docs" / "report.md"


def _read(name: str) -> list[dict[str, str]]:
    path = FIGURE_DATA / name
    if not path.exists() or path.stat().st_size == 0:
        raise FileNotFoundError(f"Missing or empty figure-ready dataset: {path}")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _read_interim(name: str) -> list[dict[str, str]]:
    path = INTERIM_DATA / name
    if not path.exists() or path.stat().st_size == 0:
        raise FileNotFoundError(f"Missing or empty interim dataset: {path}")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _num(row: dict[str, str], column: str) -> float:
    return float(row[column])


def _unique_number(rows: Iterable[dict[str, str]], column: str) -> float:
    values = {float(row[column]) for row in rows if row[column] != ""}
    if len(values) != 1:
        raise AssertionError(f"Expected one value in {column}; found {values!r}")
    return values.pop()


def _key_unique(rows: Iterable[dict[str, str]], columns: tuple[str, ...]) -> None:
    keys = [tuple(row[column] for column in columns) for row in rows]
    if len(keys) != len(set(keys)):
        raise AssertionError(f"Duplicate key for {columns}")


def _quantile(values: Iterable[float], probability: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise AssertionError("Cannot calculate a quantile of an empty series")
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def _correlation(xs: Iterable[float], ys: Iterable[float]) -> float:
    x = list(xs)
    y = list(ys)
    if len(x) != len(y) or len(x) < 2:
        raise AssertionError("Correlation inputs must have the same nontrivial length")
    mean_x = statistics.fmean(x)
    mean_y = statistics.fmean(y)
    numerator = sum((a - mean_x) * (b - mean_y) for a, b in zip(x, y))
    denominator = math.sqrt(sum((a - mean_x) ** 2 for a in x) * sum((b - mean_y) ** 2 for b in y))
    if denominator == 0:
        raise AssertionError("Correlation is undefined for a constant input")
    return numerator / denominator


def _weighted_slope(xs: Iterable[float], ys: Iterable[float], weights: Iterable[float]) -> float:
    x = list(xs)
    y = list(ys)
    w = list(weights)
    if len(x) != len(y) or len(x) != len(w) or len(x) < 2 or any(value <= 0 for value in w):
        raise AssertionError("Weighted-regression inputs must have equal length and positive weights")
    total_weight = sum(w)
    mean_x = sum(weight * value for weight, value in zip(w, x)) / total_weight
    mean_y = sum(weight * value for weight, value in zip(w, y)) / total_weight
    numerator = sum(weight * (a - mean_x) * (b - mean_y) for a, b, weight in zip(x, y, w))
    denominator = sum(weight * (a - mean_x) ** 2 for a, weight in zip(x, w))
    if denominator == 0:
        raise AssertionError("Weighted slope is undefined for a constant regressor")
    return numerator / denominator


def _pt(value: float, decimals: int = 1) -> str:
    return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _add(
    rows: list[dict[str, object]],
    section: str,
    claim: str,
    value: float | int,
    display: str,
    source: str,
    calculation: str,
) -> None:
    rows.append({"section": section, "claim": claim, "value": value, "display": display,
                 "source": source, "calculation": calculation})


def _rows_for(rows: Iterable[dict[str, str]], **criteria: object) -> list[dict[str, str]]:
    return [row for row in rows if all(row[column] == str(value) for column, value in criteria.items())]


def build_ledger() -> tuple[list[dict[str, object]], dict[str, object]]:
    claims: list[dict[str, object]] = []
    diagnostics: dict[str, object] = {}

    world = _read("fig_01_distribuicao_mundial_homicidios.csv")
    _key_unique(world, ("year", "iso3"))
    years = {int(row["year"]) for row in world}
    assert years == {2016, 2024}
    year_units = {year: len({row["iso3"] for row in world if int(row["year"]) == year}) for year in years}
    assert len(set(year_units.values())) == 1 and min(year_units.values()) >= 80
    brazil = sorted((row for row in world if row["is_brazil"] == "1"), key=lambda row: int(row["year"]))
    assert len(brazil) == 2
    for row in brazil:
        year = row["year"]
        rate = _num(row, "homicide_rate_per_100k")
        percentile = _num(row, "percentile_unweighted")
        _add(claims, "3.1", f"Brazil homicide rate, {year}", rate, _pt(rate),
             "fig_01_distribuicao_mundial_homicidios.csv", "Official UNODC annual rate for Brazil")
        _add(claims, "3.1", f"Brazil percentile, {year}", percentile, _pt(percentile),
             "fig_01_distribuicao_mundial_homicidios.csv", "Unweighted average-rank percentile")
    common_units = len({row["iso3"] for row in world})
    _add(claims, "3.1", "UNODC 2016/2024 common reporting-unit sample", common_units, str(common_units),
         "fig_01_distribuicao_mundial_homicidios.csv", "Distinct common ISO3 units")

    crimes = _read("fig_02a_crimes_registrados.csv")
    rates = _read("fig_02b_taxas_criminalidade.csv")
    prop = _read("fig_02d_taxas_cobertura_parcial.csv")
    _key_unique(crimes, ("year", "crime"))
    _key_unique(rates, ("year", "crime"))
    crime_keys = {(row["year"], row["crime"]) for row in crimes}
    rate_keys = {(row["year"], row["crime"]) for row in rates}
    assert crime_keys == rate_keys
    rate_lookup = {(row["year"], row["crime"]): row for row in rates}
    assert all(math.isclose(_num(row, "count"), _num(rate_lookup[(row["year"], row["crime"])], "count")) for row in crimes)
    for crime in sorted({row["crime"] for row in crimes}):
        block = sorted(_rows_for(crimes, crime=crime), key=lambda row: int(row["year"]))
        start, end = block[0], block[-1]
        change_pct = 100 * (_num(end, "count") / _num(start, "count") - 1)
        _add(claims, "3.2", f"{crime}: count change, 2016--2025", change_pct, _pt(change_pct),
             "fig_02a_crimes_registrados.csv", "100 * (count_2025 / count_2016 - 1)")
        for endpoint in (start, end):
            count_thousand = _num(endpoint, "count") / 1_000
            _add(claims, "3.2", f"{crime}: count in thousands, {endpoint['year']}",
                 count_thousand, _pt(count_thousand), "fig_02a_crimes_registrados.csv",
                 "Reported victims / 1,000")
        absolute_change_thousand = (_num(end, "count") - _num(start, "count")) / 1_000
        _add(claims, "3.2", f"{crime}: absolute count change in thousands, 2016--2025",
             absolute_change_thousand, _pt(absolute_change_thousand),
             "fig_02a_crimes_registrados.csv", "(count_2025 - count_2016) / 1,000")
        if crime == "Homicídio doloso":
            for endpoint in (start, end):
                value = _num(endpoint, "rate_per_100k")
                _add(claims, "3.2", f"Homicídio doloso rate, {endpoint['year']}", value, _pt(value),
                     "fig_02b_taxas_criminalidade.csv", "Sinesp count / matched IBGE population")
    for crime in ["Roubo de veículo", "Roubo de carga"]:
        block = sorted(_rows_for(prop, crime=crime), key=lambda row: int(row["year"]))
        start, end = block[0], block[-1]
        change_pct = 100 * (_num(end, "rate_per_100k") / _num(start, "rate_per_100k") - 1)
        _add(claims, "3.2", f"{crime}: partial-panel rate change, 2016--2025", change_pct, _pt(change_pct),
             "fig_02d_taxas_cobertura_parcial.csv",
             "100 * (rate_2025 / rate_2016 - 1), indicator-specific fixed UF panel")
    for crime in sorted({row["crime"] for row in prop}):
        block = _rows_for(prop, crime=crime)
        reporting_ufs = int(_unique_number(block, "reporting_ufs"))
        coverage_2025 = _num(_rows_for(block, year=2025)[0], "population_coverage_pct")
        _add(claims, "3.2", f"{crime}: balanced-panel UFs", reporting_ufs, str(reporting_ufs),
             "fig_02d_taxas_cobertura_parcial.csv", "Distinct UFs in the indicator-specific panel")
        _add(claims, "3.2", f"{crime}: population coverage, 2025", coverage_2025,
             _pt(coverage_2025), "fig_02d_taxas_cobertura_parcial.csv",
             "IBGE population share in the indicator-specific fixed UF panel")

    micro = _read("fig_03_microrregion_homicides.csv")
    change = _read("fig_04_microrregion_homicide_change.csv")
    _key_unique(micro, ("microrregion_code",))
    _key_unique(change, ("microrregion_code",))
    assert len(micro) == len(change) == 558
    micro_rates = [_num(row, "homicide_rate_per_100k") for row in micro]
    for probability, label in [(0.25, "first quartile"), (0.5, "median"), (0.75, "third quartile"), (0.9, "90th percentile")]:
        value = _quantile(micro_rates, probability)
        _add(claims, "3.3", f"Microrregion homicide-rate {label}, 2024", value, _pt(value),
             "fig_03_microrregion_homicides.csv", f"Unweighted cross-sectional quantile {probability}")
    first_quartile_cutoff = _quantile(micro_rates, 0.25)
    third_quartile_cutoff = _quantile(micro_rates, 0.75)
    bottom_quartile_mean = statistics.fmean(value for value in micro_rates if value <= first_quartile_cutoff)
    top_quartile_mean = statistics.fmean(value for value in micro_rates if value >= third_quartile_cutoff)
    _add(claims, "3.3", "Mean homicide rate in bottom microrregion quartile, 2024",
         bottom_quartile_mean, _pt(bottom_quartile_mean),
         "fig_03_microrregion_homicides.csv", "Unweighted mean among rates at or below Q1")
    _add(claims, "3.3", "Mean homicide rate in top microrregion quartile, 2024",
         top_quartile_mean, _pt(top_quartile_mean),
         "fig_03_microrregion_homicides.csv", "Unweighted mean among rates at or above Q3")

    unodc_panel = _read_interim("unodc_homicide_country_year.csv")
    for iso3, country in [("USA", "United States"), ("HTI", "Haiti")]:
        comparison = _rows_for(unodc_panel, iso3=iso3, year=2023)
        if len(comparison) != 1:
            raise AssertionError(f"Expected one retained UNODC observation for {iso3} in 2023")
        value = _num(comparison[0], "homicide_rate_per_100k")
        _add(claims, "3.3", f"UNODC homicide rate, 2023: {country}", value, _pt(value),
             "unodc_homicide_country_year.csv", "Official retained UNODC annual rate")
    _add(claims, "3.3", "Microrregions in fixed geography", len(micro), str(len(micro)),
         "fig_03_microrregion_homicides.csv", "Distinct microrregion codes")
    high_micro = sum(value >= 40 for value in micro_rates)
    _add(claims, "3.3", "Microrregions at or above 40 per 100k", high_micro, str(high_micro),
         "fig_03_microrregion_homicides.csv", "Count with rate >= 40")
    labels = {
        "São Paulo": "São Paulo",
        "Brasília": "Brasília",
        "Rio de Janeiro": "Rio de Janeiro",
        "São Luís": "Aglomeração Urbana de São Luís",
        "Fortaleza": "Fortaleza",
        "Recife": "Recife",
        "Salvador": "Salvador",
    }
    diagnostics["figure_3_labels"] = {
        display: _num(_rows_for(micro, microrregion_name=source)[0], "homicide_rate_per_100k")
        for display, source in labels.items()
    }
    for display, value in diagnostics["figure_3_labels"].items():
        _add(claims, "3.3", f"Highlighted microrregion rate: {display}", value, _pt(value),
             "fig_03_microrregion_homicides.csv", "Homicide count / population * 100,000")
    deltas = [_num(row, "delta_rate_per_100k") for row in change]
    smooth_deltas = [_num(row, "delta_average_rate_per_100k") for row in change]
    median_delta = statistics.median(deltas)
    falling_share = 100 * sum(value < 0 for value in deltas) / len(deltas)
    smooth_corr = _correlation(deltas, smooth_deltas)
    same_sign = 100 * sum((a > 0) == (b > 0) for a, b in zip(deltas, smooth_deltas)) / len(deltas)
    _add(claims, "3.4", "Median microrregion homicide-rate change, 2016--2024", median_delta, _pt(median_delta),
         "fig_04_microrregion_homicide_change.csv", "Unweighted median of end minus start rate")
    _add(claims, "3.4", "Microrregions with declining endpoint rate", falling_share, _pt(falling_share),
         "fig_04_microrregion_homicide_change.csv", "100 * count(delta < 0) / 558")
    _add(claims, "3.4", "Endpoint versus smoothed-change correlation", smooth_corr, _pt(smooth_corr, 3),
         "fig_04_microrregion_homicide_change.csv", "Pearson correlation across 558 microrregions")
    _add(claims, "3.4", "Endpoint and smoothed change with same sign", same_sign, _pt(same_sign),
         "fig_04_microrregion_homicide_change.csv", "Share with identical sign")
    regional_deltas: dict[str, list[float]] = defaultdict(list)
    for row in change:
        regional_deltas[row["macroregion"]].append(_num(row, "delta_rate_per_100k"))
    diagnostics["macroregion_change"] = {
        region: {"n": len(values), "median": statistics.median(values), "mean": statistics.fmean(values),
                 "declining": 100 * sum(value < 0 for value in values) / len(values)}
        for region, values in regional_deltas.items()
    }

    convergence = _read("fig_05_microrregion_homicide_convergence.csv")
    _key_unique(convergence, ("microrregion_code",))
    assert len(convergence) == 558
    convergence_slope = _weighted_slope(
        (_num(row, "rate_2016_per_100k") for row in convergence),
        (_num(row, "delta_rate_2016_2024_per_100k") for row in convergence),
        (_num(row, "population_2016") for row in convergence),
    )
    _add(claims, "3.4", "Population-weighted convergence slope, 2016--2024", convergence_slope,
         _pt(convergence_slope, 2), "fig_05_microrregion_homicide_convergence.csv",
         "Population-weighted OLS slope of endpoint rate change on 2016 homicide rate")

    national_files = {
        "seguranca_publica": "fig_06_public_security.csv",
        "seguranca_privada": "fig_07_private_security.csv",
        "encarceramento": "fig_08_incarceration.csv",
        "seguros_perdas": "fig_09_insurance_material_losses.csv",
        "perda_produtiva": "fig_10_productive_capacity.csv",
        "custos_judiciais": "fig_11_judicial_costs.csv",
        "servicos_medicos": "fig_12_medical_costs.csv",
        "total": "fig_13_total_costs.csv",
    }
    national_summary: dict[str, object] = {}
    for key, filename in national_files.items():
        frame = _read(filename)
        _key_unique(frame, ("ano", "componente"))
        years = sorted({int(row["ano"]) for row in frame})
        summary: dict[str, object] = {}
        for year in [years[0], 2015, years[-1]]:
            block = _rows_for(frame, ano=year)
            if not block:
                continue
            total_value = _unique_number(block, "total_reportado_reais_dez_2025")
            gdp = _unique_number(block, "pib_reais_dez_2025")
            summary[str(year)] = {"total_billion": total_value / 1e9, "gdp_share_pct": 100 * total_value / gdp,
                                  "components": {row["componente"]: _num(row, "composicao_pct") for row in block}}
            if year == years[-1]:
                for component_row in block:
                    component_share = _num(component_row, "composicao_pct")
                    _add(claims, "4", f"{key}: {year} composition: {component_row['componente']}",
                         component_share, _pt(component_share), filename,
                         "100 * component / component-group total")
        national_summary[key] = summary
        start = _rows_for(frame, ano=years[0])
        end = _rows_for(frame, ano=years[-1])
        start_total = _unique_number(start, "total_reportado_reais_dez_2025")
        end_total = _unique_number(end, "total_reportado_reais_dez_2025")
        start_share = 100 * start_total / _unique_number(start, "pib_reais_dez_2025")
        end_share = 100 * end_total / _unique_number(end, "pib_reais_dez_2025")
        for label, value, display, formula in [
            (f"{key}: real level, {years[0]}", start_total / 1e9, _pt(start_total / 1e9), "Reported total / 1e9"),
            (f"{key}: real level, {years[-1]}", end_total / 1e9, _pt(end_total / 1e9), "Reported total / 1e9"),
            (f"{key}: GDP share, {years[0]}", start_share, _pt(start_share), "100 * reported total / GDP"),
            (f"{key}: GDP share, {years[-1]}", end_share, _pt(end_share), "100 * reported total / GDP"),
            (f"{key}: real growth, {years[0]}--{years[-1]}", 100 * (end_total / start_total - 1),
             _pt(100 * (end_total / start_total - 1)), "100 * (end / start - 1)"),
        ]:
            _add(claims, "4", label, value, display, filename, formula)
        totals_by_year = {
            year: _unique_number(_rows_for(frame, ano=year), "total_reportado_reais_dez_2025")
            for year in years
        }
        peak_year = max(totals_by_year, key=totals_by_year.get)
        _add(claims, "4", f"{key}: real peak year", peak_year, str(peak_year), filename,
             "Year with maximum reported real total")
        _add(claims, "4", f"{key}: real peak level", totals_by_year[peak_year] / 1e9,
             _pt(totals_by_year[peak_year] / 1e9), filename,
             "Maximum reported total / 1e9")
    diagnostics["national_summary"] = national_summary

    total = _read("fig_13_total_costs.csv")
    for year in [1996, 2015, 2025]:
        block = _rows_for(total, ano=year)
        reported = _unique_number(block, "total_reportado_reais_dez_2025")
        share = 100 * reported / _unique_number(block, "pib_reais_dez_2025")
        _add(claims, "4.7", f"Total measured cost, {year}", reported / 1e9, _pt(reported / 1e9),
             "fig_13_total_costs.csv", "Reported accounting total / 1e9")
        _add(claims, "4.7", f"Total measured cost GDP share, {year}", share, _pt(share),
             "fig_13_total_costs.csv", "100 * total / GDP")
    total_2025 = sorted(_rows_for(total, ano=2025), key=lambda row: _num(row, "composicao_pct"), reverse=True)
    diagnostics["total_2025_composition"] = [
        {"component": row["componente"], "value": _num(row, "valor_reais_dez_2025"),
         "gdp_share": _num(row, "participacao_pib_pct"), "composition": _num(row, "composicao_pct")}
        for row in total_2025
    ]
    for row in total_2025:
        value = _num(row, "composicao_pct")
        _add(claims, "4.7", f"2025 total composition: {row['componente']}", value, _pt(value),
             "fig_13_total_costs.csv", "100 * component / seven-component total")
    cumulative_total = sum(
        _unique_number(_rows_for(total, ano=year), "total_reportado_reais_dez_2025")
        for year in sorted({int(row["ano"]) for row in total})
    )
    _add(claims, "4.7", "Cumulative measured cost, 1996--2025, R$ trillion", cumulative_total / 1e12,
         _pt(cumulative_total / 1e12), "fig_13_total_costs.csv", "Sum of annual reported totals / 1e12")
    productive_2025 = _rows_for(_read("fig_10_productive_capacity.csv"), ano=2025)
    productive_average = (
        _unique_number(productive_2025, "total_reportado_reais_dez_2025")
        / _unique_number(productive_2025, "total_de_homicidios")
        / 1_000
    )
    _add(claims, "4.4", "Average modeled productive loss per homicide, 2025, R$ thousand",
         productive_average, _pt(productive_average), "fig_10_productive_capacity.csv",
         "Reported productive loss / homicide count / 1,000")
    medical_2025 = _rows_for(_read("fig_12_medical_costs.csv"), ano=2025)
    medical_total = _unique_number(medical_2025, "total_reportado_reais_dez_2025")
    medical_gdp_share = 100 * medical_total / _unique_number(medical_2025, "pib_reais_dez_2025")
    medical_total_share = _num(_rows_for(total, ano=2025, componente="Serviços médico-terapêuticos")[0], "composicao_pct")
    _add(claims, "4.6", "Medical costs, 2025, R$ million", medical_total / 1e6, _pt(medical_total / 1e6),
         "fig_12_medical_costs.csv", "Reported total / 1e6")
    _add(claims, "4.6", "Medical costs GDP share, 2025", medical_gdp_share, _pt(medical_gdp_share, 3),
         "fig_12_medical_costs.csv", "100 * reported total / GDP")
    _add(claims, "4.6", "Medical share of total measured costs, 2025", medical_total_share,
         _pt(medical_total_share, 2), "fig_13_total_costs.csv", "100 * component / accounting total")
    for year in (1998, 2015, 2025):
        medical_year = _rows_for(_read("fig_12_medical_costs.csv"), ano=year)
        admissions_thousand = _unique_number(medical_year, "internacoes_agressao") / 1_000
        _add(claims, "4.6", f"Violent-injury admissions, {year}, thousands", admissions_thousand,
             _pt(admissions_thousand), "fig_12_medical_costs.csv", "SIH/SUS admissions / 1,000")
    annual_totals: dict[int, tuple[float, float]] = {}
    for year in sorted({int(row["ano"]) for row in total}):
        block = _rows_for(total, ano=year)
        annual_totals[year] = (_unique_number(block, "total_reportado_reais_dez_2025"),
                               _unique_number(block, "pib_reais_dez_2025"))
    real_peak_year = max(annual_totals, key=lambda year: annual_totals[year][0])
    share_peak_year = max(annual_totals, key=lambda year: annual_totals[year][0] / annual_totals[year][1])
    share_min_year = min(annual_totals, key=lambda year: annual_totals[year][0] / annual_totals[year][1])
    diagnostics["total_turning_points"] = {
        "real_peak_year": real_peak_year, "real_peak_billion": annual_totals[real_peak_year][0] / 1e9,
        "share_peak_year": share_peak_year,
        "share_peak_pct": 100 * annual_totals[share_peak_year][0] / annual_totals[share_peak_year][1],
        "share_min_year": share_min_year,
        "share_min_pct": 100 * annual_totals[share_min_year][0] / annual_totals[share_min_year][1],
    }

    states = _read("fig_14_state_costs.csv")
    traj = _read("fig_15_state_trajectories.csv")
    assert {row["ano"] for row in states} == {"2025"}
    assert len({row["uf"] for row in states}) == 27
    _key_unique(states, ("uf", "componente"))
    state_totals = {row["uf"]: row for row in states}
    burdens = [_num(row, "custo_total_pib_pct") for row in state_totals.values()]
    gdppc = [_num(row, "pib_per_capita_reais_dez_2025") for row in state_totals.values()]
    for probability, label in [(0.25, "first quartile"), (0.5, "median"), (0.75, "third quartile")]:
        value = _quantile(burdens, probability)
        _add(claims, "5.1", f"State burden {label}, 2025", value, _pt(value),
             "fig_14_state_costs.csv", f"Unweighted cross-state quantile {probability}")
    state_corr = _correlation(gdppc, burdens)
    log_state_corr = _correlation((math.log(value) for value in gdppc), burdens)
    _add(claims, "5.1", "GDP per capita versus state burden correlation, 2025", state_corr, _pt(state_corr, 2),
         "fig_14_state_costs.csv", "Pearson correlation across 27 UFs")
    _add(claims, "5.1", "Log GDP per capita versus state burden correlation, 2025", log_state_corr,
         _pt(log_state_corr, 2), "fig_14_state_costs.csv", "Pearson correlation across 27 UFs")
    diagnostics["state_rankings"] = [
        {"uf": row["uf"], "gdp_per_capita": _num(row, "pib_per_capita_reais_dez_2025"),
         "burden": _num(row, "custo_total_pib_pct")}
        for row in sorted(state_totals.values(), key=lambda row: _num(row, "custo_total_pib_pct"), reverse=True)
    ]
    for rank_row in diagnostics["state_rankings"]:
        _add(claims, "5.1", f"State burden, 2025: {rank_row['uf']}", rank_row["burden"],
             _pt(rank_row["burden"]), "fig_14_state_costs.csv", "UF total / state GDP * 100")
    component_values: dict[str, list[float]] = defaultdict(list)
    for row in states:
        component_values[row["componente"]].append(_num(row, "participacao_pib_pct"))
    diagnostics["state_component_dispersion"] = {
        component: {"mean": statistics.fmean(values), "std": statistics.stdev(values),
                    "min": min(values), "max": max(values)}
        for component, values in sorted(component_values.items(), key=lambda item: statistics.stdev(item[1]), reverse=True)
    }

    _key_unique(traj, ("uf", "ano"))
    assert len({row["uf"] for row in traj}) == 27 and {row["ano"] for row in traj} == {"2016", "2025"}
    trajectory = {uf: {int(row["ano"]): row for row in traj if row["uf"] == uf} for uf in {row["uf"] for row in traj}}
    income_changes = {uf: _num(points[2025], "pib_per_capita_reais_dez_2025") - _num(points[2016], "pib_per_capita_reais_dez_2025")
                      for uf, points in trajectory.items()}
    burden_changes = {uf: _num(points[2025], "custo_total_pib_pct") - _num(points[2016], "custo_total_pib_pct")
                      for uf, points in trajectory.items()}
    start_income = [_num(trajectory[uf][2016], "pib_per_capita_reais_dez_2025") for uf in sorted(trajectory)]
    ordered_burden_changes = [burden_changes[uf] for uf in sorted(trajectory)]
    groups = {
        "income_up_burden_down": sorted(uf for uf in trajectory if income_changes[uf] > 0 and burden_changes[uf] < 0),
        "income_up_burden_up": sorted(uf for uf in trajectory if income_changes[uf] > 0 and burden_changes[uf] > 0),
        "income_down_burden_down": sorted(uf for uf in trajectory if income_changes[uf] < 0 and burden_changes[uf] < 0),
        "income_down_burden_up": sorted(uf for uf in trajectory if income_changes[uf] < 0 and burden_changes[uf] > 0),
    }
    diagnostics["state_trajectory_groups"] = groups
    for key, members in groups.items():
        _add(claims, "5.2", f"State trajectories: {key}", len(members), str(len(members)),
             "fig_15_state_trajectories.csv", "Count from each UF's 2016 and 2025 endpoints")
    median_burden_change = statistics.median(burden_changes.values())
    income_growth = [100 * (_num(points[2025], "pib_per_capita_reais_dez_2025") /
                            _num(points[2016], "pib_per_capita_reais_dez_2025") - 1)
                     for points in trajectory.values()]
    _add(claims, "5.2", "Median state burden change, 2016--2025", median_burden_change, _pt(median_burden_change),
         "fig_15_state_trajectories.csv", "Median UF-level end minus start burden")
    _add(claims, "5.2", "Median real GDP per capita growth, 2016--2025", statistics.median(income_growth),
         _pt(statistics.median(income_growth)), "fig_15_state_trajectories.csv", "Median UF-level growth")
    trajectory_corr = _correlation(start_income, ordered_burden_changes)
    _add(claims, "5.2", "Initial GDP per capita versus burden change correlation", trajectory_corr,
         _pt(trajectory_corr, 2), "fig_15_state_trajectories.csv",
         "Pearson correlation across UFs between 2016 real GDP per capita and 2016--2025 burden change")
    diagnostics["state_burden_changes"] = dict(sorted(burden_changes.items(), key=lambda item: item[1]))

    return claims, diagnostics


def validate_draft(claims: list[dict[str, object]], diagnostics: dict[str, object]) -> int:
    text = REPORT.read_text(encoding="utf-8")
    section = text.split("## 3.", 1)[1].split("## 6.", 1)[0]

    # Every decimal printed in the draft must be a reproducible rendering of a
    # claim, except for documented model parameters and ICD/subfunction codes.
    allowed: set[str] = {str(row["display"]).replace("-", "−") for row in claims}
    for row in claims:
        value = float(row["value"])
        for decimals in (1, 2, 3):
            allowed.add(_pt(value, decimals).replace("-", "−"))
            # A decline may be written as a positive magnitude after verbs such
            # as "recuou" or "diminuiu" rather than with a minus sign.
            allowed.add(_pt(abs(value), decimals))
    allowed.update({"1,86"})
    decimal_tokens = set(re.findall(r"(?<![\w])−?\d+(?:\.\d{3})*,\d+(?!\w)", section))
    unexplained = sorted(decimal_tokens - allowed)
    if unexplained:
        raise AssertionError(f"Draft contains decimal values absent from the quantitative ledger: {unexplained}")

    required_fragments = [
        "amostra harmonizada de 87 países ou territórios",
        "30,1 homicídios por 100 mil habitantes",
        "percentil 91,9",
        "18,7 e o país passou ao percentil 86,0",
        "25,1 para 14,8 vítimas por 100 mil habitantes",
        "22 UFs e 87,8% da população brasileira em 2025",
        "20 UFs e, respectivamente, 85,3% e 86,0% da população",
        "558 microrregiões",
        "70,3% das microrregiões",
        "variação 0,50 ponto mais negativa",
        "R$ 715,4 mil por homicídio",
        "52,8 mil em 2025",
        "R$ 439,5 bilhões",
        "aproximadamente R$ 10,0 trilhões",
        "equivalentes a 3,5% do PIB",
        "Amapá e Acre aparecem no topo",
        "Santa Catarina e o Distrito Federal ficam próximos de 2%",
        "foi −0,78",
        "Em 19 UFs, a renda aumentou e a carga do crime caiu",
        "nas outras oito, a renda aumentou e a carga subiu",
        "Acre, Amazonas, Bahia, Ceará, Paraíba, Pernambuco, Piauí e Roraima",
    ]
    missing = [fragment for fragment in required_fragments if fragment not in section]
    if missing:
        raise AssertionError(f"Expected verified draft fragments not found: {missing}")

    # Programmatic ranking and direction checks supporting qualitative prose.
    ranking = diagnostics["state_rankings"]
    assert [row["uf"] for row in ranking[:2]] == ["AP", "AC"]
    assert [row["uf"] for row in ranking[-3:]] == ["SP", "DF", "SC"]
    assert diagnostics["state_trajectory_groups"]["income_up_burden_up"] == ["AC", "AM", "BA", "CE", "PB", "PE", "PI", "RR"]
    assert list(diagnostics["state_burden_changes"])[:3] == ["GO", "TO", "RN"]
    assert [item["component"] for item in diagnostics["total_2025_composition"][:4]] == [
        "Segurança pública", "Seguros e perdas materiais", "Custos judiciais", "Segurança privada"
    ]
    print(f"PASS: {len(decimal_tokens)} distinct decimal renderings in Sections 3--5 reconcile with the ledger")
    print("PASS: state rankings, trajectory groups and 2025 national component ordering match the draft")
    return len(decimal_tokens)


def write_ledger(rows: list[dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["section", "claim", "value", "display", "source", "calculation"])
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger-out", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--diagnostics", action="store_true")
    parser.add_argument("--check-draft", action="store_true")
    args = parser.parse_args()
    claims, diagnostics = build_ledger()
    write_ledger(claims, args.ledger_out)
    print(f"PASS: {len(claims)} quantitative claims recalculated from figure-ready data")
    print(f"Ledger: {args.ledger_out}")
    if args.diagnostics:
        print(json.dumps(diagnostics, ensure_ascii=False, indent=2))
    if args.check_draft:
        validate_draft(claims, diagnostics)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
