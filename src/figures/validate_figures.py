"""Validate figure-ready data and outputs for Figures 6--15.

The numerical tolerances are inherited from the workbook audit: R$ 2 for
cached/rounded monetary identities and 1e-8 percentage point for shares.
They are not calibrated to the 2018 report.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .common import MANIFEST_PATH, REPO_ROOT, read_csv, sha256
from .data_helpers import (
    CURRENCY_TOLERANCE,
    NATIONAL_WORKBOOK,
    PERCENTAGE_TOLERANCE,
    UF_CODES,
    assert_close,
    is_number,
    latest_complete_uf_year,
    national_summary,
    sheet_records,
)
from .fig_06_public_security import CONFIG as FIG06
from .fig_07_private_security import CONFIG as FIG07
from .fig_08_incarceration import CONFIG as FIG08
from .fig_09_insurance_material_losses import CONFIG as FIG09
from .fig_10_productive_capacity import CONFIG as FIG10
from .fig_11_judicial_costs import CONFIG as FIG11
from .fig_12_medical_costs import CONFIG as FIG12
from .fig_13_total_costs import CONFIG as FIG13
from .fig_14_state_costs import CONFIG as FIG14
from .fig_15_state_trajectories import CONFIG as FIG15


GENERIC_CONFIGS = (FIG07, FIG08, FIG09, FIG10, FIG11, FIG12, FIG13)
ALL_CONFIGS = (FIG06, *GENERIC_CONFIGS, FIG14, FIG15)


def number(row: Mapping[str, str], field: str, *, context: str) -> float:
    try:
        value = float(row[field])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"Non-numeric {field} in {context}: {row.get(field)!r}") from error
    if value != value or value in (float("inf"), float("-inf")):
        raise ValueError(f"Non-finite {field} in {context}: {value}")
    return value


def require_unique(rows: Sequence[Mapping[str, str]], fields: Sequence[str], *, context: str) -> None:
    keys = [tuple(row[field] for field in fields) for row in rows]
    duplicates = [key for key, count in Counter(keys).items() if count > 1]
    if duplicates:
        raise ValueError(f"Duplicate {context} keys: {duplicates[:10]}")


def validate_nonnegative(rows: Sequence[Mapping[str, str]], *, context: str) -> None:
    for row in rows:
        value = number(row, "valor_reais_dez_2025", context=context)
        if value < 0:
            raise ValueError(f"Negative plotted value in {context}: {row}")
        share = number(row, "participacao_pib_pct", context=context)
        if share < 0 or share > 100:
            raise ValueError(f"Implausibly scaled GDP share in {context}: {row}")


def validate_generic(config: Mapping[str, Any]) -> None:
    rows = read_csv(Path(config["data_file"]))
    expected_components = set(config["component_order"])
    require_unique(rows, ("ano", "componente"), context=config["output_stem"])
    validate_nonnegative(rows, context=config["output_stem"])
    years = sorted({int(row["ano"]) for row in rows})
    if years != list(range(min(years), max(years) + 1)):
        raise ValueError(f"Non-contiguous years in {config['output_stem']}: {years}")
    if max(years) != max(national_summary()):
        raise ValueError(f"Terminal year mismatch in {config['output_stem']}.")
    by_year: dict[int, list[Mapping[str, str]]] = defaultdict(list)
    for row in rows:
        by_year[int(row["ano"])].append(row)
    for year, subset in by_year.items():
        if {row["componente"] for row in subset} != expected_components:
            raise ValueError(f"Component coverage mismatch in {config['output_stem']} for {year}.")
        values = sum(number(row, "valor_reais_dez_2025", context=f"{config['output_stem']} {year}") for row in subset)
        reported = number(subset[0], "total_reportado_reais_dez_2025", context=f"{config['output_stem']} {year}")
        calculated = number(subset[0], "total_calculado_reais_dez_2025", context=f"{config['output_stem']} {year}")
        assert_close(values, calculated, context=f"CSV calculated total {config['output_stem']} {year}")
        assert_close(calculated, reported, context=f"CSV reported total {config['output_stem']} {year}")
        composition = sum(number(row, "composicao_pct", context=f"{config['output_stem']} {year}") for row in subset)
        assert_close(composition, 100.0, context=f"composition {config['output_stem']} {year}", absolute=PERCENTAGE_TOLERANCE)
        gdp = number(subset[0], "pib_reais_dez_2025", context=f"{config['output_stem']} {year}")
        gdp_share = sum(number(row, "participacao_pib_pct", context=f"{config['output_stem']} {year}") for row in subset)
        assert_close(gdp_share, 100.0 * reported / gdp, context=f"GDP shares {config['output_stem']} {year}", absolute=PERCENTAGE_TOLERANCE)


def validate_figure_06() -> None:
    rows = read_csv(Path(FIG06["data_file"]))
    require_unique(rows, ("ano", "componente"), context=FIG06["output_stem"])
    validate_nonnegative(rows, context=FIG06["output_stem"])
    totals = [row for row in rows if row["serie"] == "total"]
    components = [row for row in rows if row["serie"] == "decomposição"]
    total_years = sorted(int(row["ano"]) for row in totals)
    if total_years != list(range(min(total_years), max(total_years) + 1)):
        raise ValueError("Figure 6 total series is not contiguous.")
    if max(total_years) != max(national_summary()):
        raise ValueError("Figure 6 terminal year does not match the national workbook.")

    source = sheet_records(
        NATIONAL_WORKBOOK,
        "seguranca_publica_br",
        required_columns=("ano", "uniao", "ufs", "municipios"),
        key_columns=("ano",),
    )
    expected_component_years = {
        int(record["ano"])
        for record in source
        if all(is_number(record[field]) for field in ("uniao", "ufs", "municipios"))
    }
    actual_component_years = {int(row["ano"]) for row in components}
    if actual_component_years != expected_component_years:
        raise ValueError(
            "Figure 6 decomposition is not dynamically aligned with populated workbook components: "
            f"expected={sorted(expected_component_years)}, actual={sorted(actual_component_years)}"
        )
    expected_components = set(FIG06["component_order"])
    by_year: dict[int, list[Mapping[str, str]]] = defaultdict(list)
    for row in components:
        by_year[int(row["ano"])].append(row)
    totals_by_year = {int(row["ano"]): row for row in totals}
    for year, subset in by_year.items():
        if {row["componente"] for row in subset} != expected_components:
            raise ValueError(f"Incomplete Figure 6 decomposition in {year}.")
        value_sum = sum(number(row, "valor_reais_dez_2025", context=f"fig06 {year}") for row in subset)
        total = number(totals_by_year[year], "valor_reais_dez_2025", context=f"fig06 total {year}")
        assert_close(value_sum, total, context=f"Figure 6 component total {year}")
        composition = sum(number(row, "composicao_pct", context=f"fig06 {year}") for row in subset)
        assert_close(composition, 100.0, context=f"Figure 6 composition {year}", absolute=PERCENTAGE_TOLERANCE)


def validate_figure_14() -> None:
    rows = read_csv(Path(FIG14["data_file"]))
    require_unique(rows, ("uf", "ano", "componente"), context=FIG14["output_stem"])
    validate_nonnegative(rows, context=FIG14["output_stem"])
    years = {int(row["ano"]) for row in rows}
    required_fields = (
        "pib_estadual", "populacao", "pib_per_capita", "custo_total_crime", "custo_total_%_pib",
        "seguranca_publica", "seguranca_privada", "encarceramento", "seguros_&_danos_materiais",
        "processos_judiciais", "perdas_produtivas", "servicos_medicos",
    )
    expected_year = latest_complete_uf_year(required_fields)
    if years != {expected_year}:
        raise ValueError(f"Figure 14 terminal year mismatch: {years} versus {expected_year}.")
    if {row["uf"] for row in rows} != UF_CODES:
        raise ValueError("Figure 14 does not include all 27 UFs.")
    expected_components = set(FIG14["component_order"])
    by_uf: dict[str, list[Mapping[str, str]]] = defaultdict(list)
    for row in rows:
        by_uf[row["uf"]].append(row)
    for uf, subset in by_uf.items():
        if {row["componente"] for row in subset} != expected_components:
            raise ValueError(f"Figure 14 component coverage mismatch for {uf}.")
        values = sum(number(row, "valor_reais_dez_2025", context=f"fig14 {uf}") for row in subset)
        total = number(subset[0], "custo_total_reais_dez_2025", context=f"fig14 {uf}")
        assert_close(values, total, context=f"Figure 14 value identity {uf}")
        shares = sum(number(row, "participacao_pib_pct", context=f"fig14 {uf}") for row in subset)
        total_share = number(subset[0], "custo_total_pib_pct", context=f"fig14 {uf}")
        assert_close(shares, total_share, context=f"Figure 14 GDP-share identity {uf}", absolute=PERCENTAGE_TOLERANCE)
        composition = sum(number(row, "composicao_total_pct", context=f"fig14 {uf}") for row in subset)
        assert_close(composition, 100.0, context=f"Figure 14 composition {uf}", absolute=PERCENTAGE_TOLERANCE)


def validate_figure_15() -> None:
    rows = read_csv(Path(FIG15["data_file"]))
    require_unique(rows, ("uf", "ano"), context=FIG15["output_stem"])
    years = sorted({int(row["ano"]) for row in rows})
    end_year = latest_complete_uf_year(("pib_estadual", "populacao", "pib_per_capita", "custo_total_crime", "custo_total_%_pib"))
    if years != [FIG15["parameters"]["start_year"], end_year]:
        raise ValueError(f"Figure 15 endpoint mismatch: {years}.")
    for year in years:
        codes = {row["uf"] for row in rows if int(row["ano"]) == year}
        if codes != UF_CODES:
            raise ValueError(f"Figure 15 lacks 27 UFs in {year}.")
    for row in rows:
        if number(row, "pib_per_capita_reais_dez_2025", context="fig15") <= 0:
            raise ValueError(f"Non-positive GDP per capita in Figure 15: {row}")
        share = number(row, "custo_total_pib_pct", context="fig15")
        if share < 0 or share > 100:
            raise ValueError(f"Implausibly scaled cost share in Figure 15: {row}")


def validate_outputs() -> None:
    if not MANIFEST_PATH.exists():
        raise ValueError(f"Missing output manifest: {MANIFEST_PATH}")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    for config in ALL_CONFIGS:
        stem = str(config["output_stem"])
        if stem not in manifest:
            raise ValueError(f"Missing manifest entry for {stem}.")
        entry = manifest[stem]
        data_path = REPO_ROOT / entry["data_file"]
        pdf_path = REPO_ROOT / entry["pdf_file"]
        png_path = REPO_ROOT / entry["png_file"]
        for path in (data_path, pdf_path, png_path):
            if not path.exists() or path.stat().st_size == 0:
                raise ValueError(f"Missing or empty output for {stem}: {path}")
        if pdf_path.read_bytes()[:4] != b"%PDF":
            raise ValueError(f"Invalid PDF signature for {stem}.")
        if png_path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"Invalid PNG signature for {stem}.")
        for path, field in ((data_path, "data_sha256"), (pdf_path, "pdf_sha256"), (png_path, "png_sha256")):
            if sha256(path) != entry[field]:
                raise ValueError(f"Manifest checksum mismatch for {path}.")


def main() -> int:
    checks = (
        ("Figure 6", validate_figure_06),
        *((config["output_stem"], lambda config=config: validate_generic(config)) for config in GENERIC_CONFIGS),
        ("Figure 14", validate_figure_14),
        ("Figure 15", validate_figure_15),
        ("Output files and manifest", validate_outputs),
    )
    errors: list[str] = []
    passed = 0
    for label, check in checks:
        try:
            check()
        except Exception as error:  # validation must summarize all failures
            errors.append(f"{label}: {error}")
            print(f"ERROR {label}: {error}")
        else:
            passed += 1
            print(f"PASS  {label}")
    print(
        "WARNING UF figures use the documented non-blocking 2025 state-data warnings "
        "(productive losses and incarceration concept); pre-publication rebuild required."
    )
    print("WARNING GDP and population release/vintage metadata remain PENDING.")
    print(f"SUMMARY checks={len(checks)} passed={passed} errors={len(errors)} warnings=2")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
