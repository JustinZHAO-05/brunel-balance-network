from __future__ import annotations

import numpy as np

from src.config import AnalysisConfig
from src.metrics import compute_metrics, compute_pairwise_correlation


def test_pairwise_correlation_for_identical_trains_is_high() -> None:
    spike_times_ms = np.array([10, 20, 30, 10, 20, 30], dtype=float)
    spike_indices = np.array([0, 0, 0, 1, 1, 1], dtype=int)
    corr, pair_count = compute_pairwise_correlation(
        spike_times_ms,
        spike_indices,
        n_neurons=2,
        duration_ms=40.0,
        bin_ms=5.0,
        sample_pair_count=10,
        seed=0,
    )
    assert pair_count == 1
    assert corr > 0.99


def test_compute_metrics_returns_expected_keys() -> None:
    spike_times_ms = np.array([10, 20, 30, 12, 22, 32], dtype=float)
    spike_indices = np.array([0, 0, 0, 1, 1, 1], dtype=int)
    rate_t_ms = np.arange(0.0, 50.0, 1.0)
    rate_hz = np.full_like(rate_t_ms, 15.0)
    metrics = compute_metrics(
        spike_times_ms=spike_times_ms,
        spike_indices=spike_indices,
        n_recorded=2,
        sim_time_ms=50.0,
        rate_t_ms=rate_t_ms,
        rate_hz=rate_hz,
        analysis=AnalysisConfig(sample_pair_count=10),
        seed=0,
    )
    assert "mean_firing_rate_hz" in metrics
    assert "median_cv_isi" in metrics
    assert "psd_peak_power" in metrics
    assert metrics["valid_cv_neuron_count"] == 2

