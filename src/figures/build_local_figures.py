"""Build Figures 5--14 in sequence and validate all generated outputs."""

from __future__ import annotations

from importlib import import_module


FIGURE_MODULES = (
    "src.figures.fig_05_public_security",
    "src.figures.fig_06_private_security",
    "src.figures.fig_07_incarceration",
    "src.figures.fig_08_insurance_material_losses",
    "src.figures.fig_09_productive_capacity",
    "src.figures.fig_10_judicial_costs",
    "src.figures.fig_11_medical_costs",
    "src.figures.fig_12_total_costs",
    "src.figures.fig_13_state_costs",
    "src.figures.fig_14_state_trajectories",
)


def main() -> int:
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

