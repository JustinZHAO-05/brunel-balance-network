from __future__ import annotations

from pathlib import Path

import yaml

from src.analyze import analyze_run
from src.config import REPO_ROOT, load_simulation_config
from src.model import run_simulation
from src.reproduce import PROFILES, run_reproduction
from src.sweep import run_sweep


def test_simulate_then_analyze_pipeline(tmp_path: Path) -> None:
    config = load_simulation_config(REPO_ROOT / "configs/presets/panel_c.yaml").with_overrides(
        {
            "name": "test_panel_c",
            "N_E": 120,
            "sim_time_ms": 120.0,
            "record_n_neurons": 20,
            "t_range": [0.0, 120.0],
            "rate_range": [0.0, 150.0],
            "rate_tick_step": 25.0,
            "analysis": {"sample_pair_count": 10},
        }
    )
    run_dir = tmp_path / "run"
    run_simulation(config, run_dir)
    metrics = analyze_run(run_dir)
    assert (run_dir / "spikes.npz").exists()
    assert (run_dir / "population_rate.csv").exists()
    assert (run_dir / "metrics.json").exists()
    assert (run_dir / "summary.png").exists()
    assert "mean_firing_rate_hz" in metrics


def test_sweep_smoke(tmp_path: Path) -> None:
    config_path = tmp_path / "mini_sweep.yaml"
    config_path.write_text(
        yaml.safe_dump(
            {
                "name": "mini_sweep",
                "base_config": str(REPO_ROOT / "configs/presets/panel_c.yaml"),
                "output_dir": str(tmp_path / "mini_sweep_output"),
                "overrides": {
                    "N_E": 100,
                    "sim_time_ms": 80.0,
                    "record_n_neurons": 20,
                    "t_range": [0.0, 80.0],
                    "rate_range": [0.0, 150.0],
                    "analysis": {"sample_pair_count": 10},
                },
                "grid": {
                    "g": [4.5, 5.0],
                    "nu_ext_over_nu_thr": [1.5, 2.0],
                },
            }
        ),
        encoding="utf-8",
    )
    summary_df = run_sweep(config_path)
    assert len(summary_df) == 4
    assert (tmp_path / "mini_sweep_output" / "summary.csv").exists()
    assert (tmp_path / "mini_sweep_output" / "phase_diagram.png").exists()


def test_reproduce_quick_smoke(tmp_path: Path) -> None:
    sweep_path = tmp_path / "repro_quick.yaml"
    sweep_path.write_text(
        yaml.safe_dump(
            {
                "name": "repro_quick",
                "base_config": str(REPO_ROOT / "configs/presets/panel_c.yaml"),
                "output_dir": str(tmp_path / "repro_quick_output"),
                "overrides": {
                    "N_E": 80,
                    "sim_time_ms": 60.0,
                    "record_n_neurons": 15,
                    "t_range": [0.0, 60.0],
                    "rate_range": [0.0, 150.0],
                    "analysis": {"sample_pair_count": 5},
                },
                "grid": {
                    "g": [4.5, 5.0],
                    "nu_ext_over_nu_thr": [1.5, 2.0],
                },
            }
        ),
        encoding="utf-8",
    )
    original = PROFILES["quick"]
    PROFILES["quick"] = {
        "simulation_overrides": {
            "N_E": 80,
            "sim_time_ms": 60.0,
            "record_n_neurons": 15,
            "t_range": [0.0, 60.0],
            "rate_range": [0.0, 150.0],
            "analysis": {"sample_pair_count": 5},
        },
        "sweep_config": sweep_path,
    }
    try:
        result = run_reproduction("quick")
    finally:
        PROFILES["quick"] = original
    assert result["acceptance"]["rule_count"] == 4
    assert Path(result["reproduction_dir"]).joinpath("figure1_panels.png").exists()
    assert Path(result["reproduction_dir"]).joinpath("figure3_metrics.png").exists()
