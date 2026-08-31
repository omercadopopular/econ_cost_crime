"""Acquire the retained official SIM annual mortality files used by Figures 3–4."""

from __future__ import annotations

from .acquisition import annotate_manifest_source, retain_download
from .homicide_config import SIM_SOURCES, resource_page


def main() -> int:
    for year, source in SIM_SOURCES.items():
        retain_download(
            source_id=str(source.get("source_id", f"sim_mortality_{year}_final")),
            url=str(source["url"]),
            target=source["target"],
            institution="Ministério da Saúde",
            database="Sistema de Informações sobre Mortalidade (SIM), DO_BDD",
            release=str(source["release"]),
            years=[year],
            notes=(
                "Arquivo oficial de mortalidade geral. Recurso do catálogo: "
                f"{resource_page(str(source['resource']))}. A transformação usa CAUSABAS, "
                "DTOBITO e CODMUNRES; o arquivo bruto é retido sem alteração."
            ),
        )
    annotate_manifest_source(
        "sim_mortality_2023_final",
        status="retained_diagnostic_not_used",
        note=(
            "A conversão genérica Mortalidade_Geral_2023_csv.zip foi retida durante a auditoria, "
            "mas não é usada: seu total nacional de 38.559 homicídios não reconcilia com a versão "
            "final DO23OPEN. A produção usa sim_mortality_2023_final_do_open."
        ),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
