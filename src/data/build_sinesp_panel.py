"""Build the audited Sinesp UF and national panels used by Figure 2."""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime, timedelta
import json
from pathlib import Path
import unicodedata
from typing import Any, Iterable, Mapping, Sequence

from .external_config import (
    AUDIT_DIR,
    IBGE_PROJECTION_PATH,
    INTERIM_DIR,
    SINESP_DIR,
    SINESP_YEARS,
)
from .xlsx_stream import iter_rows


ANO_INICIAL_SINESP = 2016
ANO_FINAL_SINESP = 2025
FIGURE_YEARS = tuple(range(ANO_INICIAL_SINESP, ANO_FINAL_SINESP + 1))

UF_CODES = (
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT",
    "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO",
)


CANDIDATES: dict[str, dict[str, str]] = {
    "Homicídio doloso": {
        "event": "homicidio doloso",
        "field": "total_vitima",
        "concept": "vítimas",
        "classification": "COMPARABLE",
        "definition": "Vítimas de homicídio doloso segundo a definição do Sinesp VDE.",
    },
    "Latrocínio": {
        "event": "roubo seguido de morte (latrocinio)",
        "field": "total_vitima",
        "concept": "vítimas",
        "classification": "COMPARABLE",
        "definition": "Vítimas de roubo seguido de morte (latrocínio).",
    },
    "Tentativa de homicídio": {
        "event": "tentativa de homicidio",
        "field": "total_vitima",
        "concept": "vítimas",
        "classification": "COMPARABLE",
        "definition": "Vítimas de homicídio tentado; linhas repetidas no mesmo mês são somadas.",
    },
    "Furto de veículo": {
        "event": "furto de veiculo",
        "field": "total",
        "concept": "ocorrências",
        "classification": "LIMITED_COVERAGE",
        "definition": "Ocorrências de furto de veículo automotor completo.",
    },
    "Roubo de veículo": {
        "event": "roubo de veiculo",
        "field": "total",
        "concept": "ocorrências",
        "classification": "LIMITED_COVERAGE",
        "definition": "Ocorrências de roubo de veículo automotor completo.",
    },
    "Roubo de carga": {
        "event": "roubo de carga",
        "field": "total",
        "concept": "ocorrências",
        "classification": "LIMITED_COVERAGE",
        "definition": "Ocorrências de roubo de carga transportada.",
    },
    "Roubo a instituição financeira": {
        "event": "roubo a instituicao financeira",
        "field": "total",
        "concept": "ocorrências",
        "classification": "LIMITED_COVERAGE",
        "definition": "Ocorrências de roubo a instituição financeira, inclusive caixas eletrônicos.",
    },
    "Estupro": {
        "event": "estupro",
        "field": "total_vitima",
        "concept": "vítimas",
        "classification": "COMPARABLE",
        "definition": "Vítimas no indicador Estupro, mantido separado de estupro de vulnerável.",
    },
    "Estupro de vulnerável": {
        "event": "estupro de vulneravel",
        "field": "total_vitima",
        "concept": "vítimas",
        "classification": "COMPARABLE",
        "definition": "Vítimas no detalhamento separado de estupro de vulnerável.",
    },
    "Feminicídio": {
        "event": "feminicidio",
        "field": "total_vitima",
        "concept": "vítimas",
        "classification": "COMPARABLE_WITH_BREAK",
        "definition": "Vítimas classificadas como feminicídio; categoria legal e reporte em consolidação.",
    },
    "Tráfico de drogas": {
        "event": "trafico de drogas",
        "field": "total",
        "concept": "ocorrências de fiscalização",
        "classification": "NOT_COMPARABLE",
        "definition": "Boletins classificados como tráfico; reflete crime registrado e atividade policial.",
    },
    "Armas de fogo apreendidas": {
        "event": "arma de fogo apreendida",
        "field": "total",
        "concept": "objetos apreendidos",
        "classification": "NOT_COMPARABLE",
        "definition": "Quantidade de armas de fogo apreendidas; não é ocorrência nem vítima.",
    },
}

SELECTED_CRIMES = (
    "Homicídio doloso",
    "Latrocínio",
    "Tentativa de homicídio",
    "Estupro",
    "Estupro de vulnerável",
    "Feminicídio",
)

# These occurrence indicators are useful, but they do not have complete 27-UF
# coverage. Figures 2C/2D use a separate time-balanced UF sample for each
# indicator, maximizing coverage without changing geography within a series.
PARTIAL_COVERAGE_CRIMES = (
    "Furto de veículo",
    "Roubo de veículo",
    "Roubo de carga",
    "Roubo a instituição financeira",
)

