"""Build the fixed-geography microrregion homicide panel from retained SIM/IBGE inputs."""

from __future__ import annotations

from collections import Counter, defaultdict
import csv
import gzip
import io
import json
import math
from pathlib import Path
from typing import Any, BinaryIO, Iterable, Iterator, Mapping
import zipfile

import shapefile

from .homicide_config import (
    ANOS_SIM,
    AUDIT_DIR,
    BUILD_AUDIT_PATH,
    CROSSWALK_PATH,
    IBGE_POP_DIR,
    INTERIM_DIR,
    LOCALITIES_SOURCE,
    MICROREGION_SHAPE_SOURCE,
    MUNICIPAL_PANEL_PATH,
    PANEL_PATH,
    POPULATION_SOURCES,
    SIM_SOURCES,
)


CROSSWALK_FIELDS = (
    "municipality_code_7",
    "municipality_code_6",
    "municipality_name",
    "microrregion_code",
    "microrregion_name",
    "mesorregion_code",
    "mesorregion_name",
    "uf_code",
    "uf",
    "uf_name",
    "macroregion_code",
    "macroregion",
)

MUNICIPAL_FIELDS = CROSSWALK_FIELDS + (
    "year",
    "homicide_count",
    "population",
    "population_status",
)

MICROREGION_FIELDS = (
    "microrregion_code",
    "microrregion_name",
    "uf",
    "macroregion",
    "year",
    "homicide_count",
    "population",
    "homicide_rate_per_100k",
    "percentile_unweighted",
    "population_status",
    "homicide_definition",
    "sim_status",
)

HOMICIDE_DEFINITION = "CAUSABAS X85-X99, Y00-Y09, Y35 ou Y36; todas as idades; residência"


def _load_json_payload(path: Path) -> Any:
    payload = path.read_bytes()
    if payload[:2] == b"\x1f\x8b":
        payload = gzip.decompress(payload)
    return json.loads(payload.decode("utf-8-sig"))


def _atomic_write_csv(path: Path, rows: Iterable[Mapping[str, Any]], fields: tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)
    temp.replace(path)


def build_crosswalk() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    localities = _load_json_payload(LOCALITIES_SOURCE["target"])
    rows: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    for item in localities:
        micro = item.get("microrregiao")
        if not micro:
            excluded.append({"municipality_code_7": str(item["id"]), "municipality_name": item["nome"]})
            continue
        meso = micro["mesorregiao"]
        uf = meso["UF"]
        region = uf["regiao"]
        code7 = str(item["id"]).zfill(7)
        rows.append(
            {
                "municipality_code_7": code7,
                "municipality_code_6": code7[:6],
                "municipality_name": item["nome"],
                "microrregion_code": str(micro["id"]).zfill(5),
                "microrregion_name": micro["nome"],
                "mesorregion_code": str(meso["id"]).zfill(4),
                "mesorregion_name": meso["nome"],
                "uf_code": str(uf["id"]).zfill(2),
                "uf": uf["sigla"],
                "uf_name": uf["nome"],
                "macroregion_code": str(region["id"]),
                "macroregion": region["nome"],
            }
        )
    rows.sort(key=lambda row: row["municipality_code_7"])
    if len(rows) != 5570:
        raise ValueError(f"Expected 5,570 fixed-period municipalities; found {len(rows)}.")
    if len({row["municipality_code_7"] for row in rows}) != len(rows):
        raise ValueError("Duplicate seven-digit municipality code in IBGE crosswalk.")
    if len({row["municipality_code_6"] for row in rows}) != len(rows):
        raise ValueError("Six-digit SIM municipality code is not unique in IBGE crosswalk.")
    micro_codes = {row["microrregion_code"] for row in rows}
    if len(micro_codes) != 558:
        raise ValueError(f"Expected 558 old IBGE microrregions; found {len(micro_codes)}.")
    if len({row["uf"] for row in rows}) != 27:
        raise ValueError("The municipality crosswalk does not cover all 27 UFs.")
    _atomic_write_csv(CROSSWALK_PATH, rows, CROSSWALK_FIELDS)
    geometry = inspect_microrregion_geometry(micro_codes)
    return rows, {"excluded_localities": excluded, **geometry}


