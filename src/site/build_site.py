"""Assemble the bilingual GitHub Pages site from retained publication outputs.

The site is a presentation layer only. It copies the exact figure-ready CSVs,
the published report files, and a simplified version of the fixed 2015 IBGE
microregion geometry. No analytical value is recalculated here.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import shutil
import zipfile
from pathlib import Path
from typing import Iterable, Sequence

import shapefile


ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
DATA = SITE / "data"
DOWNLOADS = SITE / "downloads"
FIGURE_DATA = ROOT / "data" / "figure_data"
GEOGRAPHY_ZIP = ROOT / "data" / "raw" / "ibge_geography" / "ibge_2015_br_microrregioes.zip"
GEOJSON = DATA / "geography" / "ibge_2015_microregions_simplified.geojson"
GEOGRAPHY_STAGING = ROOT / "build" / "site-shape"
MANIFEST = SITE / "site-manifest.json"

CSV_NAMES = (
    "fig_01_distribuicao_mundial_homicidios.csv",
    "fig_02a_crimes_registrados.csv",
    "fig_02b_taxas_criminalidade.csv",
    "fig_02c_crimes_cobertura_parcial.csv",
    "fig_02d_taxas_cobertura_parcial.csv",
    "fig_03_microrregion_homicides.csv",
    "fig_04_microrregion_homicide_change.csv",
    "fig_05_microrregion_homicide_convergence.csv",
    "fig_06_public_security.csv",
    "fig_07_private_security.csv",
    "fig_08_incarceration.csv",
    "fig_09_insurance_material_losses.csv",
    "fig_10_productive_capacity.csv",
    "fig_11_judicial_costs.csv",
    "fig_12_medical_costs.csv",
    "fig_13_total_costs.csv",
    "fig_14_state_costs.csv",
    "fig_15_state_trajectories.csv",
)

ENGLISH_CSV_NAMES = {
    "fig_01_distribuicao_mundial_homicidios.csv": "fig_01_world_homicides_en.csv",
    "fig_02a_crimes_registrados.csv": "fig_02a_recorded_crime_en.csv",
    "fig_02b_taxas_criminalidade.csv": "fig_02b_crime_rates_en.csv",
    "fig_02c_crimes_cobertura_parcial.csv": "fig_02c_partial_coverage_counts_en.csv",
    "fig_02d_taxas_cobertura_parcial.csv": "fig_02d_partial_coverage_rates_en.csv",
    "fig_03_microrregion_homicides.csv": "fig_03_microregion_homicides_en.csv",
    "fig_04_microrregion_homicide_change.csv": "fig_04_microregion_homicide_change_en.csv",
    "fig_05_microrregion_homicide_convergence.csv": "fig_05_microregion_homicide_convergence_en.csv",
    "fig_06_public_security.csv": "fig_06_public_security_en.csv",
    "fig_07_private_security.csv": "fig_07_private_security_en.csv",
    "fig_08_incarceration.csv": "fig_08_incarceration_en.csv",
    "fig_09_insurance_material_losses.csv": "fig_09_insurance_material_losses_en.csv",
    "fig_10_productive_capacity.csv": "fig_10_productive_capacity_en.csv",
    "fig_11_judicial_costs.csv": "fig_11_judicial_costs_en.csv",
    "fig_12_medical_costs.csv": "fig_12_medical_costs_en.csv",
    "fig_13_total_costs.csv": "fig_13_total_costs_en.csv",
    "fig_14_state_costs.csv": "fig_14_state_costs_en.csv",
    "fig_15_state_trajectories.csv": "fig_15_state_trajectories_en.csv",
}

REPORT_FILES = (
    "docs/report.pdf",
    "docs/report.docx",
    "docs/report.md",
    "docs/report-en.pdf",
    "docs/report-en.docx",
    "docs/report-en.md",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _perpendicular_distance(point: Sequence[float], start: Sequence[float], end: Sequence[float]) -> float:
    if start == end:
        return math.hypot(point[0] - start[0], point[1] - start[1])
    numerator = abs(
        (end[1] - start[1]) * point[0]
        - (end[0] - start[0]) * point[1]
        + end[0] * start[1]
        - end[1] * start[0]
    )
    denominator = math.hypot(end[1] - start[1], end[0] - start[0])
    return numerator / denominator


def _simplify_open(points: list[list[float]], tolerance: float) -> list[list[float]]:
    if len(points) <= 2:
        return points
    maximum = 0.0
    split = 0
    for index in range(1, len(points) - 1):
        distance = _perpendicular_distance(points[index], points[0], points[-1])
        if distance > maximum:
            maximum = distance
            split = index
    if maximum <= tolerance:
        return [points[0], points[-1]]
    left = _simplify_open(points[: split + 1], tolerance)
    right = _simplify_open(points[split:], tolerance)
    return left[:-1] + right


def _simplify_ring(coordinates: Iterable[Sequence[float]], tolerance: float = 0.018) -> list[list[float]]:
    points = [[round(float(point[0]), 5), round(float(point[1]), 5)] for point in coordinates]
    if len(points) < 5:
        return points
    closed = points[0] == points[-1]
    core = points[:-1] if closed else points
    # Rotate a ring before Douglas-Peucker so its identical endpoints do not
    # collapse the entire shape. The farthest point from the first is stable.
    pivot = max(range(1, len(core)), key=lambda index: _perpendicular_distance(core[index], core[0], core[0]))
    rotated = core[pivot:] + core[: pivot + 1]
    simplified = _simplify_open(rotated, tolerance)
    if len(simplified) < 4:
        simplified = rotated[:: max(1, len(rotated) // 4)]
    if simplified[0] != simplified[-1]:
        simplified.append(simplified[0])
    return simplified


def _simplify_geometry(geometry: dict[str, object]) -> dict[str, object]:
    kind = str(geometry["type"])
    coordinates = geometry["coordinates"]
    if kind == "Polygon":
        simplified = [_simplify_ring(ring) for ring in coordinates]  # type: ignore[arg-type]
    elif kind == "MultiPolygon":
        simplified = [
            [_simplify_ring(ring) for ring in polygon]
            for polygon in coordinates  # type: ignore[assignment]
        ]
    else:
        raise ValueError(f"Unexpected microregion geometry type: {kind}")
    return {"type": kind, "coordinates": simplified}


def build_geojson() -> None:
    GEOJSON.parent.mkdir(parents=True, exist_ok=True)
    GEOGRAPHY_STAGING.mkdir(parents=True, exist_ok=True)
    shape_files = list(GEOGRAPHY_STAGING.glob("*.shp"))
    if not shape_files:
        with zipfile.ZipFile(GEOGRAPHY_ZIP) as archive:
            archive.extractall(GEOGRAPHY_STAGING)
        shape_files = list(GEOGRAPHY_STAGING.glob("*.shp"))
    if len(shape_files) != 1:
        raise AssertionError(f"Expected one staged IBGE shapefile; found {shape_files}")
    reader = shapefile.Reader(str(shape_files[0]), encoding="latin1")
    fields = [field[0] for field in reader.fields[1:]]
    code_index = fields.index("CD_GEOCMI")
    name_index = fields.index("NM_MICRO")
    grouped: dict[str, dict[str, object]] = {}
    for record, shape in zip(reader.records(), reader.shapes()):
        code = str(record[code_index]).zfill(5)
        geometry = _simplify_geometry(shape.__geo_interface__)
        polygons = (
            [geometry["coordinates"]]
            if geometry["type"] == "Polygon"
            else list(geometry["coordinates"])  # type: ignore[arg-type]
        )
        if code not in grouped:
            grouped[code] = {
                "name": str(record[name_index]).title(),
                "polygons": polygons,
            }
        else:
            grouped[code]["polygons"].extend(polygons)  # type: ignore[union-attr]
    features = [
        {
            "type": "Feature",
            "id": code,
            "properties": {"code": code, "name": str(item["name"])},
            "geometry": {"type": "MultiPolygon", "coordinates": item["polygons"]},
        }
        for code, item in sorted(grouped.items())
    ]
    if len(features) != 558 or len({feature["id"] for feature in features}) != 558:
        raise AssertionError("Expected 558 unique fixed-2015 IBGE microregions in site geography")
    GEOJSON.write_text(
        json.dumps({"type": "FeatureCollection", "features": features}, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )


def copy_publication_files() -> list[Path]:
    copied: list[Path] = []
    for language in ("pt", "en"):
        target = DATA / language
        target.mkdir(parents=True, exist_ok=True)
    for name in CSV_NAMES:
        source = FIGURE_DATA / name
        if not source.exists() or source.stat().st_size == 0:
            raise FileNotFoundError(source)
        target = DATA / "pt" / name
        shutil.copy2(source, target)
        copied.append(target)
        english_name = ENGLISH_CSV_NAMES[name]
        english_source = FIGURE_DATA / "en" / english_name
        if not english_source.exists() or english_source.stat().st_size == 0:
            raise FileNotFoundError(english_source)
        english_target = DATA / "en" / english_name
        shutil.copy2(english_source, english_target)
        copied.append(english_target)

    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    for relative in REPORT_FILES:
        source = ROOT / relative
        if not source.exists() or source.stat().st_size == 0:
            raise FileNotFoundError(source)
        target = DOWNLOADS / source.name
        shutil.copy2(source, target)
        copied.append(target)
    return copied


def validate_csvs() -> None:
    for name in CSV_NAMES:
        for path in (DATA / "pt" / name, DATA / "en" / ENGLISH_CSV_NAMES[name]):
            with path.open("r", encoding="utf-8", newline="") as stream:
                reader = csv.DictReader(stream)
                rows = list(reader)
            if not reader.fieldnames or not rows:
                raise AssertionError(f"Empty or malformed site CSV: {path}")


def main() -> int:
    if not SITE.exists():
        raise FileNotFoundError("Static site source directory is missing")
    (ROOT / "build").mkdir(exist_ok=True)
    copied = copy_publication_files()
    build_geojson()
    validate_csvs()
    required = (
        SITE / "index.html",
        SITE / "favicon.svg",
        SITE / "assets" / "css" / "styles.css",
        SITE / "assets" / "js" / "app.js",
        SITE / "assets" / "vendor" / "plotly-2.35.2.min.js",
        SITE / "assets" / "vendor" / "plotly-2.35.2.min.js.LICENSE.txt",
    )
    if any(not path.exists() or path.stat().st_size == 0 for path in required):
        raise AssertionError("Static site source assets are incomplete")
    generated = [path for path in SITE.rglob("*") if path.is_file() and path != MANIFEST]
    records = [
        {
            "path": path.relative_to(SITE).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in sorted(generated)
    ]
    MANIFEST.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"PASS: site assembled with {len(CSV_NAMES)} Portuguese CSVs, "
        f"{len(CSV_NAMES)} English CSVs, 558 microregions, and {len(REPORT_FILES)} report downloads"
    )
    print(f"SITE: {SITE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
