from __future__ import annotations

import argparse
import itertools
from pathlib import Path

import pandas as pd

from src.analyze import analyze_run
from src.config import load_simulation_config, load_sweep_config
from src.io_utils import ensure_dir
from src.model import run_simulation
from src.plotting import build_phase_diagram


def run_sweep(config_path: str | Path) -> pd.DataFrame:
    sweep_config = load_sweep_config(config_path)
    base_config = load_simulation_config(sweep_config.base_config)
    output_dir = ensure_dir(sweep_config.output_dir)
    runs_dir = ensure_dir(output_dir / "runs")

    rows = []
    for g_value, nu_ratio in itertools.product(
        sweep_config.grid["g"],
        sweep_config.grid["nu_ext_over_nu_thr"],
    ):
        config = base_config.with_overrides(
            {
                **sweep_config.overrides,
                "name": f"{sweep_config.name}_g{g_value:.2f}_nu{nu_ratio:.2f}".replace(".", "p"),
                "g": g_value,
                "nu_ext_over_nu_thr": nu_ratio,
            }
        )
        run_dir = runs_dir / config.name
        run_simulation(config, run_dir)
        metrics = analyze_run(run_dir)
        rows.append(
            {
                "run_name": config.name,
                "g": g_value,
                "nu_ext_over_nu_thr": nu_ratio,
                **metrics,
            }
        )

    summary_df = pd.DataFrame(rows).sort_values(["nu_ext_over_nu_thr", "g"]).reset_index(drop=True)
    summary_df.to_csv(output_dir / "summary.csv", index=False)
    build_phase_diagram(summary_df, output_dir / "phase_diagram.png")
    return summary_df


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a parameter sweep for the Brunel balance network.")
    parser.add_argument("--config", required=True, help="Path to YAML sweep config.")
    args = parser.parse_args()
    run_sweep(args.config)


if __name__ == "__main__":
    main()

