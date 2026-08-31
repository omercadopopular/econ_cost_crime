"""Validate the retained Sinesp/IBGE/UNODC panels and Figures 1 and 2A–2D."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any
from zipfile import ZipFile, BadZipFile

from PIL import Image

from src.data.build_sinesp_panel import (
    ANO_FINAL_SINESP,
    ANO_INICIAL_SINESP,
    COVERAGE_PATH,
    FIGURE_YEARS,
    NATIONAL_PANEL_PATH,
    PARTIAL_COVERAGE_CRIMES,
    PARTIAL_NATIONAL_PANEL_PATH,
    SELECTED_CRIMES,
    UF_CODES,
    UF_PANEL_PATH,
)
from src.data.build_unodc_homicide_panel import (
    COMPARISON_YEARS,
    COUNTRY_COMPARISON_PATH,
    COUNTRY_YEAR_PATH,
)
from src.data.external_config import AUDIT_DIR, RAW_DIR, REPO_ROOT, SINESP_YEARS


FIGURES = {
    "fig_01_distribuicao_mundial_homicidios": "fig_01_distribuicao_mundial_homicidios.csv",
    "fig_02a_crimes_registrados": "fig_02a_crimes_registrados.csv",
    "fig_02b_taxas_criminalidade": "fig_02b_taxas_criminalidade.csv",
    "fig_02c_crimes_cobertura_parcial": "fig_02c_crimes_cobertura_parcial.csv",
    "fig_02d_taxas_cobertura_parcial": "fig_02d_taxas_cobertura_parcial.csv",
}
AUDIT_PATH = AUDIT_DIR / "external_validation.json"


class Validator:
    def __init__(self) -> None:
        self.checks: list[dict[str, Any]] = []

    def check(
        self, condition: bool, code: str, message: str, *, severity: str = "error", **details: Any
    ) -> None:
        self.checks.append(
            {"code": code, "severity": severity, "passed": bool(condition), "message": message,
             "details": details}
        )

    @property
    def errors(self) -> list[dict[str, Any]]:
        return [item for item in self.checks if item["severity"] == "error" and not item["passed"]]

    @property
    def warnings(self) -> list[dict[str, Any]]:
        return [item for item in self.checks if item["severity"] == "warning" and not item["passed"]]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_raw(validator: Validator) -> None:
    manifest_path = RAW_DIR / "source_manifest.json"
    validator.check(manifest_path.exists(), "raw_manifest", "Raw-source manifest exists.")
    if not manifest_path.exists():
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))["sources"]
    source_ids = [f"sinesp_vde_{year}" for year in SINESP_YEARS] + [
        "ibge_population_projection_2024_uf_age_sex",
        "unodc_intentional_homicide_2026_07",
        "unodc_intentional_homicide_metadata_2026_07",
    ]
    for source_id in source_ids:
        validator.check(source_id in manifest, "manifest_source", f"Manifest contains {source_id}.")
        if source_id not in manifest:
            continue
        path = REPO_ROOT / manifest[source_id]["local_path"]
        exists = path.exists() and path.stat().st_size > 0
        validator.check(exists, "raw_source", f"Retained raw source exists: {source_id}.")
        if exists:
            validator.check(
                sha256(path) == manifest[source_id]["sha256"], "raw_checksum",
                f"Checksum matches manifest: {source_id}.", source_id=source_id,
            )
            if path.suffix.lower() == ".xlsx":
                try:
                    with ZipFile(path) as archive:
                        valid_zip = archive.testzip() is None
                except BadZipFile:
                    valid_zip = False
                validator.check(valid_zip, "xlsx_integrity", f"XLSX is a valid ZIP: {source_id}.")


def validate_sinesp(validator: Validator) -> dict[str, Any]:
    paths = (COVERAGE_PATH, UF_PANEL_PATH, NATIONAL_PANEL_PATH, PARTIAL_NATIONAL_PANEL_PATH)
    for path in paths:
        validator.check(path.exists() and path.stat().st_size > 0, "sinesp_file", f"{path.name} exists.")
    if any(not path.exists() for path in paths):
        return {}
    coverage = read_csv(COVERAGE_PATH)
    uf_panel = read_csv(UF_PANEL_PATH)
    national = read_csv(NATIONAL_PANEL_PATH)
    partial = read_csv(PARTIAL_NATIONAL_PANEL_PATH)
    coverage_keys = [(row["crime"], row["year"], row["uf"]) for row in coverage]
    uf_keys = [(row["uf"], row["year"], row["crime"]) for row in uf_panel]
    national_keys = [(row["crime"], row["year"]) for row in national]
    validator.check(len(coverage_keys) == len(set(coverage_keys)), "sinesp_coverage_keys", "Coverage keys are unique.")
    validator.check(len(uf_keys) == len(set(uf_keys)), "sinesp_uf_keys", "UF-year-crime keys are unique.")
    validator.check(len(national_keys) == len(set(national_keys)), "sinesp_national_keys", "National year-crime keys are unique.")
    validator.check(
        all(row["count_reported"] == "" for row in coverage if row["reporting_status"] == "NOT_REPORTED"),
        "missing_not_zero", "Non-reporting remains missing rather than zero.",
    )
    for crime in SELECTED_CRIMES:
        rows = [
            row for row in national
            if row["crime"] == crime and int(row["year"]) in FIGURE_YEARS
        ]
        validator.check(
            len(rows) == len(FIGURE_YEARS) and all(row["reporting_ufs"] == "27" for row in rows),
            "selected_full_coverage", f"{crime} has 27-UF coverage in every Figure 2 year.", crime=crime,
        )
        validator.check(
            all(row["raw_reported_total"] == row["balanced_sample_total"] for row in rows),
            "full_sample_reconciliation", f"{crime} raw and balanced totals agree.", crime=crime,
        )
        validator.check(
            all(row["measurement_concept"] == "vítimas" for row in rows),
            "selected_measurement_concept", f"{crime} is explicitly classified as a victim count.",
            crime=crime,
        )
    partial_keys = [(row["crime"], row["year"]) for row in partial]
    validator.check(
        len(partial_keys) == len(set(partial_keys)) == len(PARTIAL_COVERAGE_CRIMES) * len(FIGURE_YEARS),
        "partial_panel_keys", "Partial-coverage balanced-panel keys are complete and unique.",
    )
    national_lookup = {
        (row["crime"], row["year"]): row for row in national
        if row["crime"] in PARTIAL_COVERAGE_CRIMES and int(row["year"]) in FIGURE_YEARS
    }
    for crime in PARTIAL_COVERAGE_CRIMES:
        rows = [row for row in partial if row["crime"] == crime]
        sample_codes = {row["sample_codes"] for row in rows}
        sample_sizes = {row["sample_ufs"] for row in rows}
        excluded_codes = {row["excluded_uf_codes"] for row in rows}
        sample = next(iter(sample_codes)).split() if len(sample_codes) == 1 else []
        excluded = next(iter(excluded_codes)).split() if len(excluded_codes) == 1 else []
        metadata_valid = (
            len(rows) == len(FIGURE_YEARS)
            and len(sample_codes) == len(sample_sizes) == len(excluded_codes) == 1
            and len(sample) == int(next(iter(sample_sizes)))
            and not set(sample) & set(excluded)
            and set(sample) | set(excluded) == set(UF_CODES)
        )
        validator.check(
            metadata_valid,
            "partial_indicator_sample",
            f"{crime} uses one documented indicator-specific balanced UF sample.",
            crime=crime,
        )
        validator.check(
            metadata_valid and all(
                row["sample_codes"]
                == national_lookup[(crime, row["year"])]["balanced_sample_codes"]
                for row in rows
            ),
            "partial_sample_reconciliation",
            f"{crime} sample agrees with its full-period balanced sample.",
            crime=crime,
        )
    validator.check(
        all(int(row["count"]) >= 0 and float(row["sample_population"]) > 0 for row in partial),
        "partial_values", "Partial-panel counts are nonnegative and denominators positive.",
    )
    validator.check(
        all(row["measurement_concept"] == "ocorrências" for row in partial),
        "partial_measurement_concept", "All four partial-coverage indicators count occurrences.",
    )
    selected_national = [
        row for row in national
        if row["crime"] in SELECTED_CRIMES and int(row["year"]) in FIGURE_YEARS
    ]
    jumps: list[dict[str, Any]] = []
    for crime in SELECTED_CRIMES:
        series = sorted(
            (row for row in selected_national if row["crime"] == crime), key=lambda row: int(row["year"])
        )
        for previous, current in zip(series, series[1:]):
            old, new = float(previous["raw_reported_total"]), float(current["raw_reported_total"])
            if old > 0 and abs(new / old - 1) > 0.40:
                jumps.append({"crime": crime, "from": previous["year"], "to": current["year"], "change": new / old - 1})
    validator.check(
        not jumps, "large_yoy_changes", "Annual changes above 40% require interpretation, not mechanical correction.",
        severity="warning", jumps=jumps,
    )
    return {"coverage_rows": len(coverage), "uf_rows": len(uf_panel), "large_jumps": jumps}


def validate_figure2(validator: Validator) -> None:
    data_dir = REPO_ROOT / "data" / "figure_data"
    pairs = (
        ("fig_02a_crimes_registrados.csv", "fig_02b_taxas_criminalidade.csv", 27, 60),
        ("fig_02c_crimes_cobertura_parcial.csv", "fig_02d_taxas_cobertura_parcial.csv", None, 40),
    )
    for count_name, rate_name, sample_size, expected_rows in pairs:
        count_rows, rate_rows = read_csv(data_dir / count_name), read_csv(data_dir / rate_name)
        keys_count = {(row["crime"], row["year"], row["geographic_sample"]) for row in count_rows}
        keys_rate = {(row["crime"], row["year"], row["geographic_sample"]) for row in rate_rows}
        validator.check(
            len(count_rows) == len(rate_rows) == expected_rows and keys_count == keys_rate,
            "figure2_same_sample", f"{count_name} and {rate_name} use identical samples.",
        )
        samples_by_crime: dict[str, set[tuple[str, str, str]]] = {}
        for row in count_rows:
            samples_by_crime.setdefault(row["crime"], set()).add(
                (row["geographic_sample"], row["reporting_ufs"], row.get("excluded_uf_codes", ""))
            )
            size_valid = (
                int(row["reporting_ufs"]) == sample_size
                if sample_size is not None
                else 0 < int(row["reporting_ufs"]) <= 27
            )
            validator.check(
                size_valid,
                "figure2_sample_size", f"{count_name} uses the documented UF sample.",
            )
            count, population, rate = int(row["count"]), int(row["population"]), float(row["rate_per_100k"])
            validator.check(
                count >= 0 and population > 0 and math.isclose(rate, 100000 * count / population, rel_tol=0, abs_tol=1e-10),
                "figure2_rate_identity", f"Count/population/rate identity passes for {row['crime']} {row['year']}.",
            )
        validator.check(
            all(len(samples) == 1 for samples in samples_by_crime.values()),
            "figure2_balanced_within_indicator",
            f"Every series in {count_name} keeps a fixed UF sample across years.",
        )


def validate_unodc(validator: Validator) -> dict[str, Any]:
    country_year, comparison = read_csv(COUNTRY_YEAR_PATH), read_csv(COUNTRY_COMPARISON_PATH)
    keys = [(row["iso3"], row["year"]) for row in country_year]
    validator.check(len(keys) == len(set(keys)), "unodc_keys", "UNODC country-year keys are unique.")
    validator.check(
        all(0 <= float(row["homicide_rate_per_100k"]) <= 250 for row in country_year),
        "unodc_rates", "UNODC values are plausible rates, not counts.",
    )
    included = [row for row in comparison if row["included_common_sample"] == "1"]
    isos_by_year = {
        year: {row["iso3"] for row in included if int(row["year"]) == year}
        for year in COMPARISON_YEARS
    }
    common_size = len(isos_by_year[COMPARISON_YEARS[0]])
    validator.check(
        common_size >= 80
        and isos_by_year[COMPARISON_YEARS[0]] == isos_by_year[COMPARISON_YEARS[1]],
        "unodc_common_sample",
        "Both comparison years use the same official country/territory reporting units.",
        common_sample=common_size,
    )
    validator.check(
        COMPARISON_YEARS == (2016, 2024), "unodc_comparison_years",
        "Figure 1 compares the requested 2016 and 2024 cross-sections."
    )
    year_index = {
        (row["iso3"], int(row["year"])): float(row["homicide_rate_per_100k"])
        for row in country_year
    }
    percentile_checks: list[bool] = []
    rate_checks: list[bool] = []
    for year in COMPARISON_YEARS:
        year_rows = [row for row in included if int(row["year"]) == year]
        rates: dict[str, float] = {}
        for row in year_rows:
            calculated = year_index[(row["iso3"], year)]
            rates[row["iso3"]] = calculated
            rate_checks.append(
                math.isclose(
                    calculated, float(row["homicide_rate_per_100k"]),
                    rel_tol=0, abs_tol=1e-12,
                )
            )
        ordered = sorted(rates.items(), key=lambda item: (item[1], item[0]))
        stored_percentiles = {
            row["iso3"]: float(row["percentile_unweighted"]) for row in year_rows
        }
        position = 0
        while position < len(ordered):
            end = position + 1
            while end < len(ordered) and abs(ordered[end][1] - ordered[position][1]) <= 1e-12:
                end += 1
            expected_percentile = 100.0 * ((position + end - 1) / 2.0) / (len(ordered) - 1)
            for tied_position in range(position, end):
                iso3 = ordered[tied_position][0]
                percentile_checks.append(
                    math.isclose(
                        stored_percentiles[iso3], expected_percentile, rel_tol=0, abs_tol=1e-12
                    )
                )
            position = end
    validator.check(
        all(rate_checks), "unodc_comparison_rates",
        "Figure 1 rates reproduce the retained UNODC country-year panel.",
    )
    validator.check(
        all(percentile_checks), "unodc_percentiles",
        "Unweighted country percentiles reproduce the documented rank convention.",
    )
    validator.check(
        all("BRA" in isos for isos in isos_by_year.values()),
        "unodc_brazil", "Brazil is included in both comparison years.",
    )
    spot_values = {
        ("BRA", 2010): 26.9945684769237,
        ("BRA", 2024): 18.6911635044563,
        ("USA", 2010): 4.73280651793807,
        ("USA", 2023): 5.76340794073065,
        ("MEX", 2024): 25.6378892147758,
        ("ZAF", 2023): 43.3759945153785,
    }
    indexed = year_index
    validator.check(
        all(key in indexed and math.isclose(indexed[key], value, rel_tol=0, abs_tol=1e-12) for key, value in spot_values.items()),
        "unodc_raw_spotchecks", "Six country-year rates reproduce the retained raw workbook.",
    )
    return {"country_year_rows": len(country_year), "common_sample": common_size}


def validate_outputs(validator: Validator) -> None:
    for stem, csv_name in FIGURES.items():
        csv_path = REPO_ROOT / "data" / "figure_data" / csv_name
        validator.check(csv_path.exists() and csv_path.stat().st_size > 0, "figure_csv", f"{csv_name} exists.")
        for suffix in ("pdf", "png"):
            path = REPO_ROOT / "figs" / f"{stem}.{suffix}"
            validator.check(path.exists() and path.stat().st_size > 0, "figure_output", f"{path.name} exists.")
            if suffix == "png" and path.exists():
                try:
                    with Image.open(path) as image:
                        image.verify()
                    valid = True
                except Exception:
                    valid = False
                validator.check(valid, "png_integrity", f"{path.name} is a valid PNG.")


def main() -> int:
    validator = Validator()
    validate_raw(validator)
    sinesp = validate_sinesp(validator)
    validate_figure2(validator)
    unodc = validate_unodc(validator)
    validate_outputs(validator)
    result = {
        "checks": validator.checks,
        "summary": {
            "checks": len(validator.checks),
            "passed": sum(item["passed"] for item in validator.checks),
            "errors": len(validator.errors),
            "warnings": len(validator.warnings),
            "sinesp": sinesp,
            "unodc": unodc,
        },
    }
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp = AUDIT_PATH.with_suffix(".json.tmp")
    temp.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(AUDIT_PATH)
    print(
        f"EXTERNAL VALIDATION checks={len(validator.checks)} errors={len(validator.errors)} "
        f"warnings={len(validator.warnings)}"
    )
    for warning in validator.warnings:
        print(f"WARNING {warning['code']}: {warning['message']} {warning['details']}")
    for error in validator.errors:
        print(f"ERROR {error['code']}: {error['message']} {error['details']}")
    return 1 if validator.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
