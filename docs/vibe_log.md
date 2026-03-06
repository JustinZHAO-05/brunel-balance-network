# Vibe Coding Log

## 初始任务

基于 Brunel 2000 平衡网络构建一个小型研究仓库，展示经典兴奋/抑制平衡网络状态，并将 vibe coding 过程本身做成可检查的交付物。

## 关键决策

- 选择 `Brian2` 而不是训练型 SNN 框架，保持项目聚焦在计算神经科学动力学复现
- 采用 A/B/C/D canonical panels，对齐 Brian2 官方 `Brunel_2000` 示例
- 将验收规则设计为“相对行为正确”，避免把平台差异放大成虚假的失败
- `quick` 和 `poster` 分为开发复现模式与展示复现模式，解决运行时间和展示强度之间的冲突

## 风险与缓解

- 风险：Brian2 新版本与 Python 3.10 兼容性不稳定
- 缓解：固定 `Brian2==2.7.1`

- 风险：完整 Brunel 网络运行时间过长
- 缓解：`quick` 模式缩小网络规模，`poster` 模式保留更高保真度

- 风险：同步/异步状态在不同随机种子下边界漂移
- 缓解：使用多条相对验收规则，而不是单一绝对数值

## 后续记录

实现与验证过程中产生的新问题、失败尝试和修复决策，应继续追加在本文件中。

## 本次实现记录

- 标准 `python -m venv` 在当前机器上失败，因为系统缺少 `ensurepip`；改用 `virtualenv` 创建 `.venv`
- 默认 `quick` 模式的第一次实现出现全静默，原因是外部 `PoissonInput` 没有显式绑定对象；修复后恢复正常放电
- 扫参配置最初存在相对路径解析错误，导致 `configs/sweeps/*.yaml` 无法正确引用 `configs/presets/*.yaml`
- 默认 `quick` 复现当前可稳定生成 Figure 1/2/3 和 `artifacts/acceptance.json`
- 当前默认 `quick` 在验收上通常只能通过同步功率和输出完整性，异步不规则性的规则仍偏严格，这一结果被保留在 `artifacts/acceptance.json` 中作为真实记录
