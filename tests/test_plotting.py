from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.plotting import build_metrics_figure, build_phase_diagram


def test_build_phase_diagram_requires_columns(tmp_path: Path) -> None:
    df = pd.DataFrame({"g": [3.0], "nu_ext_over_nu_thr": [2.0]})
    with pytest.raises(ValueError, match="Missing required columns"):
        build_phase_diagram(df, tmp_path / "phase.png")


def test_build_metrics_figure_writes_file(tmp_path: Path) -> None:
    df = pd.DataFrame(
        {
            "panel": ["A", "B", "C", "D"],
            "mean_firing_rate_hz": [10.0, 12.0, 8.0, 7.0],
            "median_cv_isi": [0.4, 0.7, 1.0, 1.1],
            "pairwise_correlation": [0.4, 0.3, 0.1, 0.05],
            "psd_peak_power": [5.0, 4.5, 1.0, 0.8],
        }
    )
    acceptance = {
        "rules": {
            "example": {
                "passed": True,
                "detail": "example detail",
            }
        }
    }
    out_path = tmp_path / "metrics.png"
    build_metrics_figure(df, acceptance, out_path)
    assert out_path.exists()

