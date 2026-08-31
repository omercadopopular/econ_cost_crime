"""Shared configuration for the SIM/IBGE microrregion homicide pipeline."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_ROOT / "data" / "raw"
INTERIM_DIR = REPO_ROOT / "data" / "interim"
AUDIT_DIR = REPO_ROOT / "data" / "audit"
FIGURE_DATA_DIR = REPO_ROOT / "data" / "figure_data"

ANO_INICIAL = 2016
ANO_FINAL_SIM = 2024
ANOS_SIM = (2015, 2016, 2017, 2022, 2023, 2024)
ANOS_POPULACAO_OFICIAL = (2015, 2016, 2017, 2022, 2024)

SIM_DIR = RAW_DIR / "sim"
IBGE_POP_DIR = RAW_DIR / "ibge_population"
IBGE_GEO_DIR = RAW_DIR / "ibge_geography"
RAW_MANIFEST = RAW_DIR / "source_manifest.json"

CROSSWALK_PATH = INTERIM_DIR / "municipality_microrregion_crosswalk.csv"
MUNICIPAL_PANEL_PATH = INTERIM_DIR / "municipality_homicides_population.csv"
PANEL_PATH = INTERIM_DIR / "microrregion_homicides.csv"
BUILD_AUDIT_PATH = AUDIT_DIR / "homicide_build_audit.json"
VALIDATION_AUDIT_PATH = AUDIT_DIR / "homicide_validation.json"

SIM_SOURCES = {
    2015: {
        "url": "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SIM/Mortalidade_Geral_2015_csv.zip",
        "target": SIM_DIR / "sim_mortalidade_geral_2015_final_2025-12-15_csv.zip",
        "format": "csv_zip",
        "release": "Catálogo atualizado em 2025-12-15",
        "resource": "c8edc1f5-8612-417e-9389-f52ec7057e95",
    },
    2016: {
        "url": "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SIM/Mortalidade_Geral_2016_csv.zip",
        "target": SIM_DIR / "sim_mortalidade_geral_2016_final_2025-12-15_csv.zip",
        "format": "csv_zip",
        "release": "Catálogo atualizado em 2025-12-15",
        "resource": "0be9d65a-c41c-4ee1-94c7-017234f96be8",
    },
    2017: {
        "url": "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SIM/Mortalidade_Geral_2017_csv.zip",
        "target": SIM_DIR / "sim_mortalidade_geral_2017_final_2025-12-15_csv.zip",
        "format": "csv_zip",
        "release": "Catálogo atualizado em 2025-12-15",
        "resource": "980e15e9-327f-49f8-a691-ef5cf0813320",
    },
    2022: {
        "url": "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SIM/json/Mortalidade_Geral_2022_json.zip",
        "target": SIM_DIR / "sim_mortalidade_geral_2022_final_2025-12-15_json.zip",
        "format": "json_zip",
        "release": "Catálogo atualizado em 2025-12-15",
        "resource": "32fd4a5b-3625-49d8-910f-6752574a989d",
    },
    2023: {
        "url": "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SIM/DO23OPEN.csv",
        "target": SIM_DIR / "sim_do_2023_final_2025-08-14.csv",
        "format": "csv",
        "release": "Recurso final DO23OPEN; catálogo atualizado em 2025-08-14",
        "resource": "2a7269c5-91b2-4569-8b36-3ab775328555",
        "source_id": "sim_mortality_2023_final_do_open",
    },
    2024: {
        "url": "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SIM/csv/DO24OPEN_csv.zip",
        "target": SIM_DIR / "sim_mortalidade_geral_2024_final_2026-02-18_csv.zip",
        "format": "csv_zip",
        "release": "Dados finais; recurso atualizado em 2026-02-18",
        "resource": "f0bdf83f-708e-4de9-9582-959055844ae9",
    },
}

POPULATION_SOURCES = {
    2015: {
        "url": "https://apisidra.ibge.gov.br/values/t/6579/n6/all/v/9324/p/2015?formato=json",
        "target": IBGE_POP_DIR / "ibge_sidra_6579_population_2015.json.gz",
        "table": "SIDRA 6579",
        "reference": "Estimativa da população residente em 1º de julho de 2015",
    },
    2016: {
        "url": "https://apisidra.ibge.gov.br/values/t/6579/n6/all/v/9324/p/2016?formato=json",
        "target": IBGE_POP_DIR / "ibge_sidra_6579_population_2016.json.gz",
        "table": "SIDRA 6579",
        "reference": "Estimativa da população residente em 1º de julho de 2016",
    },
    2017: {
        "url": "https://apisidra.ibge.gov.br/values/t/6579/n6/all/v/9324/p/2017?formato=json",
        "target": IBGE_POP_DIR / "ibge_sidra_6579_population_2017.json.gz",
        "table": "SIDRA 6579",
        "reference": "Estimativa da população residente em 1º de julho de 2017",
    },
    2022: {
        "url": "https://apisidra.ibge.gov.br/values/t/4709/n6/all/v/93/p/2022?formato=json",
        "target": IBGE_POP_DIR / "ibge_sidra_4709_census_population_2022.json.gz",
        "table": "SIDRA 4709",
        "reference": "População residente do Censo Demográfico 2022, referência em 1º de agosto",
    },
    2024: {
        "url": "https://apisidra.ibge.gov.br/values/t/6579/n6/all/v/9324/p/2024?formato=json",
        "target": IBGE_POP_DIR / "ibge_sidra_6579_population_2024.json.gz",
        "table": "SIDRA 6579",
        "reference": "Estimativa da população residente em 1º de julho de 2024",
    },
}

LOCALITIES_SOURCE = {
    "url": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios?orderBy=id",
    "target": IBGE_GEO_DIR / "ibge_localities_municipalities_accessed_2026-08-29.json.gz",
    "release": "API de Localidades consultada em 2026-08-29; campo de microrregião antiga",
}

MICROREGION_SHAPE_SOURCE = {
    "url": (
        "https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/"
        "malhas_municipais/municipio_2015/Brasil/BR/br_microrregioes.zip"
    ),
    "target": IBGE_GEO_DIR / "ibge_2015_br_microrregioes.zip",
    "release": "Malha municipal 2015; referência territorial em 2015-07-01; SIRGAS 2000",
}

STATE_SHAPE_SOURCE = {
    "url": (
        "https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/"
        "malhas_municipais/municipio_2015/Brasil/BR/br_unidades_da_federacao.zip"
    ),
    "target": IBGE_GEO_DIR / "ibge_2015_br_unidades_da_federacao.zip",
    "release": "Malha municipal 2015; referência territorial em 2015-07-01; SIRGAS 2000",
}


def resource_page(resource: str) -> str:
    return f"https://dadosabertos.saude.gov.br/dataset/sim/resource/{resource}"