def _shape_reader(path: Path) -> shapefile.Reader:
    archive = zipfile.ZipFile(path)
    members = {Path(name).suffix.lower(): name for name in archive.namelist()}
    missing = {".shp", ".shx", ".dbf"} - set(members)
    if missing:
        archive.close()
        raise ValueError(f"Shapefile archive {path} is missing {sorted(missing)}.")
    reader = shapefile.Reader(
        shp=io.BytesIO(archive.read(members[".shp"])),
        shx=io.BytesIO(archive.read(members[".shx"])),
        dbf=io.BytesIO(archive.read(members[".dbf"])),
        encoding="latin1",
    )
    archive.close()
    return reader


def inspect_microrregion_geometry(expected_codes: set[str]) -> dict[str, Any]:
    reader = _shape_reader(MICROREGION_SHAPE_SOURCE["target"])
    codes = [str(record["CD_GEOCMI"]).zfill(5) for record in reader.iterRecords()]
    unique_codes = set(codes)
    if unique_codes != expected_codes:
        raise ValueError(
            "2015 microrregion geometry and municipality crosswalk disagree: "
            f"missing={sorted(expected_codes - unique_codes)}, extra={sorted(unique_codes - expected_codes)}"
        )
    duplicates = {code: count for code, count in Counter(codes).items() if count > 1}
    return {
        "geometry_feature_records": len(codes),
        "geometry_unique_microrregions": len(unique_codes),
        "geometry_multi_feature_codes": duplicates,
    }


def load_population() -> tuple[dict[int, dict[str, float]], dict[str, Any]]:
    by_year: dict[int, dict[str, float]] = {}
    audit: dict[str, Any] = {}
    for year, source in POPULATION_SOURCES.items():
        payload = _load_json_payload(source["target"])
        if not isinstance(payload, list) or len(payload) < 2:
            raise ValueError(f"Population source is empty or malformed for {year}: {source['target']}")
        values: dict[str, float] = {}
        invalid: list[dict[str, str]] = []
        for row in payload[1:]:
            code7 = str(row.get("D1C", "")).strip().zfill(7)
            raw_value = str(row.get("V", "")).strip()
            if not raw_value.isdigit():
                invalid.append({"municipality_code_7": code7, "name": row.get("D1N", ""), "value": raw_value})
                continue
            if code7 in values:
                raise ValueError(f"Duplicate municipality population key {year}-{code7}.")
            values[code7] = float(raw_value)
        by_year[year] = values
        audit[str(year)] = {
            "source_rows": len(payload) - 1,
            "numeric_rows": len(values),
            "nonnumeric_rows": invalid,
            "municipal_population_total": sum(values.values()),
            "source_reference": source["reference"],
        }
    common = set(by_year[2022]) & set(by_year[2024])
    by_year[2023] = {code: (by_year[2022][code] + by_year[2024][code]) / 2.0 for code in common}
    audit["2023"] = {
        "source_rows": len(common),
        "numeric_rows": len(common),
        "nonnumeric_rows": [],
        "municipal_population_total": sum(by_year[2023].values()),
        "source_reference": "Interpolação linear municipal entre Censo 2022 e estimativa 2024; diagnóstico apenas",
    }
    return by_year, audit


def is_homicide(cause: Any) -> bool:
    code = "".join(character for character in str(cause or "").upper() if character.isalnum())
    if len(code) < 3:
        return False
    stem = code[:3]
    if stem.startswith("X") and stem[1:].isdigit():
        return 85 <= int(stem[1:]) <= 99
    if stem.startswith("Y") and stem[1:].isdigit():
        number = int(stem[1:])
        return 0 <= number <= 9 or number in {35, 36}
    return False


def _death_year(value: Any) -> int | None:
    digits = "".join(character for character in str(value or "") if character.isdigit())
    if len(digits) < 4:
        return None
    year = int(digits[-4:])
    return year if 1900 <= year <= 2100 else None


