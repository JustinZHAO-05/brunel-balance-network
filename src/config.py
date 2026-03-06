from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class AnalysisConfig:
    sample_pair_count: int = 100
    correlation_bin_ms: float = 5.0
    fano_bin_ms: float = 50.0

    @classmethod
    def from_mapping(cls, data: dict[str, Any] | None) -> "AnalysisConfig":
        data = data or {}
        return cls(
            sample_pair_count=int(data.get("sample_pair_count", 100)),
            correlation_bin_ms=float(data.get("correlation_bin_ms", 5.0)),
            fano_bin_ms=float(data.get("fano_bin_ms", 50.0)),
        )

    def validate(self) -> None:
        if self.sample_pair_count <= 0:
            raise ValueError("analysis.sample_pair_count must be positive")
        if self.correlation_bin_ms <= 0:
            raise ValueError("analysis.correlation_bin_ms must be positive")
        if self.fano_bin_ms <= 0:
            raise ValueError("analysis.fano_bin_ms must be positive")


@dataclass
class SimulationConfig:
    name: str
    seed: int
    N_E: int
    gamma: float
    epsilon: float
    tau_m: float
    tau_rp: float
    theta: float
    V_r: float
    J: float
    g: float
    delay: float
    nu_ext_over_nu_thr: float
    dt: float
    sim_time_ms: float
    record_n_neurons: int
    t_range: list[float] | None = None
    rate_range: list[float] | None = None
    rate_tick_step: float | None = None
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "SimulationConfig":
        cfg = cls(
            name=str(data["name"]),
            seed=int(data["seed"]),
            N_E=int(data["N_E"]),
            gamma=float(data["gamma"]),
            epsilon=float(data["epsilon"]),
            tau_m=float(data["tau_m"]),
            tau_rp=float(data["tau_rp"]),
            theta=float(data["theta"]),
            V_r=float(data["V_r"]),
            J=float(data["J"]),
            g=float(data["g"]),
            delay=float(data["delay"]),
            nu_ext_over_nu_thr=float(data["nu_ext_over_nu_thr"]),
            dt=float(data["dt"]),
            sim_time_ms=float(data["sim_time_ms"]),
            record_n_neurons=int(data["record_n_neurons"]),
            t_range=list(data.get("t_range", [])) or None,
            rate_range=list(data.get("rate_range", [])) or None,
            rate_tick_step=float(data["rate_tick_step"]) if data.get("rate_tick_step") is not None else None,
            analysis=AnalysisConfig.from_mapping(data.get("analysis")),
        )
        cfg.validate()
        return cfg

    @property
    def N_I(self) -> int:
        return int(round(self.N_E * self.gamma))

    @property
    def total_neurons(self) -> int:
        return self.N_E + self.N_I

    def validate(self) -> None:
        positive_int_fields = {
            "seed": self.seed,
            "N_E": self.N_E,
            "record_n_neurons": self.record_n_neurons,
        }
        for field_name, value in positive_int_fields.items():
            if value <= 0:
                raise ValueError(f"{field_name} must be positive")

        positive_float_fields = {
            "gamma": self.gamma,
            "tau_m": self.tau_m,
            "tau_rp": self.tau_rp,
            "theta": self.theta,
            "J": self.J,
            "g": self.g,
            "delay": self.delay,
            "nu_ext_over_nu_thr": self.nu_ext_over_nu_thr,
            "dt": self.dt,
            "sim_time_ms": self.sim_time_ms,
        }
        for field_name, value in positive_float_fields.items():
            if value <= 0:
                raise ValueError(f"{field_name} must be positive")

        if not 0 < self.epsilon <= 1:
            raise ValueError("epsilon must be in (0, 1]")
        if self.record_n_neurons > self.total_neurons:
            raise ValueError("record_n_neurons cannot exceed total neuron count")
        if self.t_range is not None and len(self.t_range) != 2:
            raise ValueError("t_range must contain exactly two values")
        if self.rate_range is not None and len(self.rate_range) != 2:
            raise ValueError("rate_range must contain exactly two values")
        self.analysis.validate()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["analysis"] = asdict(self.analysis)
        return data

    def with_overrides(self, overrides: dict[str, Any] | None) -> "SimulationConfig":
        merged = self.to_dict()
        overrides = dict(overrides or {})
        analysis_overrides = overrides.pop("analysis", None)
        merged.update(overrides)
        if analysis_overrides:
            merged["analysis"] = {
                **merged["analysis"],
                **analysis_overrides,
            }
        return SimulationConfig.from_mapping(merged)


@dataclass
class SweepConfig:
    name: str
    base_config: Path
    output_dir: Path
    overrides: dict[str, Any]
    grid: dict[str, list[float]]

    @classmethod
    def from_mapping(cls, data: dict[str, Any], source_path: Path) -> "SweepConfig":
        if "g" not in data["grid"] or "nu_ext_over_nu_thr" not in data["grid"]:
            raise ValueError("sweep grid must define g and nu_ext_over_nu_thr")
        return cls(
            name=str(data["name"]),
            base_config=resolve_repo_path(data["base_config"], source_path.parent),
            output_dir=resolve_repo_path(data["output_dir"], source_path.parent),
            overrides=dict(data.get("overrides", {})),
            grid={
                "g": [float(value) for value in data["grid"]["g"]],
                "nu_ext_over_nu_thr": [float(value) for value in data["grid"]["nu_ext_over_nu_thr"]],
            },
        )


def resolve_repo_path(value: str | Path, relative_to: Path | None = None) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    if str(path).startswith("artifacts/") or str(path).startswith("configs/"):
        return (REPO_ROOT / path).resolve()
    relative_to = relative_to or REPO_ROOT
    candidate = (relative_to / path).resolve()
    if candidate.exists():
        return candidate
    return (REPO_ROOT / path).resolve()


def load_yaml(path: str | Path) -> dict[str, Any]:
    resolved_path = resolve_repo_path(path)
    with resolved_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_simulation_config(path: str | Path) -> SimulationConfig:
    resolved_path = resolve_repo_path(path)
    data = load_yaml(resolved_path)
    return SimulationConfig.from_mapping(data)


def load_sweep_config(path: str | Path) -> SweepConfig:
    resolved_path = resolve_repo_path(path)
    data = load_yaml(resolved_path)
    return SweepConfig.from_mapping(data, resolved_path)


def save_simulation_config(config: SimulationConfig, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(config.to_dict(), handle, sort_keys=False)
