"""Render the complete English figure set from retained figure-ready CSVs.

The Portuguese production scripts remain the source of analytical definitions.
This module reuses their plotting functions and the exact retained rows, replacing
only publication-facing text and number formatting. It also writes parallel CSVs
whose categorical labels are translated while numeric fields remain unchanged.
"""

from __future__ import annotations

import csv
import importlib
import json
import textwrap
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.text import Text


ROOT = Path(__file__).resolve().parents[2]
FIGURE_DIR = ROOT / "figs"
DATA_DIR = ROOT / "data" / "figure_data"
EN_DATA_DIR = DATA_DIR / "en"
MANIFEST = EN_DATA_DIR / "english_figures_manifest.json"


COMPONENT_TRANSLATIONS = {
    "Serviços médico-terapêuticos": "Medical and therapeutic services",
    "Encarceramento e auxílio-reclusão": "Incarceration and incarceration benefit",
    "Custos judiciais": "Judicial costs",
    "Perda de capacidade produtiva": "Productive-capacity losses",
    "Seguros e perdas materiais": "Insurance and material losses",
    "Segurança privada": "Private security",
    "Segurança pública": "Public security",
    "Setor formal": "Formal sector",
    "Provisão informal": "Informal provision",
    "Custódia e reintegração social": "Custody and social reintegration",
    "Auxílio-reclusão (transferência)": "Incarceration benefit (transfer)",
    "Prêmios — automóveis": "Premiums — automobiles",
    "Prêmios — patrimônio": "Premiums — property",
    "Prêmios — transporte e carga": "Premiums — transport and cargo",
    "Perdas — veículos": "Losses — vehicles",
    "Perdas — patrimônio": "Losses — property",
    "Perdas — transporte e carga": "Losses — transport and cargo",
    "Tribunais de Justiça": "State courts",
    "Ministérios Públicos": "Public prosecutors",
    "Serviços de defesa criminal": "Criminal-defense services",
    "União": "Federal government",
    "Estados e Distrito Federal": "States and Federal District",
    "Municípios": "Municipalities",
    "Total sem decomposição": "Total without decomposition",
    "Total": "Total",
}

CRIME_TRANSLATIONS = {
    "Homicídio doloso": "Intentional homicide",
    "Latrocínio": "Robbery followed by death",
    "Tentativa de homicídio": "Attempted homicide",
    "Estupro": "Rape",
    "Estupro de vulnerável": "Rape of a vulnerable person",
    "Feminicídio": "Femicide",
    "Furto de veículo": "Vehicle theft",
    "Roubo de veículo": "Vehicle robbery",
    "Roubo de carga": "Cargo robbery",
    "Roubo a instituição financeira": "Robbery of financial institutions",
}

VALUE_TRANSLATIONS = {
    **COMPONENT_TRANSLATIONS,
    **CRIME_TRANSLATIONS,
    "vítimas": "victims",
    "vítimas por 100 mil habitantes": "victims per 100,000 inhabitants",
    "ocorrências": "incidents",
    "ocorrências por 100 mil habitantes": "incidents per 100,000 inhabitants",
    "Gasto público": "Public expenditure",
    "Custo do trabalho": "Labor cost",
    "Transferência previdenciária": "Social-security transfer",
    "Prêmio de seguro": "Insurance premium",
    "Perda material estimada": "Estimated material loss",
    "Perda modelada de renda esperada": "Modeled expected-income loss",
    "Despesa pública atribuída": "Attributed public expenditure",
    "Serviço jurídico valorado": "Valued legal service",
    "Gasto hospitalar + perda temporária modelada": "Hospital expenditure + modeled temporary loss",
    "Gasto público + transferência previdenciária": "Public expenditure + social-security transfer",
    "início": "start",
    "fim": "end",
    "Norte": "North",
    "Nordeste": "Northeast",
    "Centro-Oeste": "Center-West",
    "Sudeste": "Southeast",
    "Sul": "South",
    "Preliminar: perdas produtivas UF e conceito de encarceramento em revisão": (
        "Preliminary: state productive losses and the incarceration concept are under review"
    ),
}


