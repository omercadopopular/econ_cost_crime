"""Validate the retained SIM/IBGE homicide pipeline and Figures 3–5."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from statistics import correlation, median
from typing import Any

from PIL import Image

from src.data.homicide_config import (
    ANO_FINAL_SIM,
    ANO_INICIAL,
    ANOS_SIM,
    BUILD_AUDIT_PATH,
    CROSSWALK_PATH,
    MUNICIPAL_PANEL_PATH,
    PANEL_PATH,
    RAW_MANIFEST,
    REPO_ROOT,
    VALIDATION_AUDIT_PATH,
)


FIGURE_SPECS = {
    3: {
        "csv": REPO_ROOT / "data" / "figure_data" / "fig_03_microrregion_homicides.csv",
        "stem": "fig_03_homicidios_microrregioes",
    },
    4: {
        "csv": REPO_ROOT / "data" / "figure_data" / "fig_04_microrregion_homicide_change.csv",
        "stem": "fig_04_variacao_homicidios_microrregioes",
    },
    5: {
        "csv": REPO_ROOT / "data" / "figure_data" / "fig_05_microrregion_homicide_convergence.csv",
        "stem": "fig_05_convergencia_homicidios_microrregioes",
    },
}

# Independent, published national checks for pinned years. The 2016 value appears in the
# original report; 2023 and 2024 are the final SIM totals reported with Atlas da Violência 2026.
OFFICIAL_HOMICIDE_TOTALS = {2016: 62517, 2023: 45747, 2024: 42590}
OFFICIAL_POPULATION_TOTALS = {2016: 206081432, 2022: 203080756, 2024: 212583750}


class Validator:
    def __init__(self) -> None:
        self.checks: list[dict[str, Any]] = []

    def check(self, condition: bool, code: str, message: str, *, severity: str = "error", **details: Any) -> None:
        self.checks.append(
            {
                "code": code,
                "severity": severity,
                "passed": bool(condition),
                "message": message,
                "details": details,
            }
        )

    @property
    def errors(self) -> list[dict[str, Any]]:
        return [check for check in self.checks if check["severity"] == "error" and not check["passed"]]

    @property
    def warnings(self) -> list[dict[str, Any]]:
        return [check for check in self.checks if check["severity"] == "warning" and not check["passed"]]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_raw_sources(validator: Validator) -> None:
    validator.check(RAW_MANIFEST.exists(), "raw_manifest_exists", "Raw source manifest exists.")
    if not RAW_MANIFEST.exists():
        return
    manifest = json.loads(RAW_MANIFEST.read_text(encoding="utf-8"))
    active = 0
    for source_id, source in manifest.get("sources", {}).items():
        path = REPO_ROOT / source["local_path"]
        exists = path.exists() and path.stat().st_size > 0
        validator.check(exists, "raw_file_exists", f"Retained raw source exists: {source_id}.", source_id=source_id)
        if not exists:
            continue
        digest = sha256(path)
        validator.check(
            digest == source["sha256"],
            "raw_checksum",
            f"Retained raw checksum matches manifest: {source_id}.",
            source_id=source_id,
            expected=source["sha256"],
            actual=digest,
        )
        if source.get("status") != "retained_diagnostic_not_used":
            active += 1
    validator.check(active >= 13, "active_sources", "All active SIM and IBGE inputs are retained.", active_sources=active)


def validate_panels(validator: Validator) -> dict[str, Any]:
    required = (CROSSWALK_PATH, MUNICIPAL_PANEL_PATH, PANEL_PATH, BUILD_AUDIT_PATH)
    for path in required:
        validator.check(path.exists() and path.stat().st_size > 0, "derived_file_exists", f"Derived file exists: {path.name}.")
    if any(not path.exists() for path in required):
        return {}
    crosswalk = read_csv(CROSSWALK_PATH)
    municipal = read_csv(MUNICIPAL_PANEL_PATH)
    panel = read_csv(PANEL_PATH)
    audit = json.loads(BUILD_AUDIT_PATH.read_text(encoding="utf-8"))
    validator.check(len(crosswalk) == 5570, "crosswalk_municipalities", "Crosswalk has 5,570 period municipalities.", rows=len(crosswalk))
    validator.check(
        len({row["municipality_code_7"] for row in crosswalk}) == 5570,
        "crosswalk_key_7",
        "Seven-digit municipality keys are unique.",
    )
    validator.check(
        len({row["municipality_code_6"] for row in crosswalk}) == 5570,
        "crosswalk_key_6",
        "Six-digit SIM municipality keys are unique.",
    )
    validator.check(
        len({row["microrregion_code"] for row in crosswalk}) == 558,
        "crosswalk_microrregions",
        "Crosswalk covers 558 old IBGE microrregions.",
    )
    validator.check(len({row["uf"] for row in crosswalk}) == 27, "crosswalk_ufs", "Crosswalk covers all 27 UFs.")
    municipal_keys = [(row["municipality_code_7"], int(row["year"])) for row in municipal]
    validator.check(
        len(municipal_keys) == len(set(municipal_keys)) == 5570 * len(ANOS_SIM),
        "municipality_year_keys",
        "Municipality-year consolidation has one row per key.",
        rows=len(municipal_keys),
    )
    panel_keys = [(row["microrregion_code"], int(row["year"])) for row in panel]
    validator.check(
        len(panel_keys) == len(set(panel_keys)) == 558 * len(ANOS_SIM),
        "microrregion_year_keys",
        "Microrregion-year panel has one row per key.",
        rows=len(panel_keys),
    )
    validator.check(
        {int(row["year"]) for row in panel} == set(ANOS_SIM),
        "panel_years",
        "Panel contains the six requested endpoint/diagnostic years.",
    )
    validator.check(
        all(int(row["homicide_count"]) >= 0 for row in panel),
        "nonnegative_homicides",
        "Homicide counts are nonnegative.",
    )
    validator.check(
        all(float(row["population"]) > 0 for row in panel),
        "positive_population",
        "Microrregion populations are positive.",
    )
    validator.check(
        all(math.isfinite(float(row["homicide_rate_per_100k"])) for row in panel),
        "finite_rates",
        "Homicide rates are finite.",
    )
    for year in ANOS_SIM:
        year_rows = [row for row in panel if int(row["year"]) == year]
        validator.check(
            len(year_rows) == 558 and len({row["uf"] for row in year_rows}) == 27,
            "annual_geographic_coverage",
            f"{year} covers 558 microrregions and 27 UFs.",
            year=year,
            rows=len(year_rows),
            ufs=len({row["uf"] for row in year_rows}),
        )
        mapped = sum(int(row["homicide_count"]) for row in year_rows)
        sim = audit["sim"][str(year)]
        validator.check(
            mapped == sim["mapped_homicides"],
            "mapped_homicide_reconciliation",
            f"{year} panel reconciles to all SIM homicides with identifiable municipality.",
            year=year,
            panel=mapped,
            audit=sim["mapped_homicides"],
        )
        validator.check(
            sim["match_rate_pct"] >= 95.0,
            "municipality_match_minimum",
            f"{year} municipality match rate exceeds the documented 95% sufficiency floor.",
            year=year,
            match_rate_pct=sim["match_rate_pct"],
        )
        validator.check(
            sim["match_rate_pct"] >= 99.0,
            "municipality_match_below_99",
            f"{year} municipality match is below the 99% review threshold.",
            severity="warning",
            year=year,
            match_rate_pct=sim["match_rate_pct"],
            excluded_homicides=sim["excluded_homicides"],
        )
    for year, expected in OFFICIAL_HOMICIDE_TOTALS.items():
        actual = audit["sim"][str(year)]["official_sim_homicide_records"]
        validator.check(
            actual == expected,
            "official_homicide_total",
            f"{year} raw SIM definition matches the published national total.",
            year=year,
            expected=expected,
            actual=actual,
        )
    for year, expected in OFFICIAL_POPULATION_TOTALS.items():
        actual = audit["population"][str(year)]["municipal_population_total"]
        validator.check(
            math.isclose(actual, expected, rel_tol=0.0, abs_tol=0.5),
            "official_population_total",
            f"{year} municipal populations aggregate to the official national total.",
            year=year,
            expected=expected,
            actual=actual,
        )
    start_codes = {row["microrregion_code"] for row in panel if int(row["year"]) == ANO_INICIAL}
    end_codes = {row["microrregion_code"] for row in panel if int(row["year"]) == ANO_FINAL_SIM}
    validator.check(
        start_codes == end_codes and len(start_codes) == 558,
        "fixed_geography_endpoints",
        "The same 558 fixed microrregions are used in 2016 and the terminal year.",
    )
    return {"audit": audit, "panel": panel}


def validate_figures(validator: Validator) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for number, spec in FIGURE_SPECS.items():
        data_path = spec["csv"]
        validator.check(data_path.exists() and data_path.stat().st_size > 0, "figure_csv_exists", f"Figure {number} CSV exists.")
        for extension in ("pdf", "png"):
            path = REPO_ROOT / "figs" / f"{spec['stem']}.{extension}"
            validator.check(
                path.exists() and path.stat().st_size > 0,
                "figure_output_exists",
                f"Figure {number} {extension.upper()} exists and is nonempty.",
            )
            if extension == "png" and path.exists():
                try:
                    with Image.open(path) as image:
                        image.verify()
                    valid = True
                except Exception:
                    valid = False
                validator.check(valid, "png_integrity", f"Figure {number} PNG passes image verification.")
    if any(not spec["csv"].exists() for spec in FIGURE_SPECS.values()):
        return summary
    fig3 = read_csv(FIGURE_SPECS[3]["csv"])
    validator.check(len(fig3) == 558, "fig3_rows", "Figure 3 contains all 558 microrregions.", rows=len(fig3))
    validator.check(
        {int(row["year"]) for row in fig3} == {ANO_FINAL_SIM},
        "fig3_terminal_year",
        "Figure 3 uses only ANO_FINAL_SIM.",
    )
    ratios = [float(row["bubble_area_points2"]) / float(row["population"]) for row in fig3]
    validator.check(
        max(ratios) - min(ratios) < 1e-15,
        "fig3_bubble_area",
        "Figure 3 bubble area is exactly proportional to population.",
    )
    percentiles = [float(row["percentile_unweighted"]) for row in fig3]
    validator.check(
        all(0 < value <= 100 for value in percentiles) and max(percentiles) == 100.0,
        "fig3_percentiles",
        "Figure 3 uses valid unweighted cross-sectional percentiles.",
    )
    fig4 = read_csv(FIGURE_SPECS[4]["csv"])
    validator.check(len(fig4) == 558, "fig4_rows", "Figure 4 contains each microrregion once.", rows=len(fig4))
    validator.check(
        len({row["microrregion_code"] for row in fig4}) == 558,
        "fig4_keys",
        "Figure 4 microrregion keys are unique.",
    )
    delta_ok = all(
        math.isclose(
            float(row["delta_rate_per_100k"]),
            float(row["rate_end_per_100k"]) - float(row["rate_start_per_100k"]),
            rel_tol=0.0,
            abs_tol=1e-10,
        )
        for row in fig4
    )
    validator.check(delta_ok, "fig4_absolute_change", "Figure 4 uses end-rate minus 2016-rate in levels.")
    endpoint = [float(row["delta_rate_per_100k"]) for row in fig4]
    smoothed = [float(row["delta_average_rate_per_100k"]) for row in fig4]
    smoothing = {
        "pearson_correlation": correlation(endpoint, smoothed),
        "same_direction_share": sum((a >= 0) == (b >= 0) for a, b in zip(endpoint, smoothed)) / len(fig4),
        "median_absolute_difference": median(abs(a - b) for a, b in zip(endpoint, smoothed)),
    }
    validator.check(
        smoothing["pearson_correlation"] >= 0.8 and smoothing["same_direction_share"] >= 0.75,
        "smoothing_material_change",
        "Endpoint smoothing preserves the broad geographic pattern under documented diagnostics.",
        severity="warning",
        **smoothing,
    )
    summary["smoothing"] = smoothing
    summary["visual_scale_limit"] = float(fig4[0]["visual_scale_limit"])
    summary["visually_clipped_microrregions"] = sum(int(row["visually_clipped"]) for row in fig4)
    fig5 = read_csv(FIGURE_SPECS[5]["csv"])
    validator.check(len(fig5) == 558, "fig5_rows", "Figure 5 contains each microrregion once.", rows=len(fig5))
    validator.check(
        len({row["microrregion_code"] for row in fig5}) == 558,
        "fig5_keys",
        "Figure 5 microrregion keys are unique.",
    )
    fig5_identity = all(
        math.isclose(
            float(row["delta_rate_2016_2024_per_100k"]),
            float(row["rate_2024_per_100k"]) - float(row["rate_2016_per_100k"]),
            rel_tol=0.0,
            abs_tol=1e-10,
        )
        for row in fig5
    )
    validator.check(fig5_identity, "fig5_absolute_change", "Figure 5 uses 2024-rate minus 2016-rate in levels.")
    fig5_ratios = [float(row["bubble_area_points2"]) / float(row["population_2016"]) for row in fig5]
    validator.check(
        max(fig5_ratios) - min(fig5_ratios) < 1e-15,
        "fig5_bubble_area",
        "Figure 5 bubble area is exactly proportional to 2016 population.",
    )
    convergence_audit = REPO_ROOT / "data" / "audit" / "microrregion_homicide_convergence.json"
    validator.check(
        convergence_audit.exists() and convergence_audit.stat().st_size > 0,
        "fig5_audit_exists",
        "Figure 5 convergence diagnostics are retained.",
    )
    if convergence_audit.exists():
        convergence = json.loads(convergence_audit.read_text(encoding="utf-8"))
        validator.check(
            convergence.get("n") == 558
            and convergence.get("start_year") == 2016
            and convergence.get("end_year") == ANO_FINAL_SIM,
            "fig5_audit_endpoints",
            "Figure 5 diagnostics use all 558 microrregions and the intended endpoints.",
        )
        summary["convergence"] = convergence
    return summary


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-only", action="store_true", help="Skip Figure 3–5 output checks.")
    parser.add_argument("--json-out", type=Path, default=VALIDATION_AUDIT_PATH)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    validator = Validator()
    validate_raw_sources(validator)
    panel_summary = validate_panels(validator)
    figure_summary = {} if args.data_only else validate_figures(validator)
    passed = sum(1 for check in validator.checks if check["passed"])
    output = {
        "schema_version": 1,
        "checks": validator.checks,
        "summary": {
            "checks": len(validator.checks),
            "passed": passed,
            "errors": len(validator.errors),
            "warnings": len(validator.warnings),
            "ano_final_sim": ANO_FINAL_SIM,
            "figure_diagnostics": figure_summary,
            "matched_homicides": {
                year: panel_summary.get("audit", {}).get("sim", {}).get(str(year), {})
                for year in ANOS_SIM
            },
        },
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    temp = args.json_out.with_suffix(args.json_out.suffix + ".tmp")
    temp.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(args.json_out)
    print(
        f"HOMICIDE VALIDATION checks={len(validator.checks)} passed={passed} "
        f"errors={len(validator.errors)} warnings={len(validator.warnings)}"
    )
    for check in validator.errors + validator.warnings:
        print(f"{check['severity'].upper()} {check['code']}: {check['message']} {check['details']}")
    return 1 if validator.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
