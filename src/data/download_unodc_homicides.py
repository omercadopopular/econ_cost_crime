"""Retain the official UNODC intentional-homicide data and metadata."""

from __future__ import annotations

from pathlib import Path
from zipfile import is_zipfile

from .acquisition import retain_download
from .external_config import UNODC_METADATA_PATH, UNODC_METADATA_URL, UNODC_PATH, UNODC_URL


def _is_pdf(path: Path) -> bool:
    with path.open("rb") as stream:
        return stream.read(5) == b"%PDF-"


def main() -> int:
    retain_download(
        source_id="unodc_intentional_homicide_2026_07",
        url=UNODC_URL,
        target=UNODC_PATH,
        institution="United Nations Office on Drugs and Crime (UNODC)",
        database="UNODC Research — Data Portal — Intentional Homicide",
        release="Last update 2026-07-12",
        years=None,
        notes=(
            "Official country-year workbook. Figure 1 selects total victims of intentional "
            "homicide, rate per 100,000 population, without replacing country observations."
        ),
        validator=is_zipfile,
    )
    retain_download(
        source_id="unodc_intentional_homicide_metadata_2026_07",
        url=UNODC_METADATA_URL,
        target=UNODC_METADATA_PATH,
        institution="United Nations Office on Drugs and Crime (UNODC)",
        database="Metadata Information — Intentional Homicide",
        release="Last update 2026-07-12",
        years=None,
        notes="Official indicator definition, measurement unit, sources and limitations.",
        validator=_is_pdf,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
