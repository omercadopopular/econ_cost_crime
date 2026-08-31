"""Rebuild Figures 1 and 2A–2D from retained raw inputs, without downloading."""

from __future__ import annotations

from src.data import build_sinesp_panel, build_unodc_homicide_panel
from src.figures import fig_01_world_homicides, fig_02_crime_trends
from src.validation import validate_external_figures


def main() -> int:
    for name, function in (
        ("Sinesp panel", build_sinesp_panel.main),
        ("Figures 2A–2D", fig_02_crime_trends.main),
        ("UNODC panel", build_unodc_homicide_panel.main),
        ("Figure 1", fig_01_world_homicides.main),
    ):
        print(f"BUILD {name}")
        status = function()
        if status:
            return int(status)
    return validate_external_figures.main()


if __name__ == "__main__":
    raise SystemExit(main())