def _municipality_code_6(value: Any) -> str | None:
    digits = "".join(character for character in str(value or "") if character.isdigit())
    if len(digits) == 7:
        digits = digits[:6]
    # SIM uses UF0000 when the state of residence is known but the municipality is not.
    if len(digits) != 6 or digits == "000000" or digits.endswith("0000"):
        return None
    return digits


def _iter_csv_zip(path: Path) -> Iterator[dict[str, str]]:
    with zipfile.ZipFile(path) as archive:
        members = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if len(members) != 1:
            raise ValueError(f"Expected one CSV in {path}; found {members}.")
        with archive.open(members[0]) as binary, io.TextIOWrapper(binary, encoding="latin1", newline="") as text:
            reader = csv.reader(text, delimiter=";")
            header = next(reader)
            indexes = {name: header.index(name) for name in ("DTOBITO", "CODMUNRES", "CAUSABAS", "IDADE", "CIRCOBITO")}
            maximum = max(indexes.values())
            for row in reader:
                if len(row) <= maximum:
                    continue
                yield {name: row[index] for name, index in indexes.items()}


def _iter_csv_file(path: Path) -> Iterator[dict[str, str]]:
    with path.open("r", encoding="latin1", newline="") as text:
        reader = csv.reader(text, delimiter=";")
        header = next(reader)
        indexes = {
            name: header.index(name)
            for name in ("DTOBITO", "CODMUNRES", "CAUSABAS", "IDADE", "CIRCOBITO")
        }
        maximum = max(indexes.values())
        for row in reader:
            if len(row) <= maximum:
                continue
            yield {name: row[index] for name, index in indexes.items()}


def _iter_json_array(text: io.TextIOBase, chunk_size: int = 1024 * 1024) -> Iterator[dict[str, Any]]:
    decoder = json.JSONDecoder()
    buffer = ""
    position = 0
    started = False
    ended = False
    while not ended:
        chunk = text.read(chunk_size)
        if chunk:
            buffer += chunk
        elif position >= len(buffer):
            break
        while True:
            while position < len(buffer) and buffer[position] in " \r\n\t,":
                position += 1
            if not started:
                if position >= len(buffer):
                    break
                if buffer[position] != "[":
                    raise ValueError("Expected a top-level JSON array in SIM JSON archive.")
                started = True
                position += 1
                continue
            while position < len(buffer) and buffer[position] in " \r\n\t,":
                position += 1
            if position < len(buffer) and buffer[position] == "]":
                ended = True
                position += 1
                break
            if position >= len(buffer):
                break
            try:
                value, end = decoder.raw_decode(buffer, position)
            except json.JSONDecodeError:
                break
            if not isinstance(value, dict):
                raise ValueError("SIM JSON array contains a non-object record.")
            yield value
            position = end
        if position > chunk_size:
            buffer = buffer[position:]
            position = 0
        if not chunk and not ended:
            remainder = buffer[position:].strip()
            if remainder:
                raise ValueError(f"Incomplete JSON stream; trailing content starts {remainder[:80]!r}.")
            break
    if not started or not ended:
        raise ValueError("SIM JSON archive did not contain one complete top-level array.")


def _iter_json_zip(path: Path) -> Iterator[dict[str, Any]]:
    with zipfile.ZipFile(path) as archive:
        members = sorted(name for name in archive.namelist() if name.lower().endswith(".json"))
        if not members:
            raise ValueError(f"Expected at least one JSON member in {path}.")
        for member in members:
            with archive.open(member) as binary, io.TextIOWrapper(binary, encoding="utf-8-sig") as text:
                yield from _iter_json_array(text)


def iter_sim_records(year: int) -> Iterator[dict[str, Any]]:
    source = SIM_SOURCES[year]
    if source["format"] == "csv_zip":
        yield from _iter_csv_zip(source["target"])
    elif source["format"] == "csv":
        yield from _iter_csv_file(source["target"])
    elif source["format"] == "json_zip":
        yield from _iter_json_zip(source["target"])
    else:  # pragma: no cover - protected by static configuration
        raise ValueError(f"Unsupported SIM format: {source['format']}")


