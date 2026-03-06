# Brunel 平衡网络复现报告

## 摘要

本项目使用 Brian2 实现 current-based LIF 兴奋/抑制平衡网络，并复现 Brunel 2000 中的几类典型群体活动状态。重点不在于追求论文级完全数值一致，而在于验证一套由代理主导的 vibe coding 工作流，是否能稳定地产出可复现实验、图表和自动验收结果。

## 模型

- 网络由兴奋性与抑制性 LIF 神经元构成
- 突触连接为稀疏随机连接
- 外部驱动使用 Poisson 输入
- 关键控制参数为抑制强度比 `g` 和外部输入强度 `nu_ext_over_nu_thr`

## 产物说明

- Figure 1：四个 canonical panels 的 raster 和 population rate
- Figure 2：`g x nu_ext_over_nu_thr` 小网格扫参热图
- Figure 3：关键指标和自动验收结果
- `artifacts/acceptance.json`：规则级别的程序化判断

## 解释框架

- A/B 预期更偏同步活动，因此 population-rate 振荡峰更突出
- C/D 预期更偏低相关与不规则放电，因此 pairwise correlation 更低，CV(ISI) 更接近 1
- 若相对关系成立，即认为复现达到了“行为正确”的目标

## 复现命令

```bash
python -m src.reproduce --preset quick
python -m src.reproduce --preset poster
```