PHRASE_TRANSLATIONS = {
    **COMPONENT_TRANSLATIONS,
    **CRIME_TRANSLATIONS,
    "Figura": "Figure",
    "Brasil: gastos com segurança pública": "Brazil: public-security expenditure",
    "Brasil: gastos com segurança privada": "Brazil: private-security expenditure",
    "Brasil: encarceramento e auxílio-reclusão": "Brazil: incarceration and the incarceration benefit",
    "Brasil: seguros e perdas materiais": "Brazil: insurance and material losses",
    "Brasil: perda de capacidade produtiva por homicídios": "Brazil: productive-capacity losses from homicide",
    "Brasil: custos judiciais associados à criminalidade": "Brazil: crime-related judicial costs",
    "Brasil: custos médico-terapêuticos da violência": "Brazil: medical and therapeutic costs of violence",
    "Brasil: custos econômicos medidos da criminalidade": "Brazil: measured economic costs of crime",
    "Mundo: distribuição das taxas de homicídio": "World: distribution of homicide rates",
    "Brasil: distribuição das taxas de homicídio por microrregião": "Brazil: distribution of homicide rates across microregions",
    "Brasil: mudança nas taxas de homicídio por microrregião": "Brazil: change in homicide rates across microregions",
    "Brasil: convergência das taxas de homicídio entre microrregiões": "Brazil: convergence in homicide rates across microregions",
    "UFs: nível e composição dos custos econômicos da criminalidade": "States: level and composition of the economic costs of crime",
    "UFs: trajetória da renda e do custo da criminalidade": "States: trajectory of income and the cost of crime",
    "Tendências da criminalidade — vítimas registradas": "Crime trends — recorded victims",
    "Tendências da criminalidade — taxas de vítimas registradas": "Crime trends — recorded victim rates",
    "Cobertura parcial: tendências de crimes patrimoniais registrados": "Partial coverage: recorded property-crime trends",
    "Cobertura parcial: taxas de crimes patrimoniais registrados": "Partial coverage: recorded property-crime rates",
    "A. Valores reais": "A. Real values",
    "B. Participação no PIB": "B. Share of GDP",
    "C. Percentual do total": "C. Share of total",
    "A. Renda estadual e peso dos custos medidos": "A. State income and measured cost burden",
    "B. Componentes do custo medido, ordenados pelo peso total": "B. Components of measured costs, ordered by total burden",
    "Percentual do total": "Share of total",
    "Percentual do PIB": "Share of GDP",
    "R$ bilhões de dez./2025": "R$ billions, Dec. 2025",
    "R$ mil de dez./2025": "R$ thousands, Dec. 2025",
    "Ano": "Year",
    "População": "Population",
    "População em 2016": "Population in 2016",
    "Taxa de homicídios em 2016 (por 100 mil habitantes)": "2016 homicide rate (per 100,000 inhabitants)",
    "Variação da taxa, 2016–2024 (por 100 mil habitantes)": "Change in rate, 2016–2024 (per 100,000 inhabitants)",
    "Homicídios por 100 mil habitantes": "Homicides per 100,000 inhabitants",
    "Homicídios intencionais por 100 mil habitantes": "Intentional homicides per 100,000 inhabitants",
    "Percentil entre países/territórios": "Percentile across countries/territories",
    "Percentil na distribuição das microrregiões": "Percentile in the microregion distribution",
    "Variação absoluta na taxa de homicídios por 100 mil habitantes": "Absolute change in homicides per 100,000 inhabitants",
    "Custos medidos (% do PIB estadual)": "Measured costs (% of state GDP)",
    "PIB per capita real": "Real GDP per capita",
    "Contribuição ao custo medido (percentual do PIB estadual)": "Contribution to measured cost (share of state GDP)",
    "Direção da trajetória": "Direction of trajectory",
    "Demais unidades": "Other reporting units",
    "Brasil": "Brazil",
    "percentil": "percentile",
    "Queda": "Decline",
    "Aumento": "Increase",
    "Ajuste ponderado": "Weighted fit",
    "Inclinação ponderada": "Weighted slope",
    "Correlação ponderada": "Weighted correlation",
    "RESULTADOS ESTADUAIS PRELIMINARES": "PRELIMINARY STATE RESULTS",
    "Decomposição por esfera disponível a partir de": "Government-level decomposition available from",
    "total em todo o período; percentuais por esfera desde": (
        "total for the entire period; government-level shares from"
    ),
    "100 mil": "100 thousand",
    "1 milhão": "1 million",
    "5 milhões": "5 million",
}