def consolidate_sim(crosswalk: list[dict[str, Any]]) -> tuple[dict[int, Counter[str]], dict[str, Any]]:
    valid_codes = {row["municipality_code_6"] for row in crosswalk}
    counts: dict[int, Counter[str]] = {}
    audit: dict[str, Any] = {}
    for expected_year in ANOS_SIM:
        municipal = Counter()
        unmatched_codes: Counter[str] = Counter()
        raw_records = 0
        homicide_records = 0
        mapped_homicides = 0
        missing_date = 0
        wrong_year = 0
        missing_municipality = 0
        age_missing = 0
        circumstances: Counter[str] = Counter()
        for row in iter_sim_records(expected_year):
            raw_records += 1
            if not is_homicide(row.get("CAUSABAS")):
                continue
            homicide_records += 1
            year = _death_year(row.get("DTOBITO"))
            if year is None:
                missing_date += 1
                continue
            if year != expected_year:
                wrong_year += 1
                continue
            code6 = _municipality_code_6(row.get("CODMUNRES"))
            if code6 is None:
                missing_municipality += 1
                continue
            if code6 not in valid_codes:
                unmatched_codes[code6] += 1
                continue
            municipal[code6] += 1
            mapped_homicides += 1
            if not str(row.get("IDADE") or "").strip():
                age_missing += 1
            circumstances[str(row.get("CIRCOBITO") or "").strip() or "missing"] += 1
        counts[expected_year] = municipal
        excluded = homicide_records - mapped_homicides
        audit[str(expected_year)] = {
            "raw_mortality_records": raw_records,
            "official_sim_homicide_records": homicide_records,
            "mapped_homicides": mapped_homicides,
            "excluded_homicides": excluded,
            "match_rate_pct": 100.0 * mapped_homicides / homicide_records if homicide_records else 0.0,
            "missing_death_date": missing_date,
            "death_year_outside_annual_file": wrong_year,
            "missing_residence_municipality": missing_municipality,
            "unmatched_residence_codes": dict(sorted(unmatched_codes.items())),
            "homicides_with_missing_age_retained": age_missing,
            "circumstance_of_death_among_mapped_homicides": dict(sorted(circumstances.items())),
        }
        print(
            f"SIM {expected_year}: rows={raw_records:,} homicides={homicide_records:,} "
            f"mapped={mapped_homicides:,} match={audit[str(expected_year)]['match_rate_pct']:.4f}%"
        )
    return counts, audit


def _average_rank_percentiles(values: Mapping[str, float]) -> dict[str, float]:
    ordered = sorted(values.items(), key=lambda item: (item[1], item[0]))
    result: dict[str, float] = {}
    position = 0
    n = len(ordered)
    while position < n:
        end = position + 1
        while end < n and math.isclose(ordered[end][1], ordered[position][1], rel_tol=0.0, abs_tol=1e-12):
            end += 1
        average_rank = ((position + 1) + end) / 2.0
        percentile = 100.0 * average_rank / n
        for index in range(position, end):
            result[ordered[index][0]] = percentile
        position = end
    return result


