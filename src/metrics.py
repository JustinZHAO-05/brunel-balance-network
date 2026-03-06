from __future__ import annotations

from itertools import combinations
from typing import Any

import numpy as np
from scipy.signal import welch

from src.config import AnalysisConfig


def _group_spikes_by_neuron(spike_times_ms: np.ndarray, spike_indices: np.ndarray, n_neurons: int) -> list[np.ndarray]:
    grouped = [list() for _ in range(n_neurons)]
    for time_ms, neuron_idx in zip(spike_times_ms, spike_indices, strict=False):
        if 0 <= int(neuron_idx) < n_neurons:
            grouped[int(neuron_idx)].append(float(time_ms))
    return [np.asarray(times, dtype=float) for times in grouped]


def compute_cv_isi(spike_times_ms: np.ndarray, spike_indices: np.ndarray, n_neurons: int) -> tuple[float, int]:
    cvs = []
    for neuron_spikes in _group_spikes_by_neuron(spike_times_ms, spike_indices, n_neurons):
        if neuron_spikes.size < 3:
            continue
        isis = np.diff(neuron_spikes)
        mean_isi = float(np.mean(isis))
        if mean_isi <= 0:
            continue
        cvs.append(float(np.std(isis) / mean_isi))
    if not cvs:
        return float("nan"), 0
    return float(np.median(cvs)), len(cvs)


def compute_fano_factor(spike_times_ms: np.ndarray, duration_ms: float, bin_ms: float) -> float:
    bins = np.arange(0.0, duration_ms + bin_ms, bin_ms)
    counts, _ = np.histogram(spike_times_ms, bins=bins)
    mean_count = float(np.mean(counts))
    if mean_count <= 0:
        return float("nan")
    return float(np.var(counts) / mean_count)


def _binned_spike_matrix(
    spike_times_ms: np.ndarray,
    spike_indices: np.ndarray,
    n_neurons: int,
    duration_ms: float,
    bin_ms: float,
) -> np.ndarray:
    n_bins = max(int(np.ceil(duration_ms / bin_ms)), 1)
    matrix = np.zeros((n_neurons, n_bins), dtype=float)
    bin_indices = np.floor(spike_times_ms / bin_ms).astype(int)
    valid = (bin_indices >= 0) & (bin_indices < n_bins) & (spike_indices >= 0) & (spike_indices < n_neurons)
    for neuron_idx, bin_idx in zip(spike_indices[valid], bin_indices[valid], strict=False):
        matrix[int(neuron_idx), int(bin_idx)] += 1.0
    return matrix


def compute_pairwise_correlation(
    spike_times_ms: np.ndarray,
    spike_indices: np.ndarray,
    n_neurons: int,
    duration_ms: float,
    bin_ms: float,
    sample_pair_count: int,
    seed: int,
) -> tuple[float, int]:
    matrix = _binned_spike_matrix(spike_times_ms, spike_indices, n_neurons, duration_ms, bin_ms)
    active_neurons = [idx for idx in range(n_neurons) if np.var(matrix[idx]) > 0]
    if len(active_neurons) < 2:
        return float("nan"), 0

    all_pairs = list(combinations(active_neurons, 2))
    if not all_pairs:
        return float("nan"), 0

    rng = np.random.default_rng(seed)
    if len(all_pairs) > sample_pair_count:
        indices = rng.choice(len(all_pairs), size=sample_pair_count, replace=False)
        candidate_pairs = [all_pairs[int(idx)] for idx in indices]
    else:
        candidate_pairs = all_pairs

    correlations = []
    for left, right in candidate_pairs:
        left_series = matrix[left]
        right_series = matrix[right]
        if np.std(left_series) == 0 or np.std(right_series) == 0:
            continue
        corr = np.corrcoef(left_series, right_series)[0, 1]
        if np.isfinite(corr):
            correlations.append(float(corr))

    if not correlations:
        return float("nan"), 0
    return float(np.mean(correlations)), len(correlations)


def compute_psd_peak(rate_t_ms: np.ndarray, rate_hz: np.ndarray) -> tuple[float, float]:
    if rate_t_ms.size < 8 or rate_hz.size < 8:
        return float("nan"), float("nan")
    dt_ms = float(np.median(np.diff(rate_t_ms)))
    if dt_ms <= 0:
        return float("nan"), float("nan")
    demeaned = rate_hz - np.mean(rate_hz)
    if np.allclose(demeaned, 0.0):
        return 0.0, 0.0
    fs = 1000.0 / dt_ms
    freqs, power = welch(demeaned, fs=fs, nperseg=min(1024, rate_hz.size))
    valid = freqs > 0
    if not np.any(valid):
        return float("nan"), float("nan")
    peak_idx = np.argmax(power[valid])
    valid_freqs = freqs[valid]
    valid_power = power[valid]
    return float(valid_freqs[peak_idx]), float(valid_power[peak_idx])


def compute_metrics(
    *,
    spike_times_ms: np.ndarray,
    spike_indices: np.ndarray,
    n_recorded: int,
    sim_time_ms: float,
    rate_t_ms: np.ndarray,
    rate_hz: np.ndarray,
    analysis: AnalysisConfig,
    seed: int,
) -> dict[str, Any]:
    mean_firing_rate_hz = float(np.mean(rate_hz)) if rate_hz.size else float("nan")
    recorded_mean_rate_hz = (
        float(spike_times_ms.size / max(n_recorded, 1) / (sim_time_ms / 1000.0))
        if sim_time_ms > 0
        else float("nan")
    )
    median_cv_isi, valid_cv_neuron_count = compute_cv_isi(spike_times_ms, spike_indices, n_recorded)
    fano_factor = compute_fano_factor(spike_times_ms, sim_time_ms, analysis.fano_bin_ms)
    pairwise_correlation, pair_count = compute_pairwise_correlation(
        spike_times_ms,
        spike_indices,
        n_recorded,
        sim_time_ms,
        analysis.correlation_bin_ms,
        analysis.sample_pair_count,
        seed,
    )
    psd_peak_frequency_hz, psd_peak_power = compute_psd_peak(rate_t_ms, rate_hz)

    return {
        "mean_firing_rate_hz": mean_firing_rate_hz,
        "recorded_mean_rate_hz": recorded_mean_rate_hz,
        "median_cv_isi": median_cv_isi,
        "valid_cv_neuron_count": valid_cv_neuron_count,
        "fano_factor": fano_factor,
        "pairwise_correlation": pairwise_correlation,
        "pairwise_correlation_pairs": pair_count,
        "psd_peak_frequency_hz": psd_peak_frequency_hz,
        "psd_peak_power": psd_peak_power,
        "spike_count": int(spike_times_ms.size),
    }

