"""Acquire the fixed 2015 IBGE microrregion geography and municipality crosswalk source."""

from __future__ import annotations

from .acquisition import retain_download
from .homicide_config import LOCALITIES_SOURCE, MICROREGION_SHAPE_SOURCE, STATE_SHAPE_SOURCE


def main() -> int:
    retain_download(
        source_id="ibge_localities_municipalities_2026-08-29",
        url=LOCALITIES_SOURCE["url"],
        target=LOCALITIES_SOURCE["target"],
        institution="Instituto Brasileiro de Geografia e Estatística (IBGE)",
        database="API de Localidades — municípios",
        release=LOCALITIES_SOURCE["release"],
        years=None,
        notes=(
            "O campo microrregiao fornece a classificação antiga. Dos 5.571 municípios retornados, "
            "5.570 têm microrregião; Boa Esperança do Norte, instalado em 2025 e fora do período, "
            "tem microrregião nula."
        ),
    )
    for source_id, source, database in (
        ("ibge_microrregions_shape_2015", MICROREGION_SHAPE_SOURCE, "Malha municipal 2015 — microrregiões"),
        ("ibge_states_shape_2015", STATE_SHAPE_SOURCE, "Malha municipal 2015 — Unidades da Federação"),
    ):
        retain_download(
            source_id=source_id,
            url=source["url"],
            target=source["target"],
            institution="Instituto Brasileiro de Geografia e Estatística (IBGE)",
            database=database,
            release=source["release"],
            years=[2015],
            notes="Malha oficial em escala operacional 1:250.000, coordenadas geográficas e SIRGAS 2000.",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
