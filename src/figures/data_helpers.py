"""Workbook extraction and accounting checks shared by Figures 6--15."""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
import os
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.validation.workbook_reader import Sheet, Workbook


REPO_ROOT = Path(__file__).resolve().parents[2]
NATIONAL_WORKBOOK = Path(os.environ.get(
    "CEC_NATIONAL_WORKBOOK",
    REPO_ROOT / "data" / "output" / "tabela_final_cec_brasil.xlsx",
)).resolve()
UF_WORKBOOK = Path(os.environ.get(
    "CEC_UF_WORKBOOK",
    REPO_ROOT / "data" / "output" / "tabela_final_cec_ufs.xlsx",
)).resolve()

# These match the documented validation tolerances in DATA-DICTIONARY.md.
CURRENCY_TOLERANCE = 2.0
PERCENTAGE_TOLERANCE = 1e-8
UF_CODES = frozenset(
    {
        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
        "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
        "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
    }
)


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def require_number(value: Any, *, context: str) -> float:
    if not is_number(value):
        raise ValueError(f"Expected a numerical value for {context}; found {value!r}.")
    return float(value)


def assert_close(
    observed: float,
    expected: float,
    *,
    context: str,
    absolute: float = CURRENCY_TOLERANCE,
) -> None:
    if abs(observed - expected) > absolute:
        raise ValueError(
            f"{context}: observed {observed:.12g}, expected {expected:.12g}, "
            f"absolute difference {abs(observed - expected):.12g} exceeds {absolute}."
        )


@lru_cache(maxsize=2)
def workbook(path: str) -> Workbook:
    return Workbook(Path(path))


def header_map(sheet: Sheet) -> dict[str, int]:
    headers: dict[str, int] = {}
    for column in range(1, sheet.max_column + 1):
        cell = sheet.cell(1, column)
        if cell is not None and isinstance(cell.value, str) and cell.value:
            if cell.value in headers:
                raise ValueError(f"Duplicate header {cell.value!r} in {sheet.name}.")
            headers[cell.value] = column
    return headers


def sheet_records(
    path: Path,
    sheet_name: str,
    *,
    required_columns: Sequence[str],
    key_columns: Sequence[str],
) -> list[dict[str, Any]]:
    """Read keyed records from a worksheet using cached formula results."""

    book = workbook(str(path.resolve()))
    if sheet_name not in book.sheets:
        raise ValueError(f"Required worksheet {sheet_name!r} is absent from {path}.")
    sheet = book.sheets[sheet_name]
    headers = header_map(sheet)
    missing = sorted(set(required_columns) - set(headers))
    if missing:
        raise ValueError(f"Missing columns in {sheet_name}: {', '.join(missing)}")

    records: list[dict[str, Any]] = []
    for row in range(2, sheet.max_row + 1):
        key_values = [
            sheet.cell(row, headers[key]).value if sheet.cell(row, headers[key]) else None
            for key in key_columns
        ]
        if any(value is None for value in key_values):
            continue
        record = {
            name: (
                sheet.cell(row, headers[name]).value
                if sheet.cell(row, headers[name]) is not None
                else None
            )
            for name in required_columns
        }
        records.append(record)

    counts = Counter(tuple(record[key] for key in key_columns) for record in records)
    duplicates = [key for key, count in counts.items() if count > 1]
    if duplicates:
        raise ValueError(f"Duplicate keys in {sheet_name}: {duplicates[:5]}")
    return records


def index_by_year(records: Iterable[Mapping[str, Any]]) -> dict[int, Mapping[str, Any]]:
    result: dict[int, Mapping[str, Any]] = {}
    for record in records:
        year = int(require_number(record["ano"], context="ano"))
        if year in result:
            raise ValueError(f"Duplicate year {year}.")
        result[year] = record
    return result


