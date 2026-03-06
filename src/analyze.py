from __future__ import annotations

import argparse
from pathlib import Path

from src.io_utils import load_run_data, write_metrics
from src.metrics import compute_metrics
from src.plotting import plot_raster, plot_rate_trace, plot_run_summary


def analyze_run(run_dir: str | Path) -> dict[str, float]:
    run_path = Path(run_dir)
    payload = load_run_data(run_path)
    config = payload["config"]
    if config.t_range is not None:
        window_start_ms, window_end_ms = config.t_range
    else:
        window_start_ms, window_end_ms = 0.0, payload["sim_time_ms"]

    spike_mask = (payload["spike_times_ms"] >= window_start_ms) & (payload["spike_times_ms"] <= window_end_ms)
    windowed_spike_times = payload["spike_times_ms"][spike_mask] - window_start_ms
    windowed_spike_indices = payload["spike_indices"][spike_mask]
    rate_mask = (payload["rate_t_ms"] >= window_start_ms) & (payload["rate_t_ms"] <= window_end_ms)
    windowed_rate_t_ms = payload["rate_t_ms"][rate_mask] - window_start_ms
    windowed_rate_hz = payload["rate_hz"][rate_mask]
    if windowed_rate_t_ms.size == 0:
        windowed_rate_t_ms = payload["rate_t_ms"]
        windowed_rate_hz = payload["rate_hz"]
        windowed_spike_times = payload["spike_times_ms"]
        windowed_spike_indices = payload["spike_indices"]
        window_start_ms = 0.0
        window_end_ms = payload["sim_time_ms"]

    metrics = compute_metrics(
        spike_times_ms=windowed_spike_times,
        spike_indices=windowed_spike_indices,
        n_recorded=payload["n_recorded"],
        sim_time_ms=window_end_ms - window_start_ms,
        rate_t_ms=windowed_rate_t_ms,
        rate_hz=windowed_rate_hz,
        analysis=config.analysis,
        seed=config.seed,
    )
    metrics["analysis_window_start_ms"] = window_start_ms
    metrics["analysis_window_end_ms"] = window_end_ms
    write_metrics(run_path / "metrics.json", metrics)
    plot_raster(payload["spike_times_ms"], payload["spike_indices"], config, run_path / "raster.png")
    plot_rate_trace(payload["rate_t_ms"], payload["rate_hz"], config, run_path / "rate_trace.png")
    plot_run_summary(
        payload["spike_times_ms"],
        payload["spike_indices"],
        payload["rate_t_ms"],
        payload["rate_hz"],
        config,
        metrics,
        run_path / "summary.png",
    )
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a saved Brunel simulation run.")
    parser.add_argument("--run-dir", required=True, help="Run directory created by src.simulate.")
    args = parser.parse_args()
    analyze_run(args.run_dir)


if __name__ == "__main__":
    main()
