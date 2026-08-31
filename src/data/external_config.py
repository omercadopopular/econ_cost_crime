"""Pinned sources and paths for Figures 1 and 2."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_ROOT / "data" / "raw"
INTERIM_DIR = REPO_ROOT / "data" / "interim"
AUDIT_DIR = REPO_ROOT / "data" / "audit"

SINESP_YEARS = tuple(range(2015, 2026))
SINESP_DIR = RAW_DIR / "sinesp"
SINESP_SOURCE_PAGE = (
    "https://www.gov.br/mj/pt-br/assuntos/sua-seguranca/seguranca-publica/estatistica/"
    "dados-nacionais-1/base-de-dados-e-notas-metodologicas-dos-gestores-estaduais-"
    "sinesp-vde-2022-e-2023"
)
SINESP_URL_TEMPLATE = (
    "https://www.gov.br/mj/pt-br/assuntos/sua-seguranca/seguranca-publica/estatistica/"
    "download/dnsp-base-de-dados/bancovde-{year}.xlsx/@@download/file"
)

IBGE_PROJECTION_URL = (
    "https://ftp.ibge.gov.br/Projecao_da_Populacao/Projecao_da_Populacao_2024/"
    "projecoes_2024_tab1_idade_simples.xlsx"
)
IBGE_PROJECTION_PATH = RAW_DIR / "ibge" / "population" / "projecoes_2024_tab1_idade_simples.xlsx"

UNODC_URL = (
    "https://data.unodc.org/sites/dataportal.unodc.org/files/2026-07/"
    "data_cts_intentional_homicide.xlsx"
)
UNODC_METADATA_URL = (
    "https://data.unodc.org/sites/dataportal.unodc.org/files/2026-07/"
    "metadata_intentional_homicide.pdf"
)
UNODC_DIR = RAW_DIR / "unodc"
UNODC_PATH = UNODC_DIR / "data_cts_intentional_homicide_2026-07.xlsx"
UNODC_METADATA_PATH = UNODC_DIR / "metadata_intentional_homicide_2026-07.pdf"
