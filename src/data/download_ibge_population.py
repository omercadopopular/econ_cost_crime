"""Acquire official municipal population denominators from the IBGE SIDRA API."""

from __future__ import annotations

from .acquisition import retain_download
from .homicide_config import POPULATION_SOURCES


def main() -> int:
    for year, source in POPULATION_SOURCES.items():
        retain_download(
            source_id=f"ibge_population_{year}",
            url=str(source["url"]),
            target=source["target"],
            institution="Instituto Brasileiro de Geografia e Estatística (IBGE)",
            database=str(source["table"]),
            release=str(source["reference"]),
            years=[year],
            notes=(
                "Consulta municipal oficial em JSON. Para 2023 não há estimativa municipal na tabela "
                "6579; o painel diagnóstico interpola linearmente 2022–2024 e identifica essa observação."
            ),
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
