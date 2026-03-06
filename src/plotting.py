from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import SimulationConfig


def _select_window(t_ms: np.ndarray, values: np.ndarray, t_range: list[float] | None) -> tuple[np.ndarray, np.ndarray]:
    if t_range is None:
        return t_ms, values
    mask = (t_ms >= t_range[0]) & (t_ms <= t_range[1])
    return t_ms[mask], values[mask]


def _draw_raster(ax: plt.Axes, spike_times_ms: np.ndarray, spike_indices: np.ndarray, config: SimulationConfig, title: str) -> None:
    t_ms = spike_times_ms
    idx = spike_indices
    if config.t_range is not None:
        mask = (t_ms >= config.t_range[0]) & (t_ms <= config.t_range[1])
        t_ms = t_ms[mask]
        idx = idx[mask]
    ax.scatter(t_ms, idx, s=5, c="#111111", linewidths=0)
    ax.set_title(title, fontsize=11)
    ax.set_ylabel("Neuron")
    ax.set_xlabel("Time (ms)")
    if config.t_range is not None:
        ax.set_xlim(config.t_range)


def _draw_rate(ax: plt.Axes, rate_t_ms: np.ndarray, rate_hz: np.ndarray, config: SimulationConfig, title: str) -> None:
    t_plot, rate_plot = _select_window(rate_t_ms, rate_hz, config.t_range)
    ax.plot(t_plot, rate_plot, color="#0072B2", linewidth=1.5)
    ax.set_title(title, fontsize=11)
    ax.set_ylabel("Rate (Hz)")
    ax.set_xlabel("Time (ms)")
    if config.t_range is not None:
        ax.set_xlim(config.t_range)
    if config.rate_range is not None:
        ax.set_ylim(config.rate_range)
    if config.rate_tick_step:
        low, high = ax.get_ylim()
        ax.set_yticks(np.arange(low, high + config.rate_tick_step, config.rate_tick_step))