def latest_complete_year(
    records: Iterable[Mapping[str, Any]], required_numeric: Sequence[str]
) -> int:
    eligible = [
        int(record["ano"])
        for record in records
        if all(is_number(record.get(field)) for field in required_numeric)
    ]
    if not eligible:
        raise ValueError(f"No complete year for required variables {required_numeric}.")
    return max(eligible)


def make_component_rows(
    *,
    year: int,
    components: Mapping[str, float],
    gdp: float,
    reported_total: float,
    nature: Mapping[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Create long-form rows and enforce the component accounting identity."""

    if gdp <= 0:
        raise ValueError(f"GDP must be positive in {year}.")
    if reported_total <= 0:
        raise ValueError(f"Reported total must be positive in {year}.")
    if any(value < 0 for value in components.values()):
        raise ValueError(f"Negative component in {year}: {components}")

    calculated_total = sum(components.values())
    assert_close(
        calculated_total,
        reported_total,
        context=f"Component identity in {year}",
    )
    rows: list[dict[str, Any]] = []
    for label, value in components.items():
        rows.append(
            {
                "ano": year,
                "componente": label,
                "natureza_contabil": (nature or {}).get(label, "PENDING"),
                "valor_reais_dez_2025": value,
                "pib_reais_dez_2025": gdp,
                "participacao_pib_pct": 100.0 * value / gdp,
                "composicao_pct": 100.0 * value / calculated_total,
                "total_calculado_reais_dez_2025": calculated_total,
                "total_reportado_reais_dez_2025": reported_total,
            }
        )

    composition = sum(float(row["composicao_pct"]) for row in rows)
    assert_close(
        composition,
        100.0,
        context=f"Composition identity in {year}",
        absolute=PERCENTAGE_TOLERANCE,
    )
    return rows


def national_summary() -> dict[int, Mapping[str, Any]]:
    columns = (
        "ano",
        "seguranca_publica",
        "seguranca_privada",
        "encarceramento",
        "seguros_&_danos_materiais",
        "processos_judiciais",
        "perdas_produtivas",
        "servicos_medicos",
        "custo_total_violencia",
        "pib_deflacionado",
    )
    return index_by_year(
        sheet_records(
            NATIONAL_WORKBOOK,
            "custo_total_violencia",
            required_columns=columns,
            key_columns=("ano",),
        )
    )


def uf_graph_records() -> list[dict[str, Any]]:
    columns = (
        "uf",
        "ano",
        "pib_estadual",
        "pib_per_capita",
        "populacao",
        "custo_total_crime",
        "seguranca_publica",
        "seguranca_privada",
        "encarceramento",
        "seguros_&_danos_materiais",
        "processos_judiciais",
        "perdas_produtivas",
        "servicos_medicos",
        "custo_total_%_pib",
        "seguranca_publica_%_pib",
        "seguranca_privada_%_pib",
        "encarceramento_%_pib",
        "seguros_&_danos_materiais_%_pib",
        "processos_judiciais_%_pib",
        "perdas_produtivas_%_pib",
        "servicos_medicos_%_pib",
    )
    records = sheet_records(
        UF_WORKBOOK,
        "graficos_ufs",
        required_columns=columns,
        key_columns=("uf", "ano"),
    )
    unexpected = sorted({str(record["uf"]) for record in records} - UF_CODES)
    if unexpected:
        raise ValueError(f"Unexpected UF codes in graficos_ufs: {unexpected}")
    return records


def latest_complete_uf_year(required_numeric: Sequence[str]) -> int:
    records = uf_graph_records()
    years = sorted({int(record["ano"]) for record in records})
    complete: list[int] = []
    for year in years:
        subset = [record for record in records if int(record["ano"]) == year]
        codes = {str(record["uf"]) for record in subset}
        if codes == UF_CODES and all(
            all(is_number(record.get(field)) for field in required_numeric)
            for record in subset
        ):
            complete.append(year)
    if not complete:
        raise ValueError("No year has complete coverage of all 27 UFs.")
    return max(complete)