FIGURES: list[dict[str, Any]] = [
    {"module": "src.figures.fig_01_world_homicides", "csv": "fig_01_distribuicao_mundial_homicidios.csv", "stem": "fig_01_world_homicides_en"},
    {"module": "src.figures.fig_03_microrregion_homicides", "csv": "fig_03_microrregion_homicides.csv", "stem": "fig_03_microregion_homicides_en"},
    {"module": "src.figures.fig_04_microrregion_homicide_change", "csv": "fig_04_microrregion_homicide_change.csv", "stem": "fig_04_microregion_homicide_change_en"},
    {"module": "src.figures.fig_05_microrregion_homicide_convergence", "csv": "fig_05_microrregion_homicide_convergence.csv", "stem": "fig_05_microregion_homicide_convergence_en"},
    {"module": "src.figures.fig_06_public_security", "csv": "fig_06_public_security.csv", "stem": "fig_06_public_security_en"},
    {"module": "src.figures.fig_07_private_security", "csv": "fig_07_private_security.csv", "stem": "fig_07_private_security_en"},
    {"module": "src.figures.fig_08_incarceration", "csv": "fig_08_incarceration.csv", "stem": "fig_08_incarceration_en"},
    {"module": "src.figures.fig_09_insurance_material_losses", "csv": "fig_09_insurance_material_losses.csv", "stem": "fig_09_insurance_material_losses_en"},
    {"module": "src.figures.fig_10_productive_capacity", "csv": "fig_10_productive_capacity.csv", "stem": "fig_10_productive_capacity_en"},
    {"module": "src.figures.fig_11_judicial_costs", "csv": "fig_11_judicial_costs.csv", "stem": "fig_11_judicial_costs_en"},
    {"module": "src.figures.fig_12_medical_costs", "csv": "fig_12_medical_costs.csv", "stem": "fig_12_medical_costs_en"},
    {"module": "src.figures.fig_13_total_costs", "csv": "fig_13_total_costs.csv", "stem": "fig_13_total_costs_en"},
    {"module": "src.figures.fig_14_state_costs", "csv": "fig_14_state_costs.csv", "stem": "fig_14_state_costs_en"},
    {"module": "src.figures.fig_15_state_trajectories", "csv": "fig_15_state_trajectories.csv", "stem": "fig_15_state_trajectories_en"},
]