POPULATION_PATH = INTERIM_DIR / "ibge_population_uf_2015_2025.csv"
COVERAGE_PATH = INTERIM_DIR / "sinesp_category_coverage.csv"
UF_PANEL_PATH = INTERIM_DIR / "sinesp_uf_year_crime.csv"
NATIONAL_PANEL_PATH = INTERIM_DIR / "sinesp_national_year_crime.csv"
PARTIAL_NATIONAL_PANEL_PATH = INTERIM_DIR / "sinesp_partial_coverage_panel.csv"
AUDIT_PATH = AUDIT_DIR / "sinesp_build_audit.json"


def _normalized(value: object | None) -> str:
    text = "" if value is None else str(value).strip().casefold()
    decomposed = unicodedata.normalize("NFKD", text)
    return " ".join("".join(char for char in decomposed if not unicodedata.combining(char)).split())


EVENT_TO_CRIME = {spec["event"]: crime for crime, spec in CANDIDATES.items()}


def _number(value: object | None) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return float(int(value))
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(".", "").replace(",", ".")
    return float(text) if text else None


def _excel_date(value: object) -> datetime:
    number = _number(value)
    if number is None:
        raise ValueError(f"Missing Sinesp reference date: {value!r}")
    return datetime(1899, 12, 30) + timedelta(days=number)


