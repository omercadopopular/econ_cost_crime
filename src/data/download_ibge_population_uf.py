"""Retain one coherent IBGE population vintage for Figure 2 rates."""

from __future__ import annotations

from zipfile import is_zipfile

from .acquisition import retain_download
from .external_config import IBGE_PROJECTION_PATH, IBGE_PROJECTION_URL


def main() -> int:
    retain_download(
        source_id="ibge_population_projection_2024_uf_age_sex",
        url=IBGE_PROJECTION_URL,
        target=IBGE_PROJECTION_PATH,
        institution="Instituto Brasileiro de Geografia e Estatística (IBGE)",
        database="Projeções da População do Brasil e UFs — Revisão 2024, tabela 1",
        release="Revisão 2024, publicada em 2024-08-22",
        years=list(range(2000, 2071)),
        notes=(
            "População por UF, sexo e idade simples. A transformação de Figure 2 soma ambos os "
            "sexos e todas as idades em 1º de julho, usando a mesma revisão para 2015–2025."
        ),
        validator=is_zipfile,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
