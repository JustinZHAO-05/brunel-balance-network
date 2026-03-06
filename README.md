# Brunel Balance Network

<p align="center">
  <img src="docs/assets/cover.svg" alt="Brunel Balance Network cover" width="100%" />
</p>

<p align="center">
  <a href="https://github.com/JustinZHAO-05/brunel-balance-network/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-0f172a" alt="MIT License" /></a>
  <img src="https://img.shields.io/badge/python-3.10-1d4ed8" alt="Python 3.10" />
  <img src="https://img.shields.io/badge/Brian2-2.7.1-059669" alt="Brian2 2.7.1" />
  <img src="https://img.shields.io/badge/vibe%20coding-Codex%20GPT--5.4-c2410c" alt="Codex GPT-5.4 vibe coding" />
  <img src="https://img.shields.io/github/last-commit/JustinZHAO-05/brunel-balance-network?color=7c3aed" alt="Last commit" />
</p>

一个面向展示的计算神经科学微项目：用 `Brian2` 复现 Brunel 2000 稀疏兴奋/抑制脉冲网络中的经典群体活动状态，并把整个项目的实现过程显式记录为一次 `codex GPT-5.4 vibe coding` 实验。

## What This Repo Shows

- 复现 Brian2 官方 `Brunel_2000` 示例中的 A/B/C/D canonical panels
- 生成单次运行图、四联图、扫参相图和指标对比图
- 通过自动验收规则检验“相对行为是否正确”
- 保留 vibe coding 协议、关键决策和修复记录，便于公开展示与复查

## Core Outputs

- `Figure 1`：四个 canonical panels 的 raster + population rate
- `Figure 2`：`g x nu_ext/nu_thr` 小型相图热图
- `Figure 3`：关键指标 + 自动验收结果
- `artifacts/acceptance.json`：规则级判定结果

## Project Story

这个仓库不是为了追求论文级数值完全一致，而是为了回答一个更实际的问题：

`Codex 能不能在一个真实但可控的计算神经科学任务里，端到端产出能运行、能解释、能展示、能复现的项目？`

当前答案是：可以完成建模、配置、仿真、分析、绘图、测试、仓库管理和开源发布；同时也会真实暴露模型缩放和验收阈值上的不足，而不是用手工修饰把结果伪装成“全部通过”。

## Stack

- `Python 3.10`
- `Brian2 2.7.1`
- `NumPy / SciPy / Matplotlib / Pandas / PyYAML / pytest`

## Quick Start

```bash
python3 -m venv .venv || python3 -m virtualenv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m src.reproduce --preset quick
```

运行完成后可查看：

- `artifacts/reproductions/quick/figure1_panels.png`
- `artifacts/reproductions/quick/figure2_phase_diagram.png`
- `artifacts/reproductions/quick/figure3_metrics.png`
- `artifacts/acceptance.json`

## CLI

```bash
python -m src.simulate --config configs/presets/panel_c.yaml
python -m src.analyze --run-dir artifacts/runs/panel_c
python -m src.sweep --config configs/sweeps/quick.yaml
python -m src.reproduce --preset quick
python -m src.reproduce --preset poster
```

## Repository Layout

- `src/`：仿真、分析、绘图和 CLI
- `configs/`：单次预设和扫参配置
- `artifacts/`：运行结果、图和自动验收文件
- `docs/`：报告、参考资料和 vibe coding 记录
- `tests/`：单元测试与集成测试

## Vibe Coding Record

- 协议：[`docs/vibe_protocol.md`](docs/vibe_protocol.md)
- 日志：[`docs/vibe_log.md`](docs/vibe_log.md)
- 报告：[`docs/report.md`](docs/report.md)

项目主页和仓库文案都明确保留了这个事实：本项目使用 `codex GPT-5.4 vibe coding` 完成。

## References

- Brian2 example: https://brian2.readthedocs.io/en/latest/examples/frompapers.Brunel_2000.html
- Brunel, 2000: https://doi.org/10.1023/A:1008925309027
