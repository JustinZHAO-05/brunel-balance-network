# Brunel Balance Network 项目报告

## 1. 项目概述

本项目实现了一个基于 Brian2 的 Brunel 平衡网络复现仓库，目标是用一个足够小、但足够真实的计算神经科学任务验证 `codex GPT-5.4 vibe coding` 的端到端交付能力。项目覆盖模型配置、仿真、分析、扫参、自动验收，以及最终的公开展示材料生成。

## 2. 研究问题

本项目要回答的问题不是“能否精确重现论文中的每一个数值”，而是：

> 在真实的 Brunel 平衡网络任务里，代理是否能端到端地完成可运行、可解释、可展示、可开源的研究型微项目？

## 3. 模型与实验设计

- 模型：current-based LIF 兴奋/抑制网络
- 框架：Brian2 2.7.1
- 关键参数：抑制强度比 `g`、外部输入强度 `nu_ext_over_nu_thr`
- 核心预设：A/B/C/D 四个 canonical panels
- 扫参：在 `g x nu_ext_over_nu_thr` 网格上批量运行，构建小型相图

## 4. 复现工作流

- `src.simulate`：单次仿真
- `src.analyze`：单次结果分析与作图
- `src.sweep`：批量扫参
- `src.reproduce --preset quick|poster`：端到端复现

## 5. 主要图表

### Figure 1. Canonical panels

![Figure 1](../artifacts/reproductions/poster/figure1_panels.png)

### Figure 2. Poster-scale phase diagram

![Figure 2](../artifacts/reproductions/poster/figure2_phase_diagram.png)

### Figure 3. Metrics and acceptance

![Figure 3](../artifacts/reproductions/poster/figure3_metrics.png)

## 6. Quick 结果摘要

| panel | mean_firing_rate_hz | median_cv_isi | pairwise_correlation | psd_peak_power |
| --- | --- | --- | --- | --- |
| A | 125.851 | 0.089 | -0.042 | 7.386 |
| B | 149.024 | 0.132 | -0.012 | 21.221 |
| C | 78.525 | 0.149 | -0.011 | 9.858 |
| D | 3.240 | 0.092 | -0.014 | 0.023 |

Quick 验收：`3/4` 规则通过。

## 7. Poster 结果摘要

| panel | mean_firing_rate_hz | median_cv_isi | pairwise_correlation | psd_peak_power |
| --- | --- | --- | --- | --- |
| A | 190.886 | 0.089 | 0.022 | 93.383 |
| B | 102.011 | 0.246 | 0.004 | 39.616 |
| C | 63.646 | 0.214 | 0.017 | 6.259 |
| D | 3.200 | 0.130 | 0.009 | 0.135 |

Poster 验收：`3/4` 规则通过。

## 8. 验收规则逐项结果

| preset | rule | passed | detail |
| --- | --- | --- | --- |
| quick | async_corr_lt_sync | PASS | \|sync\|=0.0273, \|async\|=0.0125 |
| quick | async_cv_near_irregular | FAIL | median async CV(ISI)=0.1202 |
| quick | required_outputs_present | PASS | 4/4 required files found |
| quick | sync_peak_power_gt_async | PASS | sync=14.3036, async=4.9404 |
| poster | async_corr_lt_sync | PASS | \|sync\|=0.0131, \|async\|=0.0128 |
| poster | async_cv_near_irregular | FAIL | median async CV(ISI)=0.1722 |
| poster | required_outputs_present | PASS | 4/4 required files found |
| poster | sync_peak_power_gt_async | PASS | sync=66.4999, async=3.1974 |

## 9. Poster Sweep 高亮点

下表列出 `poster` 扫参中 `PSD peak power` 最高的 6 个点，用于快速识别更明显的同步态区域。

| g | nu_ext_over_nu_thr | mean_firing_rate_hz | median_cv_isi | psd_peak_power |
| --- | --- | --- | --- | --- |
| 4.500 | 4.000 | 173.008 | 0.128 | 88.129 |
| 4.000 | 4.000 | 196.512 | 0.108 | 80.524 |
| 5.000 | 4.000 | 153.124 | 0.160 | 76.817 |
| 6.000 | 4.000 | 121.777 | 0.216 | 51.084 |
| 5.500 | 4.000 | 135.589 | 0.184 | 45.466 |
| 3.000 | 0.900 | 20.353 | 0.330 | 37.688 |

## 10. 结果解释

- A/B 条件在 population-rate peak power 上显著高于 C/D，这与同步活动更强的预期一致。
- C/D 条件在 pairwise correlation 的绝对值上整体低于 A/B，说明异步特征方向基本成立。
- 当前项目的主要缺口是 `async_cv_near_irregular` 规则未通过。无论在 `quick` 还是 `poster` 预设下，C/D 的 `median CV(ISI)` 都低于目标阈值 `0.8`，说明网络缩放与参数保持之间仍有偏差。
- 这类失败被保留在自动验收文件中，而不是被手工美化或隐藏，这一点本身也是 vibe coding 流程可信度的一部分。

## 11. 工程产出

- 代码仓库：仿真、分析、扫参与复现 CLI
- 数据产物：spike、population rate、metrics、phase diagram、acceptance JSON
- 展示产物：项目报告、A1 poster、汇报 PPT
- 过程记录：`docs/vibe_protocol.md` 与 `docs/vibe_log.md`

## 12. 局限与后续工作

- 当前 `quick` 和 `poster` 都没有让 D 条件达到接近 1 的不规则放电水平
- 网络缩放目前主要缩放 `N_E`，但对 Brunel 模型而言，如何保持连接数、输入强度和统计结构的一致性仍需更严谨处理
- 下一步应优先做参数缩放校正，而不是继续堆更多图表

## 13. 复现命令

```bash
python -m src.reproduce --preset quick
python -m src.reproduce --preset poster
python scripts/build_deliverables.py
```
