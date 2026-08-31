"""Validate the complete first draft and write its headline-statistics ledger.

The quantitative universe is inherited from the figure-ready-data ledger used for
Sections 3--5.  This validator checks that every decimal rendering in the full
report is reproducible, that the report structure and figure references are
complete, and that drafting artifacts and raw variable names are absent.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from src.validation.validate_report_sections_3_5 import _pt, build_ledger, validate_draft


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs" / "report.md"
HEADLINE_OUT = ROOT / "data" / "audit" / "report_headline_statistics.csv"
CITATION_AUDIT_OUT = ROOT / "data" / "audit" / "report_citation_audit.csv"

HEADLINE_CLAIMS = [
    "Brazil homicide rate, 2016",
    "Brazil percentile, 2016",
    "Brazil homicide rate, 2024",
    "Brazil percentile, 2024",
    "Homicídio doloso rate, 2016",
    "Homicídio doloso rate, 2025",
    "Microrregions with declining endpoint rate",
    "Total measured cost, 1996",
    "Total measured cost GDP share, 1996",
    "Total measured cost, 2025",
    "Total measured cost GDP share, 2025",
    "2025 total composition: Segurança pública",
    "2025 total composition: Seguros e perdas materiais",
    "State burden median, 2025",
    "State trajectories: income_up_burden_down",
]

EXPECTED_SECTIONS = [
    "1. Sumário executivo",
    "2. Introdução",
    "3. Homicídios e criminalidade no Brasil",
    "4. Estimando os custos econômicos da criminalidade no Brasil",
    "5. Heterogeneidade regional dos custos da criminalidade",
    "6. Conclusão",
]

EXPECTED_FIGURES = ["01", "02A", "02B", "02C", "02D"] + [f"{number:02d}" for number in range(3, 16)]

CITATION_ITEMS = [
    {
        "report_scope": "Figura 1 e Seção 3.1",
        "institution_or_reference": "UNODC — Intentional Homicide",
        "repository_evidence": "data/raw/source_manifest.json; data/figure_data/fig_01_distribuicao_mundial_homicidios.csv; src/figures/fig_01_world_homicides.py",
        "note": "Versão oficial de julho de 2026; taxas de 2016 e 2024; amostra comum sem interpolação.",
    },
    {
        "report_scope": "Figuras 2A–2D e Seção 3.2",
        "institution_or_reference": "Ministério da Justiça e Segurança Pública — Sinesp VDE; IBGE",
        "repository_evidence": "data/raw/source_manifest.json; data/figure_data/fig_02a_crimes_registrados.csv; src/figures/fig_02_crime_trends.py",
        "note": "Contagens administrativas e denominadores populacionais com amostras geográficas correspondentes.",
    },
    {
        "report_scope": "Figuras 3–5 e Seções 3.3–3.4",
        "institution_or_reference": "Ministério da Saúde — SIM; IBGE",
        "repository_evidence": "data/raw/source_manifest.json; data/figure_data/fig_03_microrregion_homicides.csv; data/figure_data/fig_04_microrregion_homicide_change.csv; data/figure_data/fig_05_microrregion_homicide_convergence.csv",
        "note": "Microdados finais de mortalidade, população oficial e geografia fixa de microrregiões de 2015.",
    },
    {
        "report_scope": "Figuras 6–13 e Seção 4",
        "institution_or_reference": "Planilha nacional final e apêndice metodológico",
        "repository_evidence": "data/output/tabela_final_cec_brasil.xlsx; docs/appendix.pdf; docs/DATA-DICTIONARY.md",
        "note": "Planilha validada como referência numérica; fontes e construções mapeadas por componente.",
    },
    {
        "report_scope": "Figuras 14–15 e Seção 5",
        "institution_or_reference": "Planilha estadual final e apêndice metodológico",
        "repository_evidence": "data/output/tabela_final_cec_ufs.xlsx; docs/appendix.pdf; docs/METHODOLOGY-DECISIONS.md",
        "note": "Resultados estaduais identificados como preliminares e sujeitos às revisões documentadas.",
    },
    {
        "report_scope": "Continuidade histórica e enquadramento",
        "institution_or_reference": "Custos Econômicos da Criminalidade no Brasil (2018)",
        "repository_evidence": "docs/bib/original-report.pdf; docs/REFERENCE-FILES.md",
        "note": "Referência conceitual e histórica, não alvo de reprodução numérica.",
    },
]


def write_headlines(claims: list[dict[str, object]]) -> None:
    by_claim = {str(row["claim"]): row for row in claims}
    missing = [claim for claim in HEADLINE_CLAIMS if claim not in by_claim]
    if missing:
        raise AssertionError(f"Headline claims missing from quantitative ledger: {missing}")
    HEADLINE_OUT.parent.mkdir(parents=True, exist_ok=True)
    with HEADLINE_OUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["section", "claim", "value", "display", "source", "calculation"],
        )
        writer.writeheader()
        writer.writerows(by_claim[claim] for claim in HEADLINE_CLAIMS)


def validate_and_write_citations(text: str) -> None:
    rows: list[dict[str, str]] = []
    for item in CITATION_ITEMS:
        paths = [ROOT / value.strip() for value in item["repository_evidence"].split(";")]
        missing = [str(path) for path in paths if not path.exists() or path.stat().st_size == 0]
        if missing:
            raise AssertionError(f"Missing citation evidence for {item['report_scope']}: {missing}")
        rows.append({**item, "status": "VERIFIED"})

    manifest = json.loads((ROOT / "data" / "raw" / "source_manifest.json").read_text(encoding="utf-8"))
    source_ids = set(manifest["sources"])
    required_source_ids = {
        "unodc_intentional_homicide_2026_07",
        "unodc_intentional_homicide_metadata_2026_07",
        "ibge_population_projection_2024_uf_age_sex",
    }
    required_source_ids.update(f"sinesp_vde_{year}" for year in range(2015, 2026))
    absent_ids = sorted(required_source_ids - source_ids)
    if absent_ids:
        raise AssertionError(f"Required report sources are absent from the raw manifest: {absent_ids}")

    required_institutions = ["UNODC", "Sinesp", "SIM", "IBGE", "STN", "Susep", "SUS"]
    absent_institutions = [name for name in required_institutions if name not in text]
    if absent_institutions:
        raise AssertionError(f"Institutional attributions missing from report: {absent_institutions}")
    text_without_markdown_links = re.sub(r"\]\(https?://[^)]+\)", "]()", text)
    if re.search(r"https?://|\[citation needed\]|\(fonte\?\)", text_without_markdown_links, flags=re.IGNORECASE):
        raise AssertionError("Unresolved or direct-URL citation artifact remains in report prose")

    CITATION_AUDIT_OUT.parent.mkdir(parents=True, exist_ok=True)
    with CITATION_AUDIT_OUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["report_scope", "institution_or_reference", "repository_evidence", "status", "note"],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"PASS: {len(rows)} source groups verified and written to {CITATION_AUDIT_OUT}")


def validate_full_report(claims: list[dict[str, object]]) -> None:
    text = REPORT.read_text(encoding="utf-8")

    sections = re.findall(r"^## (.+)$", text, flags=re.MULTILINE)
    if sections != EXPECTED_SECTIONS:
        raise AssertionError(f"Unexpected report sections or ordering: {sections}")

    artifacts = re.findall(
        r"\b(?:TODO|TBD|PENDING|XXX)\b|\{xx+\}|\bxxxx\b|\[citation needed\]|\(fonte\?\)|<!--\s*Redigir",
        text,
        flags=re.IGNORECASE,
    )
    if artifacts:
        raise AssertionError(f"Drafting artifacts remain in report: {sorted(set(artifacts))}")

    raw_names = [
        "custodia_&_reintegracao",
        "pib_deflacionado",
        "part_pib_",
        "perda_capacidade_produtiva_deflacionada",
        "uf_sigla",
        "total_deflaciodo",
    ]
    exposed = [name for name in raw_names if name in text]
    if exposed:
        raise AssertionError(f"Raw data variable names exposed in prose: {exposed}")

    allowed: set[str] = {str(row["display"]).replace("-", "−") for row in claims}
    for row in claims:
        value = float(row["value"])
        for decimals in (1, 2, 3):
            allowed.add(_pt(value, decimals).replace("-", "−"))
            allowed.add(_pt(abs(value), decimals))
    allowed.add("1,86")  # documented private-security labor-cost multiplier
    decimal_tokens = set(re.findall(r"(?<![\w])−?\d+(?:\.\d{3})*,\d+(?!\w)", text))
    unexplained = sorted(decimal_tokens - allowed)
    if unexplained:
        raise AssertionError(f"Unreconciled decimal renderings in full report: {unexplained}")

    comments = re.findall(
        r"<!-- FIGURA\s+([0-9]{2}[A-D]?).*?:\s+(\.\./figs/[^ ]+\.pdf)\s+-->",
        text,
    )
    labels = [label for label, _ in comments]
    if labels != EXPECTED_FIGURES:
        raise AssertionError(f"Figure placeholders are incomplete or out of order: {labels}")
    for _, relative_path in comments:
        pdf_path = (REPORT.parent / relative_path).resolve()
        png_path = pdf_path.with_suffix(".png")
        for path in (pdf_path, png_path):
            if not path.exists() or path.stat().st_size == 0:
                raise AssertionError(f"Missing or empty figure output referenced by report: {path}")

    for number in range(1, 16):
        if not re.search(rf"\bFigura(?:s)?\s+{number}(?:\b|[A-D])", text):
            raise AssertionError(f"Figure {number} is not introduced or interpreted in prose")

    required_fragments = [
        "R$ 439,5 bilhões em 2025",
        "equivalentes a 3,5% do PIB",
        "percentil 86,0",
        "25,1 para 14,8 vítimas por 100 mil habitantes",
        "70,3% das microrregiões",
        "R$ 220,6 bilhões em 1996",
        "37,1% do total",
        "carga mediana foi 4,9% do PIB",
        "em 19, a carga do crime caiu, e em oito ela aumentou",
        "não uma estimativa causal do efeito do crime sobre o PIB",
    ]
    absent = [fragment for fragment in required_fragments if fragment not in text]
    if absent:
        raise AssertionError(f"Verified cross-section claims missing or inconsistent: {absent}")

    generic_fillers = [
        "é importante destacar",
        "vale ressaltar",
        "como podemos observar",
        "os dados mostram claramente",
    ]
    found_fillers = [phrase for phrase in generic_fillers if phrase in text.lower()]
    if found_fillers:
        raise AssertionError(f"Generic drafting prose remains: {found_fillers}")

    print(f"PASS: all {len(decimal_tokens)} distinct decimal renderings reconcile with figure-ready data")
    print(f"PASS: Sections 1--6 and {len(labels)} figure placeholders are complete and ordered")
    print("PASS: all Figures 1--15 are introduced in prose and have nonempty PDF/PNG outputs")
    print("PASS: no drafting artifacts, raw variable names, or banned filler phrases remain")
    validate_and_write_citations(text)


def main() -> int:
    claims, diagnostics = build_ledger()
    validate_draft(claims, diagnostics)
    write_headlines(claims)
    validate_full_report(claims)
    print(f"PASS: {len(HEADLINE_CLAIMS)} headline statistics written to {HEADLINE_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
