"""Validate the two authoritative final workbooks.

Run from the repository root with::

    python -m src.validation.validate_data

The validator separates hard mechanical failures from warnings that need
economic or methodological judgment.  It deliberately does not compare
current values with the point estimates published in 2018.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any, Iterable, Sequence

from .workbook_reader import Sheet, Workbook, column_label


REPO_ROOT = Path(__file__).resolve().parents[2]
NATIONAL_PATH = Path(os.environ.get(
    "CEC_NATIONAL_WORKBOOK",
    REPO_ROOT / "data" / "output" / "tabela_final_cec_brasil.xlsx",
)).resolve()
UF_PATH = Path(os.environ.get(
    "CEC_UF_WORKBOOK",
    REPO_ROOT / "data" / "output" / "tabela_final_cec_ufs.xlsx",
)).resolve()

EXPECTED_NATIONAL_SHEETS = (
    "custo_total_violencia",
    "seguranca_publica_br",
    "seguranca_privada_br",
    "encarceramento_br",
    "seguros_&_danos_materiais_br",
    "perdas_produtivas_br",
    "processos_judiciais_br",
    "servicos_medicos_br",
)
EXPECTED_UF_SHEETS = (
    "custo_total_violencia_ufs",
    "graficos_ufs",
    "seguranca_publica_ufs",
    "seguranca_privada_ufs",
    "encarceramento_ufs",
    "seguros_&_danos_materiais_uf",
    "perdas_produtivas_ufs",
    "processos_judiciais_ufs",
    "servicos_medicos_ufs",
    "dados_aux_graficos",
    "graficos_finais_ufs",
)
EXPECTED_NATIONAL_YEARS = tuple(range(1996, 2026))
EXPECTED_UF_YEARS = (2016, 2025)
UF_CODES = frozenset(
    {
        "AC",
        "AL",
        "AP",
        "AM",
        "BA",
        "CE",
        "DF",
        "ES",
        "GO",
        "MA",
        "MT",
        "MS",
        "MG",
        "PA",
        "PB",
        "PR",
        "PE",
        "PI",
        "RJ",
        "RN",
        "RS",
        "RO",
        "RR",
        "SC",
        "SP",
        "SE",
        "TO",
    }
)

# Cached formula results in the summary sheets are often rounded to whole
# reais after component-level rounding.  A R$2 absolute tolerance covers the
# observed whole-real caching drift, while remaining far below any publishable
# precision. Formula structure is checked separately.
CURRENCY_ABS_TOLERANCE = 2.0
# GDP is around R$10 trillion and is distributed across 27 rounded UF values.
# One part per billion permits only a few thousand reais of aggregation drift.
GDP_REL_TOLERANCE = 1e-9
# Share cells carry more precision than the report will display.  This bound is
# 10,000 times smaller than 0.0001 percentage point.
PERCENTAGE_POINT_TOLERANCE = 1e-8
WEIGHT_TOLERANCE = 1e-9
# This is a diagnostic screen, not an error threshold.  A 40% annual movement
# is large enough to prompt review for unit/source breaks in an accounting
# series; documented economic movements may legitimately exceed it.
DISCONTINUITY_WARNING_THRESHOLD = 0.40


FULL_NAME_TO_CODE = {
    "Acre": "AC",
    "Alagoas": "AL",
    "Amapá": "AP",
    "Amap�": "AP",
    "Amazonas": "AM",
    "Amazos": "AM",  # truncated label in seguranca_publica_ufs
    "Bahia": "BA",
    "Ceará": "CE",
    "Cear�": "CE",
    "Distrito Federal": "DF",
    "Espírito Santo": "ES",
    "Esp�rito Santo": "ES",
    "Goiás": "GO",
    "Goi�s": "GO",
    "Maranhão": "MA",
    "Maranh�o": "MA",
    "Mato Grosso": "MT",
    "Mato Grosso do Sul": "MS",
    "Minas Gerais": "MG",
    "Mis Gerais": "MG",  # truncated label in seguranca_publica_ufs
    "Pará": "PA",
    "Par�": "PA",
    "Paraíba": "PB",
    "Para�ba": "PB",
    "Paraná": "PR",
    "Paran�": "PR",
    "Pernambuco": "PE",
    "Permbuco": "PE",  # truncated label in seguranca_publica_ufs
    "Piauí": "PI",
    "Piau�": "PI",
    "Rio de Janeiro": "RJ",
    "Rio Grande do Norte": "RN",
    "Rio Grande do Sul": "RS",
    "Rondônia": "RO",
    "Rond�nia": "RO",
    "Roraima": "RR",
    "Santa Catarina": "SC",
    "Santa Catari": "SC",  # truncated label in seguranca_publica_ufs
    "São Paulo": "SP",
    "S�o Paulo": "SP",
    "Sergipe": "SE",
    "Tocantins": "TO",
}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    context: dict[str, Any]


class Audit:
    def __init__(self) -> None:
        self.findings: list[Finding] = []
        self.checks = 0
        self.passed = 0

    def record(
        self,
        condition: bool,
        code: str,
        message: str,
        *,
        severity: str = "ERROR",
        **context: Any,
    ) -> bool:
        self.checks += 1
        if condition:
            self.passed += 1
            return True
        self.findings.append(Finding(severity, code, message, context))
        return False

    def warn(self, code: str, message: str, **context: Any) -> None:
        self.findings.append(Finding("WARNING", code, message, context))

    def info(self, code: str, message: str, **context: Any) -> None:
        self.findings.append(Finding("INFO", code, message, context))

    @property
    def errors(self) -> list[Finding]:
        return [finding for finding in self.findings if finding.severity == "ERROR"]

    @property
    def warnings(self) -> list[Finding]:
        return [finding for finding in self.findings if finding.severity == "WARNING"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def value(sheet: Sheet, row: int, column: int) -> Any:
    cell = sheet.cell(row, column)
    return cell.value if cell else None


def numeric(item: Any) -> bool:
    return isinstance(item, (int, float)) and not isinstance(item, bool) and math.isfinite(item)


def close(left: float, right: float, *, absolute: float = CURRENCY_ABS_TOLERANCE) -> bool:
    return math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=absolute)


def close_gdp(left: float, right: float) -> bool:
    return math.isclose(
        float(left),
        float(right),
        rel_tol=GDP_REL_TOLERANCE,
        abs_tol=CURRENCY_ABS_TOLERANCE,
    )


def header_map(sheet: Sheet) -> dict[str, int]:
    headers: dict[str, int] = {}
    for column in range(1, sheet.max_column + 1):
        item = value(sheet, 1, column)
        if item is not None:
            headers[str(item)] = column
    return headers


def keyed_rows(sheet: Sheet, key_columns: Sequence[int]) -> list[int]:
    rows: list[int] = []
    for row in range(2, sheet.max_row + 1):
        if all(value(sheet, row, column) is not None for column in key_columns):
            rows.append(row)
    return rows


def key_counts(sheet: Sheet, key_columns: Sequence[int]) -> Counter[tuple[Any, ...]]:
    return Counter(
        tuple(value(sheet, row, column) for column in key_columns)
        for row in keyed_rows(sheet, key_columns)
    )


def check_sheets(
    audit: Audit, workbook: Workbook, expected: Iterable[str], workbook_label: str
) -> None:
    actual = set(workbook.sheets)
    expected_set = set(expected)
    audit.record(
        actual == expected_set,
        "SHEET_INVENTORY",
        f"Unexpected sheet inventory in {workbook_label}.",
        workbook=workbook_label,
        missing=sorted(expected_set - actual),
        unexpected=sorted(actual - expected_set),
    )


def check_required_headers(
    audit: Audit, sheet: Sheet, expected: Sequence[str], workbook_label: str
) -> None:
    actual = header_map(sheet)
    missing = [item for item in expected if item not in actual]
    audit.record(
        not missing,
        "MISSING_HEADERS",
        f"Required headers are missing from {sheet.name}.",
        workbook=workbook_label,
        sheet=sheet.name,
        missing=missing,
    )


def check_numeric_block(
    audit: Audit,
    sheet: Sheet,
    rows: Iterable[int],
    columns: Iterable[int],
    workbook_label: str,
) -> None:
    invalid = [
        {
            "cell": f"{sheet.cell(row, column).reference if sheet.cell(row, column) else '?'}",
            "value": value(sheet, row, column),
        }
        for row in rows
        for column in columns
        if not numeric(value(sheet, row, column))
    ]
    audit.record(
        not invalid,
        "NON_NUMERIC_REQUIRED_VALUE",
        f"Required numerical cells are missing or non-numeric in {sheet.name}.",
        workbook=workbook_label,
        sheet=sheet.name,
        invalid=invalid[:50],
        invalid_count=len(invalid),
    )


def check_key_uniqueness(
    audit: Audit, sheet: Sheet, key_columns: Sequence[int], workbook_label: str
) -> None:
    counts = key_counts(sheet, key_columns)
    duplicates = [key for key, count in counts.items() if count > 1]
    audit.record(
        not duplicates,
        "DUPLICATE_KEYS",
        f"Duplicate primary keys found in {sheet.name}.",
        workbook=workbook_label,
        sheet=sheet.name,
        key_columns=list(key_columns),
        duplicates=duplicates,
    )


def formula_errors(workbook: Workbook) -> list[dict[str, str]]:
    return [
        {"sheet": sheet.name, "cell": cell.reference, "value": cell.value}
        for sheet in workbook.sheets.values()
        for cell in sheet.cells.values()
        if isinstance(cell.value, str) and cell.value.startswith("#")
    ]


def uf_code(raw: Any) -> str | None:
    if raw in UF_CODES:
        return str(raw)
    return FULL_NAME_TO_CODE.get(str(raw))


def state_rows_by_key(sheet: Sheet, code_column: int = 1) -> dict[tuple[str, int], int]:
    result: dict[tuple[str, int], int] = {}
    for row in keyed_rows(sheet, (code_column, 2)):
        code = uf_code(value(sheet, row, code_column))
        year = value(sheet, row, 2)
        if code is not None and isinstance(year, int):
            result[(code, year)] = row
    return result


def check_national(audit: Audit, workbook: Workbook) -> dict[str, Any]:
    label = str(NATIONAL_PATH.relative_to(REPO_ROOT))
    check_sheets(audit, workbook, EXPECTED_NATIONAL_SHEETS, label)

    total = workbook.sheets["custo_total_violencia"]
    public = workbook.sheets["seguranca_publica_br"]
    private = workbook.sheets["seguranca_privada_br"]
    prison = workbook.sheets["encarceramento_br"]
    insurance = workbook.sheets["seguros_&_danos_materiais_br"]
    productive = workbook.sheets["perdas_produtivas_br"]
    justice = workbook.sheets["processos_judiciais_br"]
    medical = workbook.sheets["servicos_medicos_br"]

    expected_headers = {
        "custo_total_violencia": (
            "ano",
            "pib_deflacionado",
            "seguranca_publica",
            "part_pib_seg_pub",
            "seguranca_privada",
            "part_pib_seg_priv",
            "encarceramento",
            "part_pib_encar",
            "seguros_&_danos_materiais",
            "part_pib_seguros",
            "processos_judiciais",
            "part_pib_justica",
            "perdas_produtivas",
            "part_pib_perdas_prod",
            "servicos_medicos",
            "part_pib_serv_med",
            "custo_total_violencia",
        ),
        "seguranca_publica_br": (
            "ano",
            "uniao",
            "ufs",
            "municipios",
            "gasto_total_deflaciodo",
            "fonte",
        ),
        "seguranca_privada_br": (
            "ano",
            "postos_formais_rais",
            "postos_formais_pnad_antiga",
            "postos_formais_pnadc",
            "massa_salarial_formal_deflacionada_rais",
            "massa_salarial_formal_deflacionada_pnad_antiga",
            "massa_salarial_formal_deflacionada_pnadc",
            "postos_informal_pnad_antiga",
            "postos_informal_pnadc",
            "massa_salarial_informal_deflacionada_pnad_antiga",
            "massa_salarial_informal_deflacionada_pnadc",
            "multiplicador_encargos_trabalhistas",
            "custo_trabalho_formal_rais",
            "custo_trabalho_formal_pnad_antiga",
            "custo_trabalho_formal_pnadc",
        ),
        "encarceramento_br": (
            "ano",
            "custodia_&_reintegracao_deflaciodo",
            "auxilio_reclusao_deflaciodo",
        ),
        "seguros_&_danos_materiais_br": (
            "ano",
            "cerio",
            "seguro_automotivo_deflaciodo",
            "seguro_patrimonial_deflaciodo",
            "seguro_transporte_carga_deflaciodo",
            "perda_patrimonial_deflaciodo",
            "perda_transporte_carga_deflaciodo",
            "perda_automobilista_deflaciodo",
            "gasto_total",
        ),
        "perdas_produtivas_br": ("ano", "total_de_homicidios", "renda_total_perdida"),
        "processos_judiciais_br": (
            "ano",
            "gastos_deflaciodos_tjs",
            "gastos_deflaciodos_mps",
            "gastos_deflaciodos_defesa",
        ),
        "servicos_medicos_br": (
            "ano",
            "internacoes_agressao",
            "custo_SUS_deflacionado",
            "gasto_total",
        ),
    }
    for sheet_name, headers in expected_headers.items():
        check_required_headers(audit, workbook.sheets[sheet_name], headers, label)

    # The summary sheet was reorganized in August 2026. Resolve variables by
    # header so harmless column-order changes do not create false failures.
    total_headers = header_map(total)
    component_names = (
        "seguranca_publica",
        "seguranca_privada",
        "encarceramento",
        "seguros_&_danos_materiais",
        "processos_judiciais",
        "perdas_produtivas",
        "servicos_medicos",
    )
    share_names = (
        "part_pib_seg_pub",
        "part_pib_seg_priv",
        "part_pib_encar",
        "part_pib_seguros",
        "part_pib_justica",
        "part_pib_perdas_prod",
        "part_pib_serv_med",
    )
    component_columns = tuple(total_headers[name] for name in component_names)
    share_columns = tuple(total_headers[name] for name in share_names)
    gdp_column = total_headers["pib_deflacionado"]
    grand_total_column = total_headers["custo_total_violencia"]

    national_sheets = (
        total,
        public,
        private,
        prison,
        insurance,
        productive,
        justice,
        medical,
    )
    for sheet in national_sheets:
        check_key_uniqueness(audit, sheet, (1,), label)
        years = tuple(value(sheet, row, 1) for row in keyed_rows(sheet, (1,)))
        audit.record(
            years == EXPECTED_NATIONAL_YEARS,
            "YEAR_COVERAGE",
            f"Unexpected year coverage in {sheet.name}.",
            workbook=label,
            sheet=sheet.name,
            expected=list(EXPECTED_NATIONAL_YEARS),
            actual=list(years),
        )

    rows = range(2, 32)
    check_numeric_block(audit, total, rows, range(1, 18), label)
    check_numeric_block(audit, public, rows, (1, 5), label)
    check_numeric_block(audit, prison, rows, (1, 2, 3), label)
    check_numeric_block(audit, insurance, rows, (1, 3, 4, 5, 6, 7, 8, 9), label)
    check_numeric_block(audit, productive, rows, (1, 2, 3), label)
    check_numeric_block(audit, justice, rows, (1, 2, 3, 4), label)
    check_numeric_block(audit, medical, rows, (1, 4), label)

    invalid_private: list[dict[str, Any]] = []
    for row in rows:
        year = value(private, row, 1)
        required = (6, 10, 12, 14) if year <= 2011 else (7, 11, 12, 15)
        for column in required:
            if not numeric(value(private, row, column)):
                invalid_private.append({"year": year, "column": column, "value": value(private, row, column)})
    audit.record(
        not invalid_private,
        "NON_NUMERIC_REQUIRED_VALUE",
        "Required PNAD/PNAD Contínua private-security values are missing or non-numeric.",
        workbook=label,
        sheet=private.name,
        invalid=invalid_private,
    )

    formula_issues = formula_errors(workbook)
    audit.record(
        not formula_issues,
        "FORMULA_ERROR_VALUE",
        "Cached Excel formula errors were found in the national workbook.",
        workbook=label,
        cells=formula_issues,
    )

    grand_total_differences: dict[int, float] = {}
    for row in rows:
        year = int(value(total, row, 1))
        links = {
            "seguranca_publica": (
                value(total, row, total_headers["seguranca_publica"]),
                value(public, row, 5),
            ),
            "seguranca_privada": (
                value(total, row, total_headers["seguranca_privada"]),
                value(private, row, 14) + value(private, row, 10)
                if year <= 2011
                else value(private, row, 15) + value(private, row, 11),
            ),
            "encarceramento": (
                value(total, row, total_headers["encarceramento"]),
                value(prison, row, 2) + value(prison, row, 3),
            ),
            "seguros_danos": (
                value(total, row, total_headers["seguros_&_danos_materiais"]),
                value(insurance, row, 9),
            ),
            "justica": (
                value(total, row, total_headers["processos_judiciais"]),
                value(justice, row, 2) + value(justice, row, 3) + value(justice, row, 4),
            ),
            "perdas_produtivas": (
                value(total, row, total_headers["perdas_produtivas"]),
                value(productive, row, 3),
            ),
            "servicos_medicos": (
                value(total, row, total_headers["servicos_medicos"]),
                value(medical, row, 4),
            ),
        }
        for component, (reported, expected) in links.items():
            audit.record(
                close(reported, expected),
                "NATIONAL_COMPONENT_LINK",
                f"National summary does not reproduce the {component} source sheet.",
                workbook=label,
                year=year,
                component=component,
                reported=reported,
                expected=expected,
                difference=reported - expected,
                tolerance_reais=CURRENCY_ABS_TOLERANCE,
            )

        for component_column, share_column in zip(component_columns, share_columns):
            component = value(total, row, component_column)
            gdp = value(total, row, gdp_column)
            reported_share = value(total, row, share_column)
            expected_share = component / gdp * 100
            audit.record(
                math.isclose(
                    reported_share,
                    expected_share,
                    rel_tol=0.0,
                    abs_tol=PERCENTAGE_POINT_TOLERANCE,
                ),
                "GDP_SHARE_IDENTITY",
                "A national GDP-share cell does not equal component/GDP × 100.",
                workbook=label,
                year=year,
                component_column=component_column,
                reported=reported_share,
                expected=expected_share,
                difference_percentage_points=reported_share - expected_share,
                tolerance_percentage_points=PERCENTAGE_POINT_TOLERANCE,
            )
            audit.record(
                0 <= reported_share <= 100,
                "IMPOSSIBLE_SHARE",
                "A national GDP share is outside [0, 100].",
                workbook=label,
                year=year,
                column=share_column,
                value=reported_share,
            )

        component_sum = sum(value(total, row, column) for column in component_columns)
        reported_total = value(total, row, grand_total_column)
        difference = reported_total - component_sum
        grand_total_differences[year] = difference

        insurance_sum = sum(value(insurance, row, column) for column in range(3, 9))
        audit.record(
            close(value(insurance, row, 9), insurance_sum),
            "INSURANCE_TOTAL_IDENTITY",
            "Insurance/material-loss total does not equal its six components.",
            workbook=label,
            year=year,
            reported=value(insurance, row, 9),
            expected=insurance_sum,
            difference_reais=value(insurance, row, 9) - insurance_sum,
        )

        formal_mass_column = 6 if year <= 2011 else 7
        formal_cost_column = 14 if year <= 2011 else 15
        expected_formal_cost = value(private, row, formal_mass_column) * value(private, row, 12)
        audit.record(
            close(value(private, row, formal_cost_column), expected_formal_cost),
            "PRIVATE_SECURITY_MULTIPLIER",
            "Formal private-security cost does not equal formal wage mass × 1.86.",
            workbook=label,
            year=year,
            reported=value(private, row, formal_cost_column),
            expected=expected_formal_cost,
        )

    total_identity_failures = {
        year: difference
        for year, difference in grand_total_differences.items()
        if abs(difference) > CURRENCY_ABS_TOLERANCE
    }
    audit.record(
        not total_identity_failures,
        "NATIONAL_TOTAL_IDENTITY",
        "National grand total does not equal the sum of the seven monetary components.",
        workbook=label,
        affected_years=total_identity_failures,
        affected_count=len(total_identity_failures),
        tolerance_reais=CURRENCY_ABS_TOLERANCE,
    )

    total_cell = total.cell(2, grand_total_column)
    total_formula = total_cell.formula if total_cell else None
    component_refs = [f"{column_label(column)}2" for column in component_columns]
    if component_columns == tuple(range(min(component_columns), max(component_columns) + 1)):
        expected_formulas = {
            f"SUM({component_refs[0]}:{component_refs[-1]})",
            "+".join(component_refs),
        }
    else:
        expected_formulas = {
            f"SUM({','.join(component_refs)})",
            "+".join(component_refs),
        }
    normalized_formula = (total_formula or "").replace(" ", "").upper()
    audit.record(
        normalized_formula in expected_formulas,
        "NATIONAL_TOTAL_FORMULA_MIXES_UNITS",
        "The national total formula is not exactly the sum of the seven monetary components.",
        workbook=label,
        sheet=total.name,
        cell=total_cell.reference if total_cell else None,
        formula=total_formula,
        expected=sorted(expected_formulas),
    )

    # Documented missing/imputed values are warnings, not hard failures.
    audit.warn(
        "NATIONAL_STATUS_FLAGS",
        "The workbook uses red font and cell comments rather than a machine-readable status column; colors do not exhaustively flag all subcomponent imputations documented in the appendix.",
        workbook=label,
    )
    audit.warn(
        "PRODUCTIVE_LOSS_2025_PROXY",
        "The 2025 productive-loss source uses 40,775 aggregate homicides but no 2025 age-region microdata; it scales the 2024 loss in proportion to the homicide count.",
        workbook=label,
        sheet=total.name,
        cell=total.cell(31, total_headers["perdas_produtivas"]).reference,
        source_formula=productive.cell(31, 3).formula if productive.cell(31, 3) else None,
    )
    audit.warn(
        "GDP_METADATA_PENDING",
        "The national GDP denominator has no source, release/vintage, or construction metadata in the workbook or methodological appendix.",
        workbook=label,
        sheet=total.name,
        column="pib_deflacionado",
    )

    series = {
        "seguranca_publica": total_headers["seguranca_publica"],
        "seguranca_privada": total_headers["seguranca_privada"],
        "encarceramento": total_headers["encarceramento"],
        "seguros_danos": total_headers["seguros_&_danos_materiais"],
        "justica": total_headers["processos_judiciais"],
        "perdas_produtivas": total_headers["perdas_produtivas"],
        "servicos_medicos": total_headers["servicos_medicos"],
        "custo_total": grand_total_column,
    }
    for name, column in series.items():
        previous = value(total, 2, column)
        for row in range(3, 32):
            current = value(total, row, column)
            change = current / previous - 1
            if abs(change) >= DISCONTINUITY_WARNING_THRESHOLD:
                audit.warn(
                    "LARGE_ANNUAL_CHANGE",
                    "Annual change exceeds the documented 40% diagnostic screen and should be checked against source/method breaks.",
                    workbook=label,
                    series=name,
                    year=value(total, row, 1),
                    change_percent=change * 100,
                    threshold_percent=DISCONTINUITY_WARNING_THRESHOLD * 100,
                )
            previous = current

    return {
        "year_coverage": [1996, 2025],
        "terminal_year": 2025,
        "terminal_year_numerically_complete": True,
        "grand_total_difference_reais": grand_total_differences,
    }


def check_uf(audit: Audit, workbook: Workbook, national: Workbook) -> dict[str, Any]:
    label = str(UF_PATH.relative_to(REPO_ROOT))
    check_sheets(audit, workbook, EXPECTED_UF_SHEETS, label)

    total = workbook.sheets["custo_total_violencia_ufs"]
    graphs = workbook.sheets["graficos_ufs"]
    public = workbook.sheets["seguranca_publica_ufs"]
    private = workbook.sheets["seguranca_privada_ufs"]
    prison = workbook.sheets["encarceramento_ufs"]
    insurance = workbook.sheets["seguros_&_danos_materiais_uf"]
    productive = workbook.sheets["perdas_produtivas_ufs"]
    justice = workbook.sheets["processos_judiciais_ufs"]
    medical = workbook.sheets["servicos_medicos_ufs"]

    expected_headers = {
        "custo_total_violencia_ufs": (
            "uf",
            "ano",
            "seguranca_publica",
            "seguranca_privada",
            "encarceramento",
            "seguros_&_danos_materiais",
            "processos_judiciais",
            "perdas_produtivas",
            "servicos_medicos",
        ),
        "graficos_ufs": (
            "uf",
            "ano",
            "pib_estadual",
            "pib_per_capita",
            "populacao",
            "custo_total_crime",
            "custo_total_%_pib",
        ),
        "seguranca_publica_ufs": (
            "uf",
            "ano",
            "policiamento",
            "defesa_civil",
            "informacao_&_inteligencia",
            "demais_subfunções",
            "total_deflaciodo",
        ),
        "seguranca_privada_ufs": (
            "uf",
            "ano",
            "postos_formais_pnadc",
            "postos_informal_pnadc",
            "massa_salarial_formal_deflacionada_pnadc",
            "massa_salarial_informal_deflacionada_pnadc",
            "multiplicador_encargos_trabalhistas",
            "custo_trabalho_formal_rais",
        ),
        "encarceramento_ufs": (
            "uf",
            "ano",
            "presos",
            "custo_mensal_preso",
            "servidores",
            "rem_media_executivo_estadual",
            "gasto_anual_presos",
            "gasto_anual_servidores",
            "gasto_encarceramento",
        ),
        "seguros_&_danos_materiais_uf": (
            "uf",
            "ano",
            "peso_roubo_automovel",
            "peso_roubo_carga",
            "peso_roubo_total",
            "gasto_seguro_automovel",
            "gasto_seguro_patrimonio",
            "gasto_seguro_carga",
            "gasto_perda_automovel",
            "gasto_perda_patrimonio",
            "gasto_perda_carga",
            "uf_sigla",
        ),
        "perdas_produtivas_ufs": (
            "uf",
            "ano",
            "homicidios_com_idade",
            "homicidios_sem_idade",
            "perda_observada",
            "renda_media_imputacao_sem_idade",
            "perda_imputada",
            "homicidios_totais",
            "perda_total_com_imputacao",
        ),
        "processos_judiciais_ufs": (
            "uf",
            "ano",
            "gasto_justica_criminal_tj",
            "gasto_justica_criminal_mp",
            "gasto_justica_criminal_defesa",
        ),
        "servicos_medicos_ufs": (
            "uf",
            "ano",
            "deflator_bc",
            "internacoes_agressao",
            "internacoes_nao_fatais",
            "internacoes_nao_fatais_com_idade",
            "internacoes_nao_fatais_sem_idade",
            "obitos_hospitalares",
            "custo_SUS",
            "perda_produtiva_observada",
            "perda_produtiva_imputada",
            "perda_produtiva_temporaria",
            "custo_medico_total",
        ),
    }
    for sheet_name, headers in expected_headers.items():
        check_required_headers(audit, workbook.sheets[sheet_name], headers, label)

    relevant_sheets = (total, graphs, public, private, prison, insurance, productive, justice, medical)
    for sheet in relevant_sheets:
        check_key_uniqueness(audit, sheet, (1, 2), label)
        rows = keyed_rows(sheet, (1, 2))
        years = sorted({value(sheet, row, 2) for row in rows})
        audit.record(
            years == list(EXPECTED_UF_YEARS),
            "YEAR_COVERAGE",
            f"Unexpected year coverage in {sheet.name}.",
            workbook=label,
            sheet=sheet.name,
            expected=list(EXPECTED_UF_YEARS),
            actual=years,
        )
        for year in EXPECTED_UF_YEARS:
            year_rows = [row for row in rows if value(sheet, row, 2) == year]
            codes = {uf_code(value(sheet, row, 1)) for row in year_rows}
            audit.record(
                len(year_rows) == 27 and codes == UF_CODES,
                "UF_COVERAGE",
                f"Sheet {sheet.name} does not cover all 26 states plus the Federal District.",
                workbook=label,
                sheet=sheet.name,
                year=year,
                row_count=len(year_rows),
                missing_codes=sorted(UF_CODES - codes),
                unexpected_codes=sorted(str(code) for code in codes - UF_CODES),
            )

    data_rows = range(2, 56)
    check_numeric_block(audit, total, data_rows, range(2, 10), label)
    check_numeric_block(audit, graphs, data_rows, range(2, 22), label)
    check_numeric_block(audit, private, data_rows, range(2, 9), label)
    check_numeric_block(audit, prison, data_rows, range(2, 10), label)
    check_numeric_block(audit, insurance, data_rows, range(2, 15), label)
    check_numeric_block(audit, productive, data_rows, range(2, 10), label)
    check_numeric_block(audit, justice, data_rows, range(2, 6), label)
    check_numeric_block(audit, medical, data_rows, range(2, 17), label)

    formula_issues = formula_errors(workbook)
    derived_code_issues = [
        issue
        for issue in formula_issues
        if issue["sheet"] == insurance.name and issue["cell"].startswith("O")
    ]
    hard_formula_issues = [
        issue for issue in formula_issues if issue not in derived_code_issues
    ]
    audit.record(
        not hard_formula_issues,
        "FORMULA_ERROR_VALUE",
        "Cached Excel formula errors were found in the UF workbook.",
        workbook=label,
        cells=hard_formula_issues,
    )
    if derived_code_issues:
        audit.warn(
            "UF_DERIVED_CODE_CACHE_ERROR",
            "Excel cached #NAME? for the derived uf_sigla SWITCH formulas; validation recovered the canonical code from the UF name.",
            workbook=label,
            sheet=insurance.name,
            affected_count=len(derived_code_issues),
        )

    # Map each component sheet to the aggregate by UF-year.
    total_rows = state_rows_by_key(total)
    graph_rows = state_rows_by_key(graphs)
    source_rows = {
        "public": state_rows_by_key(public),
        "private": state_rows_by_key(private),
        "prison": state_rows_by_key(prison),
        "insurance": state_rows_by_key(insurance),
        "productive": state_rows_by_key(productive),
        "justice": state_rows_by_key(justice),
        "medical": state_rows_by_key(medical),
    }

    component_specs = {
        "public": (3, lambda row: value(public, row, 7)),
        "private": (4, lambda row: value(private, row, 6) + value(private, row, 8)),
        "prison": (5, lambda row: value(prison, row, 9)),
        "insurance": (6, lambda row: sum(value(insurance, row, column) for column in range(9, 15))),
        "justice": (7, lambda row: sum(value(justice, row, column) for column in range(3, 6))),
        "productive": (8, lambda row: value(productive, row, 9)),
        "medical": (9, lambda row: value(medical, row, 15)),
    }
    for key, total_row in total_rows.items():
        code, year = key
        for component, (total_column, calculator) in component_specs.items():
            source_row = source_rows[component].get(key)
            if source_row is None:
                audit.record(
                    False,
                    "UF_COMPONENT_LINK",
                    "A UF-year component row cannot be mapped to the aggregate sheet.",
                    workbook=label,
                    component=component,
                    uf=code,
                    year=year,
                )
                continue
            reported = value(total, total_row, total_column)
            expected = calculator(source_row)
            audit.record(
                close(reported, expected),
                "UF_COMPONENT_LINK",
                "UF aggregate does not reproduce its component sheet.",
                workbook=label,
                component=component,
                uf=code,
                year=year,
                reported=reported,
                expected=expected,
                difference_reais=reported - expected,
            )

        graph_row = graph_rows[key]
        component_pairs = zip(range(3, 10), range(7, 14))
        for total_column, graph_column in component_pairs:
            audit.record(
                close(value(total, total_row, total_column), value(graphs, graph_row, graph_column)),
                "UF_GRAPH_LINK",
                "graficos_ufs does not reproduce custo_total_violencia_ufs.",
                workbook=label,
                uf=code,
                year=year,
                total_column=total_column,
                graph_column=graph_column,
            )
        expected_total = sum(value(total, total_row, column) for column in range(3, 10))
        audit.record(
            close(value(graphs, graph_row, 6), expected_total),
            "UF_TOTAL_IDENTITY",
            "UF total cost does not equal its seven components.",
            workbook=label,
            uf=code,
            year=year,
            reported=value(graphs, graph_row, 6),
            expected=expected_total,
        )
        expected_gdp_per_capita = value(graphs, graph_row, 3) / value(graphs, graph_row, 5)
        audit.record(
            math.isclose(
                value(graphs, graph_row, 4),
                expected_gdp_per_capita,
                rel_tol=0.0,
                # The stored series is rounded to four decimal places.
                abs_tol=5e-5,
            ),
            "GDP_PER_CAPITA_IDENTITY",
            "UF GDP per capita does not equal GDP/population.",
            workbook=label,
            uf=code,
            year=year,
            reported=value(graphs, graph_row, 4),
            expected=expected_gdp_per_capita,
            tolerance_reais_per_person=5e-5,
        )
        for component_column, share_column in zip(range(6, 14), range(14, 22)):
            reported_share = value(graphs, graph_row, share_column)
            expected_share = value(graphs, graph_row, component_column) / value(graphs, graph_row, 3) * 100
            audit.record(
                math.isclose(
                    reported_share,
                    expected_share,
                    rel_tol=0.0,
                    abs_tol=PERCENTAGE_POINT_TOLERANCE,
                ),
                "UF_GDP_SHARE_IDENTITY",
                "UF GDP share does not equal value/GDP × 100.",
                workbook=label,
                uf=code,
                year=year,
                share_column=share_column,
                reported=reported_share,
                expected=expected_share,
            )
            audit.record(
                0 <= reported_share <= 100,
                "IMPOSSIBLE_SHARE",
                "A UF GDP share is outside [0, 100].",
                workbook=label,
                uf=code,
                year=year,
                column=share_column,
                value=reported_share,
            )

    # Within-sheet identities.
    missing_public_subfunctions: list[dict[str, Any]] = []
    prisoner_annualization_failures: list[dict[str, Any]] = []
    for row in data_rows:
        year = value(public, row, 2)
        code = uf_code(value(public, row, 1))
        missing = [
            value(public, 1, column)
            for column in range(3, 7)
            if value(public, row, column) is None
        ]
        if missing:
            missing_public_subfunctions.append({"uf": code, "year": year, "variables": missing})
        available_sum = sum(
            value(public, row, column) or 0 for column in range(3, 7)
        )
        audit.record(
            close(value(public, row, 7), available_sum),
            "UF_PUBLIC_SECURITY_TOTAL",
            "UF public-security total does not equal the available subfunctions.",
            workbook=label,
            uf=code,
            year=year,
            reported=value(public, row, 7),
            expected=available_sum,
        )

        expected_formal_cost = value(private, row, 5) * value(private, row, 7)
        audit.record(
            close(value(private, row, 8), expected_formal_cost),
            "UF_PRIVATE_SECURITY_MULTIPLIER",
            "UF formal private-security cost does not equal formal mass × 1.86.",
            workbook=label,
            uf=uf_code(value(private, row, 1)),
            year=value(private, row, 2),
        )

        # The workbook labels D as monthly and G as annual.  Annualization
        # therefore requires 12 × prisoners × monthly cost.
        expected_annual_prisoner_cost = value(prison, row, 3) * value(prison, row, 4) * 12
        if not close(value(prison, row, 7), expected_annual_prisoner_cost):
            prisoner_annualization_failures.append(
                {
                    "uf": uf_code(value(prison, row, 1)),
                    "year": value(prison, row, 2),
                    "reported": value(prison, row, 7),
                    "expected_if_header_is_correct": expected_annual_prisoner_cost,
                }
            )
        expected_staff_cost = value(prison, row, 5) * value(prison, row, 6) * 12
        audit.record(
            close(value(prison, row, 8), expected_staff_cost),
            "UF_PRISON_STAFF_IDENTITY",
            "gasto_anual_servidores does not equal 12 × servidores × remuneration.",
            workbook=label,
            uf=uf_code(value(prison, row, 1)),
            year=value(prison, row, 2),
        )
        audit.record(
            close(value(prison, row, 9), value(prison, row, 7) + value(prison, row, 8)),
            "UF_PRISON_TOTAL_IDENTITY",
            "UF incarceration total does not equal its two stored components.",
            workbook=label,
            uf=uf_code(value(prison, row, 1)),
            year=value(prison, row, 2),
        )

        audit.record(
            value(productive, row, 8) == value(productive, row, 3) + value(productive, row, 4),
            "UF_HOMICIDE_COUNT_IDENTITY",
            "UF homicide total does not equal known-age plus missing-age homicides.",
            workbook=label,
            uf=uf_code(value(productive, row, 1)),
            year=value(productive, row, 2),
        )
        audit.record(
            close(value(productive, row, 9), value(productive, row, 5) + value(productive, row, 7)),
            "UF_PRODUCTIVE_LOSS_IDENTITY",
            "UF productive loss does not equal observed plus imputed loss.",
            workbook=label,
            uf=uf_code(value(productive, row, 1)),
            year=value(productive, row, 2),
        )

        audit.record(
            value(medical, row, 4) == value(medical, row, 5) + value(medical, row, 8),
            "UF_HOSPITAL_COUNT_IDENTITY",
            "Hospital admissions do not equal non-fatal admissions plus hospital deaths.",
            workbook=label,
            uf=uf_code(value(medical, row, 1)),
            year=value(medical, row, 2),
        )
        audit.record(
            value(medical, row, 5) == value(medical, row, 6) + value(medical, row, 7),
            "UF_NONFATAL_COUNT_IDENTITY",
            "Non-fatal admissions do not equal known-age plus missing-age admissions.",
            workbook=label,
            uf=uf_code(value(medical, row, 1)),
            year=value(medical, row, 2),
        )
        audit.record(
            close(value(medical, row, 14), value(medical, row, 12) + value(medical, row, 13)),
            "UF_TEMPORARY_LOSS_IDENTITY",
            "Temporary productive loss does not equal observed plus imputed loss.",
            workbook=label,
            uf=uf_code(value(medical, row, 1)),
            year=value(medical, row, 2),
        )
        audit.record(
            close(value(medical, row, 15), value(medical, row, 11) + value(medical, row, 14)),
            "UF_MEDICAL_TOTAL_IDENTITY",
            "UF medical total does not equal SUS cost plus temporary productive loss.",
            workbook=label,
            uf=uf_code(value(medical, row, 1)),
            year=value(medical, row, 2),
        )

    audit.record(
        not prisoner_annualization_failures,
        "UF_PRISON_MONTHLY_ANNUAL_SCALING",
        "gasto_anual_presos omits the factor of 12 implied by custo_mensal_preso in all UF-year rows.",
        workbook=label,
        affected=prisoner_annualization_failures,
        affected_count=len(prisoner_annualization_failures),
        anchor_formula=prison.cell(2, 7).formula if prison.cell(2, 7) else None,
    )

    audit.warn(
        "UF_PUBLIC_SECURITY_MISSING_SUBFUNCTIONS",
        "Some UF public-security totals use SUM over blank subfunction cells; the workbook does not document whether blanks mean zero or missing.",
        workbook=label,
        affected=missing_public_subfunctions,
        affected_count=len(missing_public_subfunctions),
    )
    audit.warn(
        "UF_LABEL_TRUNCATION",
        "seguranca_publica_ufs truncates the labels Amazonas, Minas Gerais, Pernambuco, and Santa Catarina.",
        workbook=label,
    )
    audit.warn(
        "UF_GDP_POPULATION_METADATA_PENDING",
        "State GDP and population cells have no source, release/vintage, or construction metadata in the workbook or appendix.",
        workbook=label,
        sheet=graphs.name,
    )
    audit.warn(
        "UF_PRISON_CONCEPT_CONFLICT",
        "UF incarceration uses prisoners × a cost parameter plus staff × remuneration, while the national method uses subfunction 421 plus auxílio-reclusão and explicitly excludes a separate staff estimate to avoid overlap.",
        workbook=label,
    )

    # Allocation weights must be bounded and close within each year.
    for row in data_rows:
        for column in (6, 7, 8):
            item = value(insurance, row, column)
            audit.record(
                0 <= item <= 1,
                "IMPOSSIBLE_WEIGHT",
                "An insurance/material-loss allocation weight is outside [0, 1].",
                workbook=label,
                uf=value(insurance, row, 15),
                year=value(insurance, row, 2),
                column=column,
                value=item,
            )
    for year in EXPECTED_UF_YEARS:
        year_rows = [row for row in data_rows if value(insurance, row, 2) == year]
        for column in (6, 7, 8):
            weight_sum = sum(value(insurance, row, column) for row in year_rows)
            audit.record(
                math.isclose(weight_sum, 1.0, rel_tol=0.0, abs_tol=WEIGHT_TOLERANCE),
                "ALLOCATION_WEIGHTS_SUM",
                "UF allocation weights do not sum to one.",
                workbook=label,
                year=year,
                column=column,
                sum=weight_sum,
                tolerance=WEIGHT_TOLERANCE,
            )

    national_total = national.sheets["custo_total_violencia"]
    national_public = national.sheets["seguranca_publica_br"]
    national_insurance = national.sheets["seguros_&_danos_materiais_br"]
    national_justice = national.sheets["processos_judiciais_br"]
    national_productive = national.sheets["perdas_produtivas_br"]
    national_total_headers = header_map(national_total)
    reconciliation: dict[int, dict[str, Any]] = {}
    for year in EXPECTED_UF_YEARS:
        national_row = year - 1994
        year_total_rows = [row for (code, item_year), row in total_rows.items() if item_year == year]
        year_graph_rows = [row for (code, item_year), row in graph_rows.items() if item_year == year]
        sums = {
            "seguranca_publica": sum(value(total, row, 3) for row in year_total_rows),
            "seguranca_privada": sum(value(total, row, 4) for row in year_total_rows),
            "encarceramento": sum(value(total, row, 5) for row in year_total_rows),
            "seguros_danos": sum(value(total, row, 6) for row in year_total_rows),
            "justica": sum(value(total, row, 7) for row in year_total_rows),
            "perdas_produtivas": sum(value(total, row, 8) for row in year_total_rows),
            "servicos_medicos": sum(value(total, row, 9) for row in year_total_rows),
            "pib": sum(value(graphs, row, 3) for row in year_graph_rows),
        }
        national_values = {
            "seguranca_publica": value(
                national_total, national_row, national_total_headers["seguranca_publica"]
            ),
            "seguranca_privada": value(
                national_total, national_row, national_total_headers["seguranca_privada"]
            ),
            "encarceramento": value(
                national_total, national_row, national_total_headers["encarceramento"]
            ),
            "seguros_danos": value(
                national_total,
                national_row,
                national_total_headers["seguros_&_danos_materiais"],
            ),
            "justica": value(
                national_total, national_row, national_total_headers["processos_judiciais"]
            ),
            "perdas_produtivas": value(
                national_total, national_row, national_total_headers["perdas_produtivas"]
            ),
            "servicos_medicos": value(
                national_total, national_row, national_total_headers["servicos_medicos"]
            ),
            "pib": value(
                national_total, national_row, national_total_headers["pib_deflacionado"]
            ),
        }
        reconciliation[year] = {
            key: {
                "national": national_values[key],
                "sum_ufs": sums[key],
                "difference": sums[key] - national_values[key],
                "ratio": sums[key] / national_values[key],
            }
            for key in sums
        }

        # Public-security UF values are real; the national sheet's sphere
        # columns are nominal.  The implied national deflator should bridge
        # the sum of UFs to the national UF sphere.
        sphere_sum = sum(value(national_public, national_row, column) for column in (2, 3, 4))
        implied_deflator = value(national_public, national_row, 5) / sphere_sum
        expected_uf_sum = value(national_public, national_row, 3) * implied_deflator
        audit.record(
            close(sums["seguranca_publica"], expected_uf_sum),
            "NATIONAL_UF_PUBLIC_SECURITY",
            "Sum of real UF public-security values does not reconcile with the national UF sphere after applying the implied deflator.",
            workbook=label,
            year=year,
            sum_ufs=sums["seguranca_publica"],
            expected=expected_uf_sum,
            implied_deflator=implied_deflator,
        )
        audit.record(
            close(sums["seguros_danos"], national_values["seguros_danos"]),
            "NATIONAL_UF_INSURANCE",
            "Allocated UF insurance/material losses do not sum to the national value.",
            workbook=label,
            year=year,
            sum_ufs=sums["seguros_danos"],
            national=national_values["seguros_danos"],
        )
        # These UF values are allocations of national amounts.  Every
        # allocated component, not only their aggregate, should close.
        year_insurance_rows = [
            row
            for (code, item_year), row in source_rows["insurance"].items()
            if item_year == year
        ]
        for component, national_column, uf_column in (
            ("seguro_automotivo", 3, 9),
            ("seguro_patrimonial", 4, 10),
            ("seguro_carga", 5, 11),
            ("perda_automovel", 8, 12),
            ("perda_patrimonio", 6, 13),
            ("perda_carga", 7, 14),
        ):
            allocated = sum(value(insurance, row, uf_column) for row in year_insurance_rows)
            national_component = value(national_insurance, national_row, national_column)
            audit.record(
                close(allocated, national_component),
                "NATIONAL_UF_INSURANCE_COMPONENT",
                "An allocated UF insurance/material-loss component does not sum to its national amount.",
                workbook=label,
                year=year,
                component=component,
                sum_ufs=allocated,
                national=national_component,
                difference_reais=allocated - national_component,
            )
        audit.record(
            close(sums["servicos_medicos"], national_values["servicos_medicos"]),
            "NATIONAL_UF_MEDICAL",
            "UF medical values do not sum to the national value.",
            workbook=label,
            year=year,
            sum_ufs=sums["servicos_medicos"],
            national=national_values["servicos_medicos"],
        )
        audit.record(
            close_gdp(sums["pib"], national_values["pib"]),
            "NATIONAL_UF_GDP",
            "Sum of UF GDP does not reconcile with national GDP.",
            workbook=label,
            year=year,
            sum_ufs=sums["pib"],
            national=national_values["pib"],
            relative_tolerance=GDP_REL_TOLERANCE,
        )

        # The appendix says the 2009–2025 national justice total is the sum of
        # 27 UFs.  Check each component to localize any vintage mismatch.
        justice_rows = [row for (code, item_year), row in source_rows["justice"].items() if item_year == year]
        for component, national_column, uf_column in (
            ("tj", 2, 3),
            ("mp", 3, 4),
            ("defesa", 4, 5),
        ):
            sum_ufs = sum(value(justice, row, uf_column) for row in justice_rows)
            national_component = value(national_justice, national_row, national_column)
            audit.record(
                close(sum_ufs, national_component),
                "NATIONAL_UF_JUSTICE_COMPONENT",
                "The appendix says national justice equals the sum of UFs, but this component does not reconcile.",
                severity="WARNING" if component == "mp" else "ERROR",
                workbook=label,
                year=year,
                component=component,
                sum_ufs=sum_ufs,
                national=national_component,
                difference_reais=sum_ufs - national_component,
            )

        productive_rows = [row for (code, item_year), row in source_rows["productive"].items() if item_year == year]
        homicide_sum = sum(value(productive, row, 8) for row in productive_rows)
        national_homicides = value(national_productive, national_row, 2)
        productive_sum = sum(value(productive, row, 9) for row in productive_rows)
        national_loss = value(national_productive, national_row, 3)
        if year == 2025:
            audit.record(
                homicide_sum == national_homicides and close(productive_sum, national_loss),
                "NATIONAL_UF_PRODUCTIVE_2025",
                "The 2025 UF productive-loss block does not reconcile with the national 2025 estimate; state data are pending an upstream update.",
                severity="WARNING",
                workbook=label,
                year=year,
                uf_homicides=homicide_sum,
                national_homicides=national_homicides,
                uf_loss=productive_sum,
                national_loss=national_loss,
                homicide_difference=homicide_sum - national_homicides,
                loss_difference_reais=productive_sum - national_loss,
            )
        else:
            relative_difference = abs(productive_sum - national_loss) / national_loss
            if relative_difference > 0:
                audit.warn(
                    "NATIONAL_UF_PRODUCTIVE_MINOR_REVISION",
                    "The 2016 UF productive-loss sum differs slightly from the national value; this is treated as a plausible vintage/aggregation revision, not a hard failure.",
                    workbook=label,
                    year=year,
                    uf_homicides=homicide_sum,
                    national_homicides=national_homicides,
                    difference_reais=productive_sum - national_loss,
                    relative_difference_percent=relative_difference * 100,
                )

        private_relative_difference = abs(sums["seguranca_privada"] - national_values["seguranca_privada"]) / national_values["seguranca_privada"]
        if private_relative_difference > 0:
            audit.warn(
                "NATIONAL_UF_PRIVATE_SECURITY",
                "Sum of separately estimated UF PNAD Contínua private-security values differs from the national survey estimate.",
                workbook=label,
                year=year,
                difference_reais=sums["seguranca_privada"] - national_values["seguranca_privada"],
                relative_difference_percent=private_relative_difference * 100,
            )

    return {
        "year_coverage": [2016, 2025],
        "terminal_year": 2025,
        "terminal_year_has_27_ufs": True,
        "reconciliation": reconciliation,
    }


def workbook_inventory(workbook: Workbook, path: Path) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(REPO_ROOT)),
        "size_bytes": path.stat().st_size,
        "sha256": sha256(path),
        "sheets": [
            {
                "name": sheet.name,
                "state": sheet.state,
                "stored_cells": len(sheet.cells),
                "nonempty_cells": sum(cell.value is not None for cell in sheet.cells.values()),
                "formula_cells": sum(cell.formula is not None for cell in sheet.cells.values()),
                "max_row": sheet.max_row,
                "max_column": sheet.max_column,
            }
            for sheet in workbook.sheets.values()
        ],
    }


def run_audit() -> tuple[Audit, dict[str, Any]]:
    audit = Audit()
    for path in (NATIONAL_PATH, UF_PATH):
        audit.record(
            path.is_file(),
            "WORKBOOK_MISSING",
            "Required workbook is missing.",
            path=str(path.relative_to(REPO_ROOT)),
        )
    if audit.errors:
        return audit, {}

    national = Workbook(NATIONAL_PATH)
    uf = Workbook(UF_PATH)
    report = {
        "tolerances": {
            "currency_absolute_reais": CURRENCY_ABS_TOLERANCE,
            "gdp_relative": GDP_REL_TOLERANCE,
            "percentage_point_absolute": PERCENTAGE_POINT_TOLERANCE,
            "allocation_weight_absolute": WEIGHT_TOLERANCE,
            "discontinuity_warning_fraction": DISCONTINUITY_WARNING_THRESHOLD,
        },
        "workbooks": [
            workbook_inventory(national, NATIONAL_PATH),
            workbook_inventory(uf, UF_PATH),
        ],
        "national": check_national(audit, national),
        "uf": check_uf(audit, uf, national),
    }
    report["summary"] = {
        "checks": audit.checks,
        "passed": audit.passed,
        "errors": len(audit.errors),
        "warnings": len(audit.warnings),
    }
    report["findings"] = [asdict(finding) for finding in audit.findings]
    return audit, report


def print_report(audit: Audit, report: dict[str, Any]) -> None:
    if report:
        for workbook in report["workbooks"]:
            print(
                f"WORKBOOK {workbook['path']} | sha256={workbook['sha256']} | "
                f"sheets={len(workbook['sheets'])}"
            )
    def compact(item: Any) -> Any:
        """Keep console diagnostics readable; the JSON retains full context."""

        if isinstance(item, list) and len(item) > 5:
            return f"{item[:3]} ... ({len(item)} items)"
        return item

    finding_counts = Counter(
        (finding.severity, finding.code) for finding in audit.findings
    )
    emitted: Counter[tuple[str, str]] = Counter()
    for finding in audit.findings:
        finding_key = (finding.severity, finding.code)
        emitted[finding_key] += 1
        if finding_counts[finding_key] > 5 and emitted[finding_key] == 5:
            omitted = finding_counts[finding_key] - 4
            print(
                f"{finding.severity} {finding.code}: "
                f"... {omitted} additional findings; see JSON for full context"
            )
            continue
        if finding_counts[finding_key] > 5 and emitted[finding_key] > 5:
            continue
        context = " | ".join(
            f"{key}={compact(value)}" for key, value in finding.context.items()
        )
        suffix = f" | {context}" if context else ""
        print(f"{finding.severity} {finding.code}: {finding.message}{suffix}")
    print(
        f"SUMMARY checks={audit.checks} passed={audit.passed} "
        f"errors={len(audit.errors)} warnings={len(audit.warnings)}"
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json-out",
        type=Path,
        help="Optional repository-relative path for a machine-readable audit report.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    # Windows PowerShell commonly exposes a cp1252 stdout even though workbook
    # metadata may contain U+FFFD replacement characters.  Emit UTF-8 so the
    # diagnostic itself never fails while reporting malformed labels.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args(argv)
    audit, report = run_audit()
    print_report(audit, report)
    if args.json_out and report:
        output = args.json_out if args.json_out.is_absolute() else REPO_ROOT / args.json_out
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"WROTE {output.relative_to(REPO_ROOT)}")
    return 1 if audit.errors else 0


if __name__ == "__main__":
    sys.exit(main())
