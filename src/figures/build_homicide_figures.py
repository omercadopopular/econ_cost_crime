"""Build and validate Figures 3–5 from retained local homicide inputs."""

from __future__ import annotations

from . import (
    fig_03_microrregion_homicides,
    fig_04_microrregion_homicide_change,
    fig_05_microrregion_homicide_convergence,
)
from src.validation import validate_homicide_data


def main() -> int:
    fig_03_microrregion_homicides.main()
    fig_04_microrregion_homicide_change.main()
    fig_05_microrregion_homicide_convergence.main()
    return validate_homicide_data.main([])


if __name__ == "__main__":
    raise SystemExit(main())