def _write_csv(path: Path, rows: Iterable[Mapping[str, Any]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    materialized = list(rows)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="raise")
        writer.writeheader()
        writer.writerows(materialized)
    temp.replace(path)


def build_population() -> dict[tuple[str, int], float]:
    rows = iter_rows(IBGE_PROJECTION_PATH)
    header: list[object | None] | None = None
    for row in rows:
        if row and _normalized(row[0]) == "idade":
            header = row
            break
    if header is None:
        raise ValueError("IBGE population header row was not found.")
    year_columns = {int(value): index for index, value in enumerate(header) if isinstance(value, int)}
    missing_years = set(SINESP_YEARS) - set(year_columns)
    if missing_years:
        raise ValueError(f"IBGE projection lacks years: {sorted(missing_years)}")
    population: dict[tuple[str, int], float] = defaultdict(float)
    seen_age_keys: set[tuple[str, str, object]] = set()
    for row in rows:
        if len(row) < 5:
            continue
        age, sex, _code, uf = row[:4]
        if uf not in UF_CODES or _normalized(sex) != "ambos":
            continue
        age_key = (str(uf), str(sex), age)
        if age_key in seen_age_keys:
            raise ValueError(f"Duplicate IBGE population age row: {age_key}")
        seen_age_keys.add(age_key)
        for year in SINESP_YEARS:
            value = _number(row[year_columns[year]] if len(row) > year_columns[year] else None)
            if value is None or value < 0:
                raise ValueError(f"Invalid IBGE population for {uf}, age={age}, year={year}: {value}")
            population[(str(uf), year)] += value
    expected = {(uf, year) for uf in UF_CODES for year in SINESP_YEARS}
    if set(population) != expected or any(value <= 0 for value in population.values()):
        raise ValueError("IBGE population panel is incomplete or contains nonpositive totals.")
    output = [
        {
            "uf": uf,
            "year": year,
            "population": int(round(population[(uf, year)])),
            "source": "IBGE Projeções da População, Revisão 2024, população em 1º de julho",
            "status": "estimativa/projeção revisada",
        }
        for year in SINESP_YEARS
        for uf in UF_CODES
    ]
    _write_csv(POPULATION_PATH, output, ("uf", "year", "population", "source", "status"))
    return population


def scan_sinesp() -> tuple[dict[tuple[str, int, str, int], dict[str, Any]], dict[str, Any]]:
    monthly: dict[tuple[str, int, str, int], dict[str, Any]] = {}
    raw_labels: dict[tuple[str, int], set[str]] = defaultdict(set)
    non_state_rows: dict[tuple[str, int], int] = defaultdict(int)
    rows_by_year: dict[int, int] = defaultdict(int)
    for year in SINESP_YEARS:
        path = SINESP_DIR / f"bancovde-{year}.xlsx"
        iterator = iter_rows(path)
        header = next(iterator)
        expected_headers = {
            "uf", "evento", "data_referencia", "total_vitima", "total", "abrangencia"
        }
        index = {str(value): position for position, value in enumerate(header) if value is not None}
        if not expected_headers.issubset(index):
            raise ValueError(f"Unexpected Sinesp schema in {path}: {header}")
        for row in iterator:
            rows_by_year[year] += 1
            event_raw = row[index["evento"]] if len(row) > index["evento"] else None
            crime = EVENT_TO_CRIME.get(_normalized(event_raw))
            if crime is None:
                continue
            uf = str(row[index["uf"]]).strip() if len(row) > index["uf"] else ""
            if uf not in UF_CODES:
                raise ValueError(f"Unexpected UF in {path}: {uf!r}")
            scope = _normalized(row[index["abrangencia"]] if len(row) > index["abrangencia"] else None)
            if scope != "estadual":
                non_state_rows[(crime, year)] += 1
                continue
            date = _excel_date(row[index["data_referencia"]])
            if date.year != year:
                raise ValueError(f"Sinesp date/file year mismatch: file={year}, date={date:%Y-%m-%d}")
            spec = CANDIDATES[crime]
            value_index = index[spec["field"]]
            value = _number(row[value_index] if len(row) > value_index else None)
            key = (uf, year, crime, date.month)
            bucket = monthly.setdefault(
                key,
                {"value": 0.0, "numeric_rows": 0, "source_rows": 0, "labels": set()},
            )
            bucket["source_rows"] += 1
            bucket["labels"].add(str(event_raw))
            raw_labels[(crime, year)].add(str(event_raw))
            if value is not None:
                if value < 0:
                    raise ValueError(f"Negative Sinesp value at {key}: {value}")
                bucket["value"] += value
                bucket["numeric_rows"] += 1
    audit = {
        "rows_scanned_by_year": dict(sorted(rows_by_year.items())),
        "raw_labels_by_crime_year": {
            f"{crime}|{year}": sorted(labels)
            for (crime, year), labels in sorted(raw_labels.items())
        },
        "excluded_non_state_rows": {
            f"{crime}|{year}": count
            for (crime, year), count in sorted(non_state_rows.items())
        },
    }
    return monthly, audit


def build_panels(
    monthly: dict[tuple[str, int, str, int], dict[str, Any]],
    population: dict[tuple[str, int], float],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, list[str]],
]:
    coverage_rows: list[dict[str, Any]] = []
    uf_rows: list[dict[str, Any]] = []
    complete: dict[tuple[str, int, str], dict[str, Any]] = {}
    for crime, spec in CANDIDATES.items():
        for year in SINESP_YEARS:
            for uf in UF_CODES:
                buckets = [monthly[(uf, year, crime, month)] for month in range(1, 13) if (uf, year, crime, month) in monthly]
                months_present = len(buckets)
                months_numeric = sum(bucket["numeric_rows"] > 0 for bucket in buckets)
                if months_present == 0:
                    status = "NOT_REPORTED"
                    count: float | None = None
                elif months_present == 12 and months_numeric == 12:
                    status = "FULL_12_MONTHS"
                    count = sum(float(bucket["value"]) for bucket in buckets)
                else:
                    status = "PARTIAL_MONTHS"
                    count = sum(float(bucket["value"]) for bucket in buckets)
                labels = sorted({label for bucket in buckets for label in bucket["labels"]})
                definition_flag = (
                    "separate_victim_indicator"
                    if crime in {"Estupro", "Estupro de vulnerável"}
                    else "legal_category_adoption"
                    if crime == "Feminicídio"
                    else "standard_vde_indicator"
                )
                coverage_rows.append(
                    {
                        "crime": crime,
                        "year": year,
                        "uf": uf,
                        "reporting_status": status,
                        "months_present": months_present,
                        "months_numeric": months_numeric,
                        "count_reported": "" if count is None else int(round(count)),
                        "measurement_concept": spec["concept"],
                        "value_field": spec["field"],
                        "raw_labels": " | ".join(labels),
                        "definition_version_flag": definition_flag,
                        "comparability_class": spec["classification"],
                    }
                )
                if status == "FULL_12_MONTHS":
                    value = float(count)
                    pop = population[(uf, year)]
                    complete[(uf, year, crime)] = {"count": value, "population": pop}
                    uf_rows.append(
                        {
                            "uf": uf,
                            "year": year,
                            "crime": crime,
                            "count": int(round(value)),
                            "population": int(round(pop)),
                            "rate_per_100k": 100000.0 * value / pop,
                            "measurement_concept": spec["concept"],
                            "reporting_status": status,
                            "comparability_class": spec["classification"],
                            "definition_version_flag": definition_flag,
                        }
                    )
    balanced_ufs: dict[str, list[str]] = {}
    national_rows: list[dict[str, Any]] = []
    for crime, spec in CANDIDATES.items():
        sample = [
            uf for uf in UF_CODES if all((uf, year, crime) in complete for year in FIGURE_YEARS)
        ]
        balanced_ufs[crime] = sample
        for year in SINESP_YEARS:
            reported = [uf for uf in UF_CODES if (uf, year, crime) in complete]
            raw_count = sum(complete[(uf, year, crime)]["count"] for uf in reported)
            raw_pop = sum(population[(uf, year)] for uf in reported)
            sample_available = all((uf, year, crime) in complete for uf in sample)
            sample_count = (
                sum(complete[(uf, year, crime)]["count"] for uf in sample)
                if sample_available and sample
                else None
            )
            sample_pop = sum(population[(uf, year)] for uf in sample) if sample else None
            brazil_pop = sum(population[(uf, year)] for uf in UF_CODES)
            national_rows.append(
                {
                    "crime": crime,
                    "year": year,
                    "measurement_concept": spec["concept"],
                    "comparability_class": spec["classification"],
                    "reporting_ufs": len(reported),
                    "population_coverage_pct": 100.0 * raw_pop / brazil_pop,
                    "all_27_ufs_report": int(len(reported) == 27),
                    "raw_reported_total": int(round(raw_count)),
                    "balanced_sample_ufs": len(sample),
                    "balanced_sample_codes": " ".join(sample),
                    "balanced_sample_total": "" if sample_count is None else int(round(sample_count)),
                    "balanced_sample_population": "" if sample_pop is None else int(round(sample_pop)),
                    "balanced_sample_rate_per_100k": (
                        "" if sample_count is None or not sample_pop else 100000.0 * sample_count / sample_pop
                    ),
                }
            )
    partial_rows: list[dict[str, Any]] = []
    for crime in PARTIAL_COVERAGE_CRIMES:
        sample_ufs = balanced_ufs[crime]
        if not sample_ufs:
            raise ValueError(f"No time-balanced UF sample for partial indicator: {crime}")
        excluded_ufs = [uf for uf in UF_CODES if uf not in sample_ufs]
        for year in FIGURE_YEARS:
            count = sum(complete[(uf, year, crime)]["count"] for uf in sample_ufs)
            sample_pop = sum(population[(uf, year)] for uf in sample_ufs)
            partial_rows.append(
                {
                    "crime": crime,
                    "year": year,
                    "measurement_concept": CANDIDATES[crime]["concept"],
                    "comparability_class": CANDIDATES[crime]["classification"],
                    "sample_ufs": len(sample_ufs),
                    "sample_codes": " ".join(sample_ufs),
                    "excluded_uf_codes": " ".join(excluded_ufs),
                    "sample_population": int(round(sample_pop)),
                    "sample_population_share_brazil_pct": 100.0
                    * sample_pop
                    / sum(population[(uf, year)] for uf in UF_CODES),
                    "count": int(round(count)),
                    "rate_per_100k": 100000.0 * count / sample_pop,
                }
            )
    return coverage_rows, uf_rows, national_rows, partial_rows, balanced_ufs