EN_OVERRIDES: dict[str, dict[str, Any]] = {
    "src.figures.fig_01_world_homicides": {
        "title": "Figure 1. World: distribution of homicide rates",
        "subtitle": "Rates in 2016 and 2024 by country/territory | unweighted distribution",
        "source_note": (
            "Source: Authors’ calculations using the UNODC Data Portal, Intentional Homicide "
            "(July 2026 release). Common sample of {sample_size} official country/territory reporting units "
            "observed in both years; rank percentiles without population weights. No interpolation or splicing "
            "with a Brazilian national source."
        ),
        "axis_labels": {"x": "Percentile across countries/territories", "y": "Intentional homicides per 100,000 inhabitants"},
    },
    "src.figures.fig_03_microrregion_homicides": {
        "title": "Figure 3. Brazil: distribution of homicide rates across microregions",
        "subtitle_template": "{year} | rate per 100,000 inhabitants; bubble area represents population",
        "source_note": (
            "Source: Authors’ calculations using final SIM/Ministry of Health and IBGE data. Homicides include "
            "ICD-10 underlying causes X85–X99, Y00–Y09, Y35, and Y36 and are assigned by residence. Fixed 2015 "
            "IBGE microregion geography; deaths without an identified municipality are excluded."
        ),
        "axis_labels": ("Percentile in the microregion distribution", "Homicides per 100,000 inhabitants"),
    },
    "src.figures.fig_04_microrregion_homicide_change": {
        "title": "Figure 4. Brazil: change in homicide rates across microregions",
        "subtitle_template": "Absolute change from {start} to {end}, per 100,000 inhabitants | fixed 2015 geography",
        "source_note_template": (
            "Source: Authors’ calculations using final SIM/Ministry of Health and IBGE data. Homicides include "
            "ICD-10 underlying causes X85–X99, Y00–Y09, Y35, and Y36 and are assigned by residence. The visual "
            "scale is centered on zero and capped at ±{limit:g}; the true values for {clipped} microregions beyond "
            "the limits remain in the CSV."
        ),
    },
    "src.figures.fig_05_microrregion_homicide_convergence": {
        "title": "Figure 5. Brazil: convergence in homicide rates across microregions",
        "subtitle": "Initial 2016 rate and absolute change through 2024 | bubble area proportional to 2016 population",
        "source_note": (
            "Source: Authors’ calculations using final SIM/Ministry of Health and IBGE data. Fixed 2015 geography. "
            "The dashed line is a population-weighted descriptive linear fit. The relationship is not causal and "
            "may incorporate mean reversion."
        ),
        "axis_labels": ("2016 homicide rate (per 100,000 inhabitants)", "Change in rate, 2016–2024 (per 100,000 inhabitants)"),
    },
    "src.figures.fig_06_public_security": {
        "title": "Figure 6. Brazil: public-security expenditure",
        "axis_labels": ("R$ billions, Dec. 2025", "Share of GDP", "Share of total"),
        "source_note_template": (
            "Source: Authors’ calculations using National Treasury and Brazilian Forum on Public Security data. "
            "Values in December 2025 reais, adjusted by the IPCA. Government-level decomposition is available "
            "from {decomposition_start}; the national total is shown before then without allocating components."
        ),
    },
    "src.figures.fig_07_private_security": {
        "title": "Figure 7. Brazil: private-security expenditure",
        "subtitle_template": "{start}–{end} | real values, share of GDP, and share of total",
        "source_note": (
            "Source: Authors’ calculations using annual PNAD and Continuous PNAD household microdata. Values in "
            "December 2025 reais. Formal labor income is multiplied by 1.86 to approximate total labor cost; "
            "informal provision uses the estimated earnings mass directly."
        ),
    },
    "src.figures.fig_08_incarceration": {
        "title": "Figure 8. Brazil: incarceration and the incarceration benefit",
        "subtitle_template": "{start}–{end} | real values, share of GDP, and share of total",
        "source_note": (
            "Source: Authors’ calculations using SIGA Brasil, National Treasury/Siconfi, Ministry of Social Security, "
            "SISDEPEN, and Ipea data. Values in December 2025 reais. The incarceration benefit is a social-security "
            "transfer and is not conceptually equivalent to prison operating expenditure."
        ),
    },
    "src.figures.fig_09_insurance_material_losses": {
        "title": "Figure 9. Brazil: insurance and material losses",
        "subtitle_template": "{start}–{end} | broad accounting scenario",
        "source_note": (
            "Source: Authors’ calculations using Susep, Brazilian Forum on Public Security, IBGE, and vehicle-value "
            "reference data. Values in December 2025 reais. The broad scenario combines premiums and estimated "
            "material losses and may contain overlap; it is not a net welfare-loss measure."
        ),
    },
    "src.figures.fig_10_productive_capacity": {
        "title": "Figure 10. Brazil: productive-capacity losses from homicide",
        "subtitle_template": "{start}–{end} | modeled estimate of expected income not produced",
        "source_note": (
            "Source: Authors’ calculations using SIM/Ministry of Health, Continuous PNAD, and IBGE life tables. "
            "Values in December 2025 reais. This is a modeled expected-income loss rather than observed spending. "
            "The 2025 estimate applies the aggregate homicide count to the 2024 age-region loss profile."
        ),
    },
    "src.figures.fig_11_judicial_costs": {
        "title": "Figure 11. Brazil: crime-related judicial costs",
        "subtitle_template": "{start}–{end} | state justice system, real values, and share of total",
        "source_note": (
            "Source: Authors’ calculations using National Council of Justice, National Council of Public Prosecutors, "
            "and Brazilian Bar Association data. Values in December 2025 reais. Courts and prosecutors are allocated "
            "to criminal matters; defense services are valued using new cases and reference legal fees."
        ),
    },
    "src.figures.fig_12_medical_costs": {
        "title": "Figure 12. Brazil: medical and therapeutic costs of violence",
        "subtitle_template": "{start}–{end} | SUS hospital admissions and productive loss during the stay",
        "source_note": (
            "Source: Authors’ calculations using SIH/SUS microdata and 2025 Continuous PNAD income profiles. Values "
            "in December 2025 reais. The measure combines assault-related hospital payments and temporary productive "
            "loss during nonfatal stays; it excludes outpatient and private care and time away after discharge."
        ),
    },
    "src.figures.fig_13_total_costs": {
        "title": "Figure 13. Brazil: measured economic costs of crime",
        "subtitle_template": "{start}–{end} | accounting total, share of GDP, and share of total",
        "source_note": (
            "Source: Authors’ calculations from the project’s final series. Values in December 2025 reais. The total "
            "combines heterogeneous expenditures, a transfer, insurance premiums, material losses, and modeled "
            "productive losses; it is not a causal welfare-loss estimate."
        ),
    },
    "src.figures.fig_14_state_costs": {
        "title": "Figure 14. States: level and composition of the economic costs of crime",
        "subtitle_template": "{year} | 27 states; state values under review",
        "source_note": (
            "Source: Authors’ calculations from the final state workbook. GDP per capita and monetary values are in "
            "December 2025 reais. Preliminary state results: the state incarceration concept differs from the national "
            "series and 2025 productive losses will be updated before publication."
        ),
        "axis_labels": ("Real GDP per capita (R$ thousands, Dec. 2025)", "Measured costs (% of state GDP)"),
    },
    "src.figures.fig_15_state_trajectories": {
        "title": "Figure 15. States: trajectory of income and the cost of crime",
        "subtitle_template": "{start}–{end} | arrows between levels; state values under review",
        "source_note": (
            "Source: Authors’ calculations from the final state workbook. The horizontal axis is real GDP per capita "
            "in December 2025 reais; the vertical axis is the share of state GDP. Arrows describe trajectories, not "
            "causal effects. State productive losses and the incarceration concept remain preliminary."
        ),
        "axis_labels": ("Real GDP per capita (R$ thousands, Dec. 2025)", "Measured costs (% of state GDP)"),
    },
}