def plot_raster(spike_times_ms: np.ndarray, spike_indices: np.ndarray, config: SimulationConfig, out_path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(7.0, 3.5))
    _draw_raster(ax, spike_times_ms, spike_indices, config, f"Raster: {config.name}")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_rate_trace(rate_t_ms: np.ndarray, rate_hz: np.ndarray, config: SimulationConfig, out_path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(7.0, 3.5))
    _draw_rate(ax, rate_t_ms, rate_hz, config, f"Population Rate: {config.name}")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_run_summary(
    spike_times_ms: np.ndarray,
    spike_indices: np.ndarray,
    rate_t_ms: np.ndarray,
    rate_hz: np.ndarray,
    config: SimulationConfig,
    metrics: dict[str, float],
    out_path: str | Path,
) -> None:
    fig, axes = plt.subplots(3, 1, figsize=(8.0, 8.5), constrained_layout=True)
    _draw_raster(axes[0], spike_times_ms, spike_indices, config, f"{config.name}: raster")
    _draw_rate(axes[1], rate_t_ms, rate_hz, config, f"{config.name}: population rate")
    axes[2].axis("off")
    lines = [
        f"mean firing rate: {metrics['mean_firing_rate_hz']:.2f} Hz",
        f"recorded mean rate: {metrics['recorded_mean_rate_hz']:.2f} Hz",
        f"median CV(ISI): {metrics['median_cv_isi']:.3f}",
        f"Fano factor: {metrics['fano_factor']:.3f}",
        f"pairwise corr: {metrics['pairwise_correlation']:.3f}",
        f"PSD peak: {metrics['psd_peak_frequency_hz']:.2f} Hz",
        f"PSD power: {metrics['psd_peak_power']:.3f}",
    ]
    axes[2].text(0.02, 0.95, "\n".join(lines), va="top", ha="left", family="monospace", fontsize=10)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def build_panel_figure(panel_payloads: list[dict[str, object]], out_path: str | Path) -> None:
    fig, axes = plt.subplots(len(panel_payloads), 2, figsize=(12.0, 3.4 * len(panel_payloads)), constrained_layout=True)
    for row_idx, payload in enumerate(panel_payloads):
        config = payload["config"]
        _draw_raster(
            axes[row_idx, 0],
            payload["spike_times_ms"],
            payload["spike_indices"],
            config,
            f"Panel {payload['label']} raster",
        )
        _draw_rate(
            axes[row_idx, 1],
            payload["rate_t_ms"],
            payload["rate_hz"],
            config,
            f"Panel {payload['label']} population rate",
        )
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def build_phase_diagram(summary_df: pd.DataFrame, out_path: str | Path) -> None:
    required_columns = {
        "g",
        "nu_ext_over_nu_thr",
        "mean_firing_rate_hz",
        "median_cv_isi",
        "pairwise_correlation",
        "psd_peak_power",
    }
    missing = sorted(required_columns - set(summary_df.columns))
    if missing:
        raise ValueError(f"Missing required columns for phase diagram: {', '.join(missing)}")

    metrics = [
        ("mean_firing_rate_hz", "Mean rate (Hz)"),
        ("median_cv_isi", "Median CV(ISI)"),
        ("pairwise_correlation", "Pairwise corr"),
        ("psd_peak_power", "PSD peak power"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 8.5), constrained_layout=True)
    g_values = sorted(summary_df["g"].unique())
    nu_values = sorted(summary_df["nu_ext_over_nu_thr"].unique())
    extent = [min(g_values), max(g_values), min(nu_values), max(nu_values)]

    for ax, (column, title) in zip(axes.flat, metrics, strict=False):
        pivot = summary_df.pivot(index="nu_ext_over_nu_thr", columns="g", values=column)
        image = ax.imshow(
            pivot.sort_index().to_numpy(),
            aspect="auto",
            origin="lower",
            extent=extent,
            cmap="viridis",
        )
        ax.set_title(title)
        ax.set_xlabel("g")
        ax.set_ylabel("nu_ext / nu_thr")
        fig.colorbar(image, ax=ax, shrink=0.85)

    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def build_metrics_figure(metrics_df: pd.DataFrame, acceptance: dict[str, object], out_path: str | Path) -> None:
    required_columns = {
        "panel",
        "mean_firing_rate_hz",
        "median_cv_isi",
        "pairwise_correlation",
        "psd_peak_power",
    }
    missing = sorted(required_columns - set(metrics_df.columns))
    if missing:
        raise ValueError(f"Missing required columns for metrics figure: {', '.join(missing)}")

    fig, axes = plt.subplots(2, 2, figsize=(11.0, 8.0), constrained_layout=True)
    metrics = [
        ("mean_firing_rate_hz", "Mean rate (Hz)", "#0072B2"),
        ("median_cv_isi", "Median CV(ISI)", "#009E73"),
        ("pairwise_correlation", "Pairwise corr", "#D55E00"),
        ("psd_peak_power", "PSD peak power", "#CC79A7"),
    ]
    for ax, (column, title, color) in zip(axes.flat, metrics, strict=False):
        ax.bar(metrics_df["panel"], metrics_df[column], color=color)
        ax.set_title(title)
        ax.set_xlabel("Panel")
        ax.set_ylabel(title)

    summary_lines = []
    for rule_name, rule_payload in acceptance["rules"].items():
        marker = "PASS" if rule_payload["passed"] else "FAIL"
        summary_lines.append(f"{marker} {rule_name}: {rule_payload['detail']}")
    fig.text(
        0.5,
        0.01,
        "\n".join(summary_lines),
        ha="center",
        va="bottom",
        fontsize=9,
        family="monospace",
        bbox={"boxstyle": "round,pad=0.4", "facecolor": "#F7F7F7", "edgecolor": "#CCCCCC"},
    )
    fig.savefig(out_path, dpi=160)
    plt.close(fig)

