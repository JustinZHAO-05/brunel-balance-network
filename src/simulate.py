from __future__ import annotations

import argparse
from pathlib import Path

from src.config import load_simulation_config
from src.model import run_simulation


def default_output_dir(config_name: str) -> Path:
    return Path("artifacts") / "runs" / config_name


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a Brunel balance network simulation.")
    parser.add_argument("--config", required=True, help="Path to YAML simulation config.")
    parser.add_argument("--output-dir", help="Optional output directory. Defaults to artifacts/runs/<name>.")
    args = parser.parse_args()

    config = load_simulation_config(args.config)
    output_dir = Path(args.output_dir) if args.output_dir else default_output_dir(config.name)
    run_simulation(config, output_dir)


if __name__ == "__main__":
    main()