FIGURE_2 = {
    "module": "src.figures.fig_02_crime_trends",
    "outputs": {
        "fig_02a_crimes_registrados.csv": "fig_02a_recorded_crime_en",
        "fig_02b_taxas_criminalidade.csv": "fig_02b_crime_rates_en",
        "fig_02c_crimes_cobertura_parcial.csv": "fig_02c_partial_coverage_counts_en",
        "fig_02d_taxas_cobertura_parcial.csv": "fig_02d_partial_coverage_rates_en",
    },
}


def format_en(value: float, decimals: int = 1) -> str:
    return f"{value:,.{decimals}f}"


def translate_text(value: str) -> str:
    if not value:
        return value
    result = value
    for source, target in sorted(PHRASE_TRANSLATIONS.items(), key=lambda item: len(item[0]), reverse=True):
        result = result.replace(source, target)
    result = result.replace("Fonte:", "Source:")
    result = result.replace("Cálculos dos autores", "Authors’ calculations")
    result = result.replace("dados finais", "final data")
    result = result.replace("por 100 mil habitantes", "per 100,000 inhabitants")
    result = result.replace("valores reais", "real values")
    result = result.replace("valores estaduais em revisão", "state values under review")
    result = result.replace("Ver Apêndice Metodológico.", "See Methodological Appendix.")
    if result.startswith(("Weighted slope:", "Weighted correlation:")):
        result = result.replace(",", ".")
    elif result.replace("-", "", 1).replace(",", "", 1).isdigit() and "," in result:
        result = result.replace(",", ".")
    return result


