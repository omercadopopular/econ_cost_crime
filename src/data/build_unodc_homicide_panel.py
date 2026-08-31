"""Build the audited UNODC country-year and 2016/2024 comparison panels for Figure 1."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
import json
from pathlib import Path
from statistics import median
from typing import Any, Iterable, Mapping, Sequence

from .external_config import AUDIT_DIR, INTERIM_DIR, UNODC_PATH
from .xlsx_stream import iter_rows


COMPARISON_YEARS = (2016, 2024)
ANO_FINAL_UNODC = 2024

COUNTRY_YEAR_PATH = INTERIM_DIR / "unodc_homicide_country_year.csv"
COUNTRY_COMPARISON_PATH = INTERIM_DIR / "unodc_homicide_country_comparison.csv"
AUDIT_PATH = AUDIT_DIR / "unodc_build_audit.json"


def _text(value: object | None) -> str:
    return "" if value is None else str(value).strip()


def _number(value: object | None) -> float | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return float(str(value).strip().replace(",", "."))


def _write_csv(path: Path, rows: Iterable[Mapping[str, Any]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)
    temp.replace(path)


def _percentiles(values: dict[str, float]) -> dict[str, float]:
    """Return average-rank percentiles scaled so the sample endpoints are 0 and 100."""

    ordered = sorted(values.items(), key=lambda item: (item[1], item[0]))
    n = len(ordered)
    if n < 2:
        raise ValueError("At least two countries are required to calculate percentiles.")
    result: dict[str, float] = {}
    start = 0
    while start < n:
        end = start + 1
        while end < n and abs(ordered[end][1] - ordered[start][1]) <= 1e-12:
            end += 1
        average_zero_based_rank = (start + end - 1) / 2.0
        percentile = 100.0 * average_zero_based_rank / (n - 1)
        for position in range(start, end):
            result[ordered[position][0]] = percentile
        start = end
    return result


def read_country_year() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = iter_rows(UNODC_PATH, sheet_name="data_cts_intentional_homicide")
    header: list[object | None] | None = None
    for row in rows:
        if row and _text(row[0]) == "Iso3_code":
            header = row
            break
    if header is None:
        raise ValueError("UNODC country-data header was not found.")
    index = {_text(value): position for position, value in enumerate(header)}
    required = {
        "Iso3_code", "Country", "Region", "Subregion", "Indicator", "Dimension",
        "Category", "Sex", "Age", "Year", "Unit of measurement", "VALUE", "Source",
    }
    if not required.issubset(index):
        raise ValueError(f"Unexpected UNODC schema; missing {sorted(required - set(index))}")

    candidates: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    names: dict[str, Counter[str]] = defaultdict(Counter)
    excluded_nonstandard_ids: Counter[str] = Counter()
    for row in rows:
        def cell(name: str) -> object | None:
            position = index[name]
            return row[position] if len(row) > position else None

        if not (
            _text(cell("Indicator")) == "Victims of intentional homicide"
            and _text(cell("Dimension")) == "Total"
            and _text(cell("Category")) == "Total"
            and _text(cell("Sex")) == "Total"
            and _text(cell("Age")) == "Total"
            and _text(cell("Unit of measurement")) == "Rate per 100,000 population"
        ):
            continue
        iso3 = _text(cell("Iso3_code")).upper()
        if len(iso3) != 3:
            # The workbook also contains a small number of subnational reporting
            # units (for example, England and Wales). Figure 1 is country-level.
            excluded_nonstandard_ids[iso3] += 1
            continue
        year_value = _number(cell("Year"))
        value = _number(cell("VALUE"))
        if year_value is None or value is None:
            continue
        year = int(year_value)
        if year != year_value:
            raise ValueError(f"Non-integer UNODC year: {year_value}")
        if value < 0 or value > 250:
            raise ValueError(f"Implausible UNODC homicide rate: {iso3}, {year}, {value}")
        name = _text(cell("Country"))
        names[iso3][name] += 1
        candidates[(iso3, year)].append(
            {
                "iso3": iso3,
                "country": name,
                "region": _text(cell("Region")),
                "subregion": _text(cell("Subregion")),
                "year": year,
                "homicide_rate_per_100k": value,
                "source": _text(cell("Source")),
            }
        )

    output: list[dict[str, Any]] = []
    duplicate_identical = 0
    conflicts: list[dict[str, Any]] = []
    for key, observations in sorted(candidates.items()):
        distinct_values = {round(float(obs["homicide_rate_per_100k"]), 12) for obs in observations}
        if len(distinct_values) > 1:
            conflicts.append({"iso3": key[0], "year": key[1], "values": sorted(distinct_values)})
            continue
        if len(observations) > 1:
            duplicate_identical += len(observations) - 1
        base = observations[0]
        canonical_name = names[key[0]].most_common(1)[0][0]
        output.append(
            {
                "iso3": key[0],
                "country": canonical_name,
                "region": base["region"],
                "subregion": base["subregion"],
                "year": key[1],
                "homicide_rate_per_100k": base["homicide_rate_per_100k"],
                "source": " | ".join(sorted({obs["source"] for obs in observations if obs["source"]})),
                "status": "observed_official_unodc",
            }
        )
    if conflicts:
        raise ValueError(f"Conflicting UNODC country-year rates: {conflicts[:10]}")
    if not output:
        raise ValueError("UNODC selector returned no observations.")
    audit = {
        "indicator": "Victims of intentional homicide",
        "selector": {
            "dimension": "Total", "category": "Total", "sex": "Total", "age": "Total",
            "unit": "Rate per 100,000 population",
        },
        "duplicate_identical_rows_collapsed": duplicate_identical,
        "country_name_variants": {
            iso: sorted(counter) for iso, counter in names.items() if len(counter) > 1
        },
        "excluded_nonstandard_country_identifiers": dict(sorted(excluded_nonstandard_ids.items())),
    }
    return output, audit


def build_comparison(country_year: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    values = {
        (str(row["iso3"]), int(row["year"])): float(row["homicide_rate_per_100k"])
        for row in country_year
    }
    if len(values) != len(country_year):
        raise ValueError("UNODC country-year key is not unique after processing.")
    metadata: dict[str, dict[str, str]] = {}
    for row in country_year:
        metadata[str(row["iso3"])] = {
            "country": str(row["country"]),
            "region": str(row["region"]),
            "subregion": str(row["subregion"]),
        }
    counts_by_year = Counter(int(row["year"]) for row in country_year)
    recent_reference = [counts_by_year[year] for year in range(2015, ANO_FINAL_UNODC) if counts_by_year[year]]
    terminal_threshold = 0.70 * median(recent_reference)
    if counts_by_year[ANO_FINAL_UNODC] < max(90, terminal_threshold):
        raise ValueError(
            f"UNODC {ANO_FINAL_UNODC} coverage is not broad enough: "
            f"{counts_by_year[ANO_FINAL_UNODC]} countries, threshold={max(90, terminal_threshold):.1f}."
        )

    all_isos = sorted(metadata)
    common_sample = {
        iso3
        for iso3 in all_isos
        if all((iso3, year) in values for year in COMPARISON_YEARS)
    }
    if "BRA" not in common_sample:
        raise ValueError("Brazil is not observed in both configured UNODC comparison years.")
    if len(common_sample) < 80:
        raise ValueError(f"UNODC 2016/2024 common sample is unexpectedly small: {len(common_sample)} units")

    percentiles = {
        year: _percentiles({iso3: values[(iso3, year)] for iso3 in common_sample})
        for year in COMPARISON_YEARS
    }

    output: list[dict[str, Any]] = []
    for year in COMPARISON_YEARS:
        for iso3 in all_isos:
            included = iso3 in common_sample
            rate = values.get((iso3, year))
            missing_years = [candidate for candidate in COMPARISON_YEARS if (iso3, candidate) not in values]
            output.append(
                {
                    "iso3": iso3,
                    "country": metadata[iso3]["country"],
                    "region": metadata[iso3]["region"],
                    "subregion": metadata[iso3]["subregion"],
                    "year": year,
                    "homicide_rate_per_100k": "" if rate is None else rate,
                    "percentile_unweighted": "" if not included else percentiles[year][iso3],
                    "included_common_sample": int(included),
                    "inclusion_reason": (
                        "INCLUDED_OBSERVED_BOTH_YEARS"
                        if included
                        else "MISSING_" + "_AND_".join(str(candidate) for candidate in missing_years)
                    ),
                }
            )
    audit = {
        "comparison_years": list(COMPARISON_YEARS),
        "common_sample_reporting_units": len(common_sample),
        "countries_by_year": dict(sorted(counts_by_year.items())),
        "terminal_year": ANO_FINAL_UNODC,
        "terminal_year_countries": counts_by_year[ANO_FINAL_UNODC],
        "terminal_completeness_rule": (
            "At least 90 reporting units and at least 70% of the median annual coverage in "
            "2015–2023; Figure 1 retains only units observed in both 2016 and 2024."
        ),
        "percentile_convention": (
            "Unweighted average rank, scaled as 100*(rank-1)/(N-1); tied values receive average ranks."
        ),
        "brazil": {
            str(year): {
                "rate": values[("BRA", year)],
                "percentile": percentiles[year]["BRA"],
            }
            for year in COMPARISON_YEARS
        },
    }
    return output, audit


def main() -> int:
    country_year, source_audit = read_country_year()
    comparison, comparison_audit = build_comparison(country_year)
    _write_csv(
        COUNTRY_YEAR_PATH,
        country_year,
        (
            "iso3", "country", "region", "subregion", "year",
            "homicide_rate_per_100k", "source", "status",
        ),
    )
    _write_csv(
        COUNTRY_COMPARISON_PATH,
        comparison,
        (
            "iso3", "country", "region", "subregion", "year", "homicide_rate_per_100k",
            "percentile_unweighted", "included_common_sample", "inclusion_reason",
        ),
    )
    audit = {**source_audit, **comparison_audit, "country_year_rows": len(country_year)}
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp = AUDIT_PATH.with_suffix(".json.tmp")
    temp.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(AUDIT_PATH)
    print(
        f"UNODC BUILD country_year={len(country_year)} common_sample="
        f"{comparison_audit['common_sample_reporting_units']} terminal={ANO_FINAL_UNODC}"
    )
    for year, stats in comparison_audit["brazil"].items():
        print(
            f"BRAZIL {year}: rate={stats['rate']:.3f}, percentile={stats['percentile']:.2f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