def main() -> int:
    population = build_population()
    monthly, audit = scan_sinesp()
    coverage, uf_rows, national, partial, balanced_ufs = build_panels(monthly, population)
    _write_csv(
        COVERAGE_PATH,
        coverage,
        (
            "crime", "year", "uf", "reporting_status", "months_present", "months_numeric",
            "count_reported", "measurement_concept", "value_field", "raw_labels",
            "definition_version_flag", "comparability_class",
        ),
    )
    _write_csv(
        UF_PANEL_PATH,
        uf_rows,
        (
            "uf", "year", "crime", "count", "population", "rate_per_100k",
            "measurement_concept", "reporting_status", "comparability_class",
            "definition_version_flag",
        ),
    )
    _write_csv(
        NATIONAL_PANEL_PATH,
        national,
        (
            "crime", "year", "measurement_concept", "comparability_class", "reporting_ufs",
            "population_coverage_pct", "all_27_ufs_report", "raw_reported_total",
            "balanced_sample_ufs", "balanced_sample_codes", "balanced_sample_total",
            "balanced_sample_population", "balanced_sample_rate_per_100k",
        ),
    )
    _write_csv(
        PARTIAL_NATIONAL_PANEL_PATH,
        partial,
        (
            "crime", "year", "measurement_concept", "comparability_class", "sample_ufs",
            "sample_codes", "excluded_uf_codes", "sample_population",
            "sample_population_share_brazil_pct",
            "count", "rate_per_100k",
        ),
    )
    audit.update(
        {
            "source_years": list(SINESP_YEARS),
            "figure_years": list(FIGURE_YEARS),
            "candidate_crimes": list(CANDIDATES),
            "configured_selected_crimes": list(SELECTED_CRIMES),
            "balanced_ufs": balanced_ufs,
            "population_rows": len(population),
            "coverage_rows": len(coverage),
            "uf_panel_rows": len(uf_rows),
            "national_panel_rows": len(national),
            "partial_coverage_panel_rows": len(partial),
        }
    )
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp = AUDIT_PATH.with_suffix(".json.tmp")
    temp.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(AUDIT_PATH)
    print(
        f"SINESP BUILD coverage={len(coverage)} uf_panel={len(uf_rows)} "
        f"national={len(national)} years={ANO_INICIAL_SINESP}-{ANO_FINAL_SINESP}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
