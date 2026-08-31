"""Retain the official annual Sinesp VDE files used by Figure 2."""

from __future__ import annotations

from zipfile import is_zipfile

from .acquisition import retain_download, sha256
from .external_config import (
    AUDIT_DIR,
    SINESP_DIR,
    SINESP_SOURCE_PAGE,
    SINESP_URL_TEMPLATE,
    SINESP_YEARS,
)


def main() -> int:
    for year in SINESP_YEARS:
        target = SINESP_DIR / f"bancovde-{year}.xlsx"
        repaired_note = ""
        if target.exists() and not is_zipfile(target):
            digest = sha256(target)
            quarantine = (
                AUDIT_DIR
                / "corrupt_downloads"
                / f"bancovde-{year}.{digest[:12]}.truncated.xlsx"
            )
            quarantine.parent.mkdir(parents=True, exist_ok=True)
            if quarantine.exists():
                raise RuntimeError(f"Quarantine target already exists: {quarantine}")
            target.replace(quarantine)
            quarantine_display = quarantine.relative_to(AUDIT_DIR.parent.parent).as_posix()
            repaired_note = (
                f" Uma transferência truncada foi preservada em {quarantine_display} e a "
                "rota oficial foi baixada novamente com retomada por intervalos HTTP."
            )
        retain_download(
            source_id=f"sinesp_vde_{year}",
            url=SINESP_URL_TEMPLATE.format(year=year),
            target=target,
            institution="Ministério da Justiça e Segurança Pública (MJSP)",
            database="Sinesp VDE — Dados Nacionais de Segurança Pública",
            release=f"Arquivo anual {year}; página-fonte atualizada em 2026-08-26",
            years=[year],
            notes=(
                "Arquivo oficial mensal por UF. Indicadores podem contar vítimas, ocorrências ou "
                "objetos, conforme o campo; ausências não são convertidas em zero. Página de "
                f"referência: {SINESP_SOURCE_PAGE}.{repaired_note}"
            ),
            validator=is_zipfile,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
