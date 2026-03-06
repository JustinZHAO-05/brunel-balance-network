from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.config import SimulationConfig, load_simulation_config


def ensure_dir(path: str | Path) -> Path:
    resolved = Path(path)
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)


def read_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_spikes(
    path: str | Path,
    times_ms: np.ndarray,
    indices: np.ndarray,
    n_recorded: int,
    total_neurons: int,
    sim_time_ms: float,
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        target,
        times_ms=np.asarray(times_ms, dtype=float),
        indices=np.asarray(indices, dtype=int),
        n_recorded=np.array([n_recorded], dtype=int),
        total_neurons=np.array([total_neurons], dtype=int),
        sim_time_ms=np.array([sim_time_ms], dtype=float),
    )


def load_run_data(run_dir: str | Path) -> dict[str, Any]:
    resolved = Path(run_dir)
    config = load_simulation_config(resolved / "config_resolved.yaml")
    spikes = np.load(resolved / "spikes.npz")
    rate_df = pd.read_csv(resolved / "population_rate.csv")
    return {
        "config": config,
        "spike_times_ms": spikes["times_ms"],
        "spike_indices": spikes["indices"],
        "n_recorded": int(spikes["n_recorded"][0]),
        "total_neurons": int(spikes["total_neurons"][0]),
        "sim_time_ms": float(spikes["sim_time_ms"][0]),
        "rate_t_ms": rate_df["t_ms"].to_numpy(dtype=float),
        "rate_hz": rate_df["rate_hz"].to_numpy(dtype=float),
    }


def write_population_rate(path: str | Path, t_ms: np.ndarray, rate_hz: np.ndarray) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        {
            "t_ms": np.asarray(t_ms, dtype=float),
            "rate_hz": np.asarray(rate_hz, dtype=float),
        }
    ).to_csv(target, index=False)


def write_metrics(path: str | Path, metrics: dict[str, Any]) -> None:
    serializable = {}
    for key, value in metrics.items():
        if isinstance(value, np.generic):
            serializable[key] = value.item()
        else:
            serializable[key] = value
    write_json(path, serializable)


def normalize_panel_label(name: str) -> str:
    return name.replace("panel_", "").upper()
