# Brunel Balance Network Microproject

一个用于验证 `vibe coding` 能力的计算神经科学微项目。项目使用 `Brian2` 复现 Brunel 2000 稀疏兴奋/抑制网络中的几种经典放电状态，并提供从仿真、分析、扫参到自动验收的一条龙流水线。

## 项目目标

- 复现 Brian2 官方 `Brunel_2000` 示例中的 A/B/C/D 四个 canonical panels
- 生成单次运行图、四联图、扫参相图和指标对比图
- 用自动验收规则判断结果是否符合“相对行为正确”
- 显式记录 vibe coding 任务定义、实施过程和修复决策

## 技术栈

- Python 3.10
- Brian2 2.7.1
- NumPy / SciPy / Matplotlib / Pandas / PyYAML / pytest

`Brian2` 新版本的 Python 兼容范围变化较快，这里固定到 `2.7.1`，以适配当前环境中的 `Python 3.10.12`。

## 目录结构

- `src/`：仿真、分析、绘图和 CLI
- `configs/`：单次预设和扫参配置
- `artifacts/`：生成的运行结果、图和验收文件
- `docs/`：报告、参考资料和 vibe coding 记录
- `tests/`：单元测试和集成测试

## 快速开始

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

运行单个 canonical panel：

```bash
python -m src.simulate --config configs/presets/panel_c.yaml
python -m src.analyze --run-dir artifacts/runs/panel_c
```

运行小型扫参：

```bash
python -m src.sweep --config configs/sweeps/quick.yaml
```

生成完整快速复现：

```bash
python -m src.reproduce --preset quick
```

## 主要产物

- `artifacts/runs/<name>/spikes.npz`
- `artifacts/runs/<name>/population_rate.csv`
- `artifacts/runs/<name>/metrics.json`
- `artifacts/runs/<name>/raster.png`
- `artifacts/runs/<name>/rate_trace.png`
- `artifacts/runs/<name>/summary.png`
- `artifacts/reproductions/<preset>/figure1_panels.png`
- `artifacts/reproductions/<preset>/figure2_phase_diagram.png`
- `artifacts/reproductions/<preset>/figure3_metrics.png`
- `artifacts/acceptance.json`

## 参考

- Brian2 official example: https://brian2.readthedocs.io/en/latest/examples/frompapers.Brunel_2000.html
- Brunel, 2000: https://doi.org/10.1023/A:1008925309027