def translate_csv(source: Path, target: Path) -> None:
    with source.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)
        fields = list(reader.fieldnames or [])
    for row in rows:
        for key, value in row.items():
            if value in VALUE_TRANSLATIONS:
                row[key] = VALUE_TRANSLATIONS[value]
            elif key in {"crime", "componente", "natureza_contabil", "measurement_concept", "plot_unit", "status_ano", "ponto", "macroregion"}:
                row[key] = translate_text(value)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


INTEGER_FIELDS = {
    "year", "ano", "start_year", "end_year", "period_start", "period_end",
    "is_brazil", "sample_reporting_units", "reporting_ufs", "homicide_count",
    "homicides_start", "homicides_end", "visually_clipped",
}


def coerce_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    converted: list[dict[str, Any]] = []
    for row in rows:
        item: dict[str, Any] = {}
        for key, value in row.items():
            if value == "":
                item[key] = value
            elif key.endswith("_code") or key in {"uf", "iso3", "excluded_uf_codes"}:
                item[key] = value
            elif key in INTEGER_FIELDS:
                item[key] = int(float(value))
            else:
                try:
                    item[key] = float(value)
                except ValueError:
                    item[key] = value
        converted.append(item)
    return converted


def _repo_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _translate_figure(fig: Any) -> None:
    for item in fig.findobj(match=lambda artist: isinstance(artist, Text)):
        translated = translate_text(item.get_text())
        if translated.startswith("Source:"):
            translated = textwrap.fill(translated, width=155)
        item.set_text(translated)


def _save_translated(fig: Any, *, output_stem: str, data_path: Path) -> tuple[Path, Path]:
    _translate_figure(fig)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    pdf = FIGURE_DIR / f"{output_stem}.pdf"
    png = FIGURE_DIR / f"{output_stem}.png"
    fig.savefig(pdf, bbox_inches="tight")
    fig.savefig(png, dpi=220, bbox_inches="tight")
    plt.close(fig)
    if any(not path.exists() or path.stat().st_size == 0 for path in (pdf, png, data_path)):
        raise RuntimeError(f"Missing English figure output for {output_stem}")
    return pdf, png


def _patch_module(module: Any, *, stem: str, data_path: Path) -> None:
    module.CONFIG["output_stem"] = stem
    module.CONFIG["data_file"] = data_path
    for key, value in EN_OVERRIDES.get(module.__name__, {}).items():
        module.CONFIG[key] = value
    if hasattr(module, "format_br"):
        module.format_br = format_en
    module.save_figure = _save_translated


def _render_standard(spec: dict[str, Any]) -> dict[str, Any]:
    module = importlib.import_module(spec["module"])
    source = DATA_DIR / spec["csv"]
    english_csv = EN_DATA_DIR / f"{spec['stem']}.csv"
    translate_csv(source, english_csv)
    _patch_module(module, stem=spec["stem"], data_path=english_csv)
    if hasattr(module, "plot"):
        with source.open("r", encoding="utf-8", newline="") as stream:
            rows = coerce_rows(list(csv.DictReader(stream)))
        if module.__name__.endswith("fig_05_microrregion_homicide_convergence"):
            diagnostics = json.loads(Path(module.CONFIG["audit_file"]).read_text(encoding="utf-8"))
            pdf, png = module.plot(rows, diagnostics)
        else:
            pdf, png = module.plot(rows)
    else:
        # Component figures expose only ``main``. Their analytical preparation is
        # deterministic and reads retained local workbooks, so run that existing
        # entry point with English output paths and publication text patched in.
        # Rewrite the parallel CSV afterwards so categorical values are English.
        module.main()
        pdf = FIGURE_DIR / f"{spec['stem']}.pdf"
        png = FIGURE_DIR / f"{spec['stem']}.png"
        translate_csv(source, english_csv)
        if any(not path.exists() or path.stat().st_size == 0 for path in (pdf, png, english_csv)):
            raise RuntimeError(f"Missing English figure output for {spec['stem']}")
    return {"stem": spec["stem"], "data": _repo_path(english_csv), "pdf": _repo_path(pdf), "png": _repo_path(png)}


