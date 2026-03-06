from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd

from src.analyze import analyze_run
from src.config import load_simulation_config, load_sweep_config
from src.io_utils import ensure_dir, load_run_data, write_json
from src.model import run_simulation
from src.plotting import build_metrics_figure, build_panel_figure
from src.sweep import run_sweep


PANEL_CONFIGS = [
    Path("configs/presets/panel_a.yaml"),
    Path("configs/presets/panel_b.yaml"),
    Path("configs/presets/panel_c.yaml"),
    Path("configs/presets/panel_d.yaml"),
]

PROFILES: dict[str, dict[str, Any]] = {
    "quick": {
        "simulation_overrides": {
            "N_E": 1500,
            "record_n_neurons": 80,
            "analysis": {
                "sample_pair_count": 80,
            },
        },
        "sweep_config": Path("configs/sweeps/quick.yaml"),
    },
    "poster": {
        "simulation_overrides": {
            "N_E": 4000,
            "record_n_neurons": 120,
            "analysis": {
                "sample_pair_count": 120,
            },
        },
        "sweep_config": Path("configs/sweeps/poster.yaml"),
    },
}


def _load_panel_payload(run_dir: Path) -> dict[str, object]:
    payload = load_run_data(run_dir)
    payload["label"] = payload["config"].name.replace("panel_", "").upper()
    return payload


def evaluate_acceptance(panel_metrics: pd.DataFrame, required_outputs: list[Path]) -> dict[str, object]:
    metric_by_panel = panel_metrics.set_index("panel")
    sync_panels = metric_by_panel.loc[["A", "B"]]
    async_panels = metric_by_panel.loc[["C", "D"]]

    sync_power = float(sync_panels["psd_peak_power"].mean())
    async_power = float(async_panels["psd_peak_power"].mean())
    sync_corr = float(sync_panels["pairwise_correlation"].abs().mean())
    async_corr = float(async_panels["pairwise_correlation"].abs().mean())
    async_cv = float(async_panels["median_cv_isi"].median())
    outputs_ok = all(path.exists() for path in required_outputs)

    rules = {
        "sync_peak_power_gt_async": {
            "passed": bool(sync_power > async_power * 1.2),
            "detail": f"sync={sync_power:.4f}, async={async_power:.4f}",
        },
        "async_corr_lt_sync": {
            "passed": bool(async_corr < sync_corr),
            "detail": f"|sync|={sync_corr:.4f}, |async|={async_corr:.4f}",
        },
        "async_cv_near_irregular": {
            "passed": bool(async_cv >= 0.8),
            "detail": f"median async CV(ISI)={async_cv:.4f}",
        },
        "required_outputs_present": {
            "passed": outputs_ok,
            "detail": f"{sum(path.exists() for path in required_outputs)}/{len(required_outputs)} required files found",
        },
    }
    passed_count = sum(int(rule["passed"]) for rule in rules.values())
    return {
        "passed": passed_count == len(rules),
        "passed_count": passed_count,
        "rule_count": len(rules),
        "rules": rules,
    }


def run_reproduction(preset: str) -> dict[str, object]:
    if preset not in PROFILES:
        raise ValueError(f"Unknown preset: {preset}")

    profile = PROFILES[preset]
    reproduction_dir = ensure_dir(Path("artifacts") / "reproductions" / preset)
    panel_rows = []
    panel_payloads = []

    for config_path in PANEL_CONFIGS:
        base_config = load_simulation_config(config_path)
        config = base_config.with_overrides(profile["simulation_overrides"])
        run_dir = reproduction_dir / "panels" / config.name
        run_simulation(config, run_dir)
        metrics = analyze_run(run_dir)
        payload = _load_panel_payload(run_dir)
        panel_payloads.append(payload)
        panel_rows.append({"panel": payload["label"], **metrics})

    panel_metrics = pd.DataFrame(panel_rows).sort_values("panel").reset_index(drop=True)
    panel_metrics.to_csv(reproduction_dir / "panel_metrics.csv", index=False)
    build_panel_figure(panel_payloads, reproduction_dir / "figure1_panels.png")

    sweep_cfg = load_sweep_config(profile["sweep_config"])
    sweep_df = run_sweep(profile["sweep_config"])
    phase_diagram = sweep_cfg.output_dir / "phase_diagram.png"
    phase_copy = reproduction_dir / "figure2_phase_diagram.png"
    phase_copy.write_bytes(phase_diagram.read_bytes())

    required_outputs = [
        reproduction_dir / "figure1_panels.png",
        reproduction_dir / "figure2_phase_diagram.png",
        reproduction_dir / "panel_metrics.csv",
    ]
    acceptance = evaluate_acceptance(panel_metrics, required_outputs)
    build_metrics_figure(panel_metrics, acceptance, reproduction_dir / "figure3_metrics.png")
    required_outputs.append(reproduction_dir / "figure3_metrics.png")
    acceptance = evaluate_acceptance(panel_metrics, required_outputs)

    write_json(reproduction_dir / "acceptance.json", acceptance)
    write_json(Path("artifacts") / "acceptance.json", {"preset": preset, **acceptance})
    sweep_df.to_csv(reproduction_dir / "sweep_summary.csv", index=False)
    return {
        "panel_metrics": panel_metrics,
        "sweep_df": sweep_df,
        "acceptance": acceptance,
        "reproduction_dir": str(reproduction_dir),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the end-to-end Brunel reproduction workflow.")
    parser.add_argument("--preset", choices=sorted(PROFILES.keys()), required=True)
    args = parser.parse_args()
    run_reproduction(args.preset)


if __name__ == "__main__":
    main()
