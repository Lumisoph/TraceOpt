# TraceOpt v0.1 发布条件

每项勾选必须附 QA 报告或已验证实验的路径，不能仅凭实现存在勾选。

## 核心能力

- [x] 真实 mini-swe-agent 轨迹读取（REQ-001） — [iter_010 QA](iterations/iter_010/QA_REPORT.md)，限报告声明范围
- [x] Canonical Event IR（REQ-002） — [iter_010 QA](iterations/iter_010/QA_REPORT.md)，限报告声明范围
- [x] 至少 10 种明确支持的 Bash 命令形式（REQ-003） — [iter_004 QA](iterations/iter_004/QA_REPORT.md)，限已声明词法模型
- [x] 读写 Effect 提取（REQ-004） — [iter_004 QA](iterations/iter_004/QA_REPORT.md)，限已声明词法模型
- [x] RAW/WAR/WAW（REQ-005） — [iter_004 QA](iterations/iter_004/QA_REPORT.md)，限已声明词法模型
- [x] 运行时绑定循环检测（REQ-006） — [iter_010 QA](iterations/iter_010/QA_REPORT.md)，限报告声明范围
- [x] 前缀可见确定性（REQ-007） — [iter_010 QA](iterations/iter_010/QA_REPORT.md)，限报告声明范围
- [x] 至少一种可执行改写（REQ-008） — [iter_006 QA](iterations/iter_006/QA_REPORT.md)，限受控 cat 片段
- [x] 原始与优化重放（REQ-009） — [iter_006 QA](iterations/iter_006/QA_REPORT.md)，限受控 cat 片段
- [x] 仓库状态验证（REQ-009） — [iter_006 QA](iterations/iter_006/QA_REPORT.md)，限受控 cat 片段

## 评估

- [x] 至少 40 个标注挑战案例 — [iter_008 QA](iterations/iter_008/QA_REPORT.md)、[EXP-002](docs/experiments/EXP-002-controlled-loops.md)，限人工受控案例
- [x] 朴素基线 — [iter_008 QA](iterations/iter_008/QA_REPORT.md)、[EXP-002](docs/experiments/EXP-002-controlled-loops.md)，限人工受控案例
- [x] Precision / Recall / F1 — [iter_008 QA](iterations/iter_008/QA_REPORT.md)、[EXP-002](docs/experiments/EXP-002-controlled-loops.md)，限人工受控案例
- [x] 重放成功率 — [iter_008 QA](iterations/iter_008/QA_REPORT.md)、[EXP-002](docs/experiments/EXP-002-controlled-loops.md)，限人工受控案例
- [x] 一项依赖消融 — [iter_008 QA](iterations/iter_008/QA_REPORT.md)、[EXP-002](docs/experiments/EXP-002-controlled-loops.md)，限人工受控案例
- [x] 至少 4 个已记录失败案例 — [iter_008 QA](iterations/iter_008/QA_REPORT.md)、[EXP-002](docs/experiments/EXP-002-controlled-loops.md)，限人工受控案例

## 工程

- [x] 完整 pytest 通过 — [iter_010 QA](iterations/iter_010/QA_REPORT.md)，限报告声明范围
- [x] Ruff 通过 — [iter_010 QA](iterations/iter_010/QA_REPORT.md)，限报告声明范围
- [x] CLI 可用 — [iter_010 QA](iterations/iter_010/QA_REPORT.md)，限报告声明范围
- [x] README 可复现 — [iter_010 QA](iterations/iter_010/QA_REPORT.md)，限报告声明范围
- [x] 已验证结果注册表 — [iter_008 QA](iterations/iter_008/QA_REPORT.md)、[EXP-002](docs/experiments/EXP-002-controlled-loops.md)，限人工受控案例

## 面试材料

- [x] 3 条可用证据支撑的简历表述 — [iter_009 QA](iterations/iter_009/QA_REPORT.md)
- [x] 3 分钟面试讲解 — [iter_009 QA](iterations/iter_009/QA_REPORT.md)
- [x] 至少 30 个面试问题 — [iter_009 QA](iterations/iter_009/QA_REPORT.md)

全部满足后停止扩展新功能，进行 v0.1 发布。