def _render_figure_2() -> list[dict[str, Any]]:
    module = importlib.import_module(FIGURE_2["module"])
    module.CONFIG["titles"] = {
        "count": "Figure 2A. Brazil: crime trends — recorded victims",
        "rate": "Figure 2B. Brazil: crime trends — recorded victim rates",
    }
    module.CONFIG["subtitle"] = "2016–2025 | six indicators with 27 states and 12 months in every year"
    module.CONFIG["source_note"] = (
        "Source: Authors’ calculations using Sinesp VDE/Ministry of Justice and Public Security and IBGE 2024 "
        "Population Projections. All six indicators count victims rather than incidents; rape and rape of a "
        "vulnerable person are distinct series and are not added together. Femicide is a recent legal classification."
    )
    module.CONFIG["axis_labels"] = {"count": "Thousands of recorded victims", "rate": "Victims per 100,000 inhabitants"}
    module.PARTIAL_CONFIG["titles"] = {
        "count": "Figure 2C. Partial coverage: recorded property-crime trends",
        "rate": "Figure 2D. Partial coverage: recorded property-crime rates",
    }
    module.PARTIAL_CONFIG["subtitle"] = "2016–2025 | indicator-specific balanced reporting panel"
    module.PARTIAL_CONFIG["source_note"] = (
        "Source: Authors’ calculations using Sinesp VDE/Ministry of Justice and Public Security and IBGE 2024 "
        "Population Projections. Each series uses its largest fixed sample of states with 12 reported months in "
        "every year. Values are recorded incidents in those panels, not national totals; missing reports are never zero."
    )
    module.PARTIAL_CONFIG["axis_labels"] = {"count": "Thousands of recorded incidents", "rate": "Incidents per 100,000 inhabitants"}

    def english_sample_note(rows: list[dict[str, object]]) -> str:
        details: list[str] = []
        for crime in module.PARTIAL_CONFIG["crime_order"]:
            endpoint = next(row for row in rows if row["crime"] == crime and int(row["year"]) == 2025)
            excluded = str(endpoint["excluded_uf_codes"]).split()
            details.append(
                f"{CRIME_TRANSLATIONS.get(str(crime), str(crime))}: {int(endpoint['reporting_ufs'])} states, "
                f"{format_en(float(endpoint['population_coverage_pct']), 1)}% of the population in 2025; "
                f"excluded: {', '.join(excluded) if excluded else 'none'}"
            )
        return "Coverage by indicator — " + "; ".join(details) + "."

    module._partial_sample_note = english_sample_note
    outputs: list[dict[str, Any]] = []
    # Figure 2 uses two plotting entry points; patch its shared saver before each call.
    for source_name, stem in FIGURE_2["outputs"].items():
        source = DATA_DIR / source_name
        english_csv = EN_DATA_DIR / f"{stem}.csv"
        translate_csv(source, english_csv)
        with source.open("r", encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        module.save_figure = _save_translated
        if "02a" in source_name or "02b" in source_name:
            kind = "count" if "02a" in source_name else "rate"
            config = module.CONFIG
            config["output_stems"][kind] = stem
            config["data_files"][kind] = english_csv
            pdf, png = module._plot(rows, kind, config)
        else:
            kind = "count" if "02c" in source_name else "rate"
            config = module.PARTIAL_CONFIG
            config["output_stems"][kind] = stem
            config["data_files"][kind] = english_csv
            pdf, png = module._plot(rows, kind, config)
        outputs.append({"stem": stem, "data": _repo_path(english_csv), "pdf": _repo_path(pdf), "png": _repo_path(png)})
    return outputs


def main() -> int:
    EN_DATA_DIR.mkdir(parents=True, exist_ok=True)
    # Shared formatters resolve this function dynamically when ticks are drawn.
    common = importlib.import_module("src.figures.common")
    common.format_br = format_en
    common.save_figure = _save_translated
    outputs = _render_figure_2()
    for spec in FIGURES:
        outputs.append(_render_standard(spec))
    MANIFEST.write_text(json.dumps(outputs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    expected = 18
    if len(outputs) != expected:
        raise AssertionError(f"Expected {expected} English figures; produced {len(outputs)}")
    print(f"PASS: produced {len(outputs)} English figures and translated CSVs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
