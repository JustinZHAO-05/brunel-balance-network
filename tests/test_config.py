from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from src.config import REPO_ROOT, load_simulation_config


def test_load_panel_a_config() -> None:
    config = load_simulation_config(REPO_ROOT / "configs/presets/panel_a.yaml")
    assert config.name == "panel_a"
    assert config.g == 3.0
    assert config.nu_ext_over_nu_thr == 2.0
    assert config.N_I == 2500


def test_invalid_config_is_rejected(tmp_path: Path) -> None:
    bad_config = {
        "name": "bad",
        "seed": 1,
        "N_E": -10,
        "gamma": 0.25,
        "epsilon": 0.1,
        "tau_m": 20.0,
        "tau_rp": 2.0,
        "theta": 20.0,
        "V_r": 10.0,
        "J": 0.1,
        "g": 5.0,
        "delay": 1.5,
        "nu_ext_over_nu_thr": 2.0,
        "dt": 0.1,
        "sim_time_ms": 100.0,
        "record_n_neurons": 10,
        "analysis": {"sample_pair_count": 10},
    }
    path = tmp_path / "bad.yaml"
    path.write_text(yaml.safe_dump(bad_config), encoding="utf-8")
    with pytest.raises(ValueError, match="N_E must be positive"):
        load_simulation_config(path)

