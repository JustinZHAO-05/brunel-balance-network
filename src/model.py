from __future__ import annotations

from pathlib import Path

import numpy as np

from src.config import SimulationConfig, save_simulation_config
from src.io_utils import ensure_dir, save_spikes, write_json, write_population_rate


def run_simulation(config: SimulationConfig, output_dir: str | Path) -> Path:
    from brian2 import (
        Hz,
        NeuronGroup,
        PoissonInput,
        PopulationRateMonitor,
        SpikeMonitor,
        Synapses,
        defaultclock,
        ms,
        mV,
        prefs,
        run,
        seed,
        start_scope,
    )

    output_path = ensure_dir(output_dir)
    prefs.codegen.target = "numpy"
    start_scope()
    np.random.seed(config.seed)
    seed(config.seed)
    defaultclock.dt = config.dt * ms

    n_exc = config.N_E
    n_inh = config.N_I
    total_neurons = config.total_neurons
    c_ext = max(int(round(config.epsilon * n_exc)), 1)
    tau_m = config.tau_m * ms
    tau_rp = config.tau_rp * ms
    theta = config.theta * mV
    reset_potential = config.V_r * mV
    synaptic_jump = config.J * mV
    synaptic_delay = config.delay * ms

    membrane_eq = "dv/dt = -v / tau_m : volt (unless refractory)"
    neurons = NeuronGroup(
        total_neurons,
        membrane_eq,
        threshold="v > theta",
        reset="v = reset_potential",
        refractory=tau_rp,
        method="exact",
        namespace={
            "tau_m": tau_m,
            "theta": theta,
            "reset_potential": reset_potential,
        },
    )
    neurons.v = "reset_potential + rand() * (theta - reset_potential)"

    excitatory = Synapses(
        neurons[:n_exc],
        neurons,
        on_pre="v += j_exc",
        delay=synaptic_delay,
        namespace={"j_exc": synaptic_jump},
    )
    excitatory.connect(condition="i != j", p=config.epsilon)

    inhibitory = Synapses(
        neurons[n_exc:],
        neurons,
        on_pre="v += j_inh",
        delay=synaptic_delay,
        namespace={"j_inh": -config.g * synaptic_jump},
    )
    inhibitory.connect(condition="i != j", p=config.epsilon)

    nu_threshold = theta / (c_ext * tau_m * synaptic_jump)
    nu_ext = config.nu_ext_over_nu_thr * nu_threshold
    external_input = PoissonInput(neurons, "v", c_ext, rate=nu_ext, weight=synaptic_jump)

    population_rate = PopulationRateMonitor(neurons)
    n_recorded = min(config.record_n_neurons, n_exc)
    spike_monitor = SpikeMonitor(neurons[:n_recorded])

    run(config.sim_time_ms * ms)

    save_simulation_config(config, output_path / "config_resolved.yaml")
    save_spikes(
        output_path / "spikes.npz",
        spike_monitor.t / ms,
        spike_monitor.i,
        n_recorded=n_recorded,
        total_neurons=total_neurons,
        sim_time_ms=config.sim_time_ms,
    )
    write_population_rate(output_path / "population_rate.csv", population_rate.t / ms, population_rate.rate / Hz)
    write_json(
        output_path / "run_manifest.json",
        {
            "name": config.name,
            "seed": config.seed,
            "n_exc": n_exc,
            "n_inh": n_inh,
            "total_neurons": total_neurons,
            "n_recorded": n_recorded,
            "sim_time_ms": config.sim_time_ms,
            "external_input_count": c_ext,
        },
    )
    return output_path
