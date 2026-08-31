"""Build Figures 6--15 in sequence and validate all generated outputs."""

from __future__ import annotations

from importlib import import_module

from .common import MANIFEST_PATH


FIGURE_MODULES = (
    "src.figures.fig_06_public_security",
    "src.figures.fig_07_private_security",
    "src.figures.fig_08_incarceration",
    "src.figures.fig_09_insurance_material_losses",
    "src.figures.fig_10_productive_capacity",
    "src.figures.fig_11_judicial_costs",
    "src.figures.fig_12_medical_costs",
    "src.figures.fig_13_total_costs",
    "src.figures.fig_14_state_costs",
    "src.figures.fig_15_state_trajectories",
)


def main() -> int:
    # A full build defines the complete current numbered set; discard stale
    # entries left by earlier numbering schemes before recording new outputs.
    MANIFEST_PATH.unlink(missing_ok=True)
    for module_name in FIGURE_MODULES:
        module = import_module(module_name)
        print(f"BUILD {module.CONFIG['output_stem']}")
        status = module.main()
        if status:
            return int(status)
    from .validate_figures import main as validate

    return validate()


if __name__ == "__main__":
    raise SystemExit(main())