def build_panels(
    crosswalk: list[dict[str, Any]],
    populations: dict[int, dict[str, float]],
    homicide_counts: dict[int, Counter[str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    municipal_rows: list[dict[str, Any]] = []
    population_status = {
        2015: "estimativa IBGE em 1º de julho",
        2016: "estimativa IBGE em 1º de julho",
        2017: "estimativa IBGE em 1º de julho",
        2022: "Censo 2022 em 1º de agosto",
        2023: "interpolação linear municipal 2022–2024; diagnóstico apenas",
        2024: "estimativa IBGE em 1º de julho",
    }
    coverage: dict[str, Any] = {}
    for year in ANOS_SIM:
        missing_population = sorted(
            row["municipality_code_7"] for row in crosswalk if row["municipality_code_7"] not in populations[year]
        )
        extra_population = sorted(set(populations[year]) - {row["municipality_code_7"] for row in crosswalk})
        if missing_population:
            raise ValueError(f"Missing population for {year}: {missing_population[:20]}")
        coverage[str(year)] = {
            "municipality_rows": len(crosswalk),
            "missing_population_codes": missing_population,
            "extra_numeric_population_codes": extra_population,
        }
        for row in crosswalk:
            code6 = row["municipality_code_6"]
            code7 = row["municipality_code_7"]
            municipal_rows.append(
                {
                    **row,
                    "year": year,
                    "homicide_count": homicide_counts[year].get(code6, 0),
                    "population": populations[year][code7],
                    "population_status": population_status[year],
                }
            )
    _atomic_write_csv(MUNICIPAL_PANEL_PATH, municipal_rows, MUNICIPAL_FIELDS)

    grouped: dict[tuple[str, int], dict[str, Any]] = {}
    for row in municipal_rows:
        key = (row["microrregion_code"], row["year"])
        if key not in grouped:
            grouped[key] = {
                "microrregion_code": row["microrregion_code"],
                "microrregion_name": row["microrregion_name"],
                "uf": row["uf"],
                "macroregion": row["macroregion"],
                "year": row["year"],
                "homicide_count": 0,
                "population": 0.0,
                "population_status": row["population_status"],
            }
        aggregate = grouped[key]
        aggregate["homicide_count"] += int(row["homicide_count"])
        aggregate["population"] += float(row["population"])
    panel_rows: list[dict[str, Any]] = []
    for year in ANOS_SIM:
        year_rows = [row for (_, row_year), row in grouped.items() if row_year == year]
        rates = {
            row["microrregion_code"]: 100000.0 * row["homicide_count"] / row["population"]
            for row in year_rows
        }
        percentiles = _average_rank_percentiles(rates)
        for row in year_rows:
            code = row["microrregion_code"]
            panel_rows.append(
                {
                    **row,
                    "homicide_rate_per_100k": rates[code],
                    "percentile_unweighted": percentiles[code],
                    "homicide_definition": HOMICIDE_DEFINITION,
                    "sim_status": "final",
                }
            )
    panel_rows.sort(key=lambda row: (int(row["year"]), row["microrregion_code"]))
    _atomic_write_csv(PANEL_PATH, panel_rows, MICROREGION_FIELDS)
    return municipal_rows, panel_rows, coverage


def main() -> int:
    for source in SIM_SOURCES.values():
        if not source["target"].exists():
            raise FileNotFoundError(f"Missing retained SIM input: {source['target']}")
    for source in POPULATION_SOURCES.values():
        if not source["target"].exists():
            raise FileNotFoundError(f"Missing retained IBGE population input: {source['target']}")
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    crosswalk, geography_audit = build_crosswalk()
    populations, population_audit = load_population()
    homicide_counts, sim_audit = consolidate_sim(crosswalk)
    municipal_rows, panel_rows, coverage_audit = build_panels(crosswalk, populations, homicide_counts)
    audit = {
        "schema_version": 1,
        "homicide_definition": HOMICIDE_DEFINITION,
        "years": list(ANOS_SIM),
        "crosswalk": {
            "municipalities": len(crosswalk),
            "microrregions": len({row["microrregion_code"] for row in crosswalk}),
            "ufs": len({row["uf"] for row in crosswalk}),
            **geography_audit,
        },
        "population": population_audit,
        "sim": sim_audit,
        "coverage": coverage_audit,
        "outputs": {
            "municipality_year_rows": len(municipal_rows),
            "microrregion_year_rows": len(panel_rows),
        },
    }
    temp = BUILD_AUDIT_PATH.with_suffix(".json.tmp")
    temp.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(BUILD_AUDIT_PATH)
    print(f"WROTE {CROSSWALK_PATH}")
    print(f"WROTE {MUNICIPAL_PANEL_PATH} ({len(municipal_rows):,} rows)")
    print(f"WROTE {PANEL_PATH} ({len(panel_rows):,} rows)")
    print(f"WROTE {BUILD_AUDIT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
