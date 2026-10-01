# 修改影响图

Developer 修改前必读；以下是职责映射，模块和测试尚未实现时不得假称已有对应回归。
具体路径与命令由当前 PLAN 写明，模块落地后更新此表。

| 修改范围 | 必须检查 | 必需回归 |
|---|---|---|
| Canonical IR | 适配器、检测器、重放 | 适配器、集成、Full Gate |
| Bash 语义 | Effect、依赖 | 语义与 Effect |
| Effect 模型 | 依赖、检测器 | Effect、依赖、候选检测 |
| 依赖核心 | 并行与循环检测 | 依赖、候选、Full Gate |
| 运行时绑定 | 确定性 | 绑定、确定性 |
| 确定性 | 改写 | 检测器、对抗案例 |
| 改写 | 重放 | 改写、重放 |
| 重放状态 | 验证器 | 重放集成、Full Gate |
| 指标 | 实验与报告 | 评估、分母与空集边界 |
| 工作流规则 | 提示词、机器状态、索引 | 状态合法性、路径、交接一致性 |

## 当前已落地路径

Canonical IR 与轨迹适配集中于 `src/traceopt/trajectory.py`。
对应回归为 `tests/test_trajectory.py` 和 `tests/test_trajectory_integration.py`。
重放现由受限 cat 执行器提供，不能推广到任意命令。

CLI 位于 `src/traceopt/cli.py`，对应 `tests/test_cli.py`；修改输出结构需验证 JSON 契约与文件不覆盖约束。

语义与 Effect 位于 `src/traceopt/semantics.py`；回归为 `tests/test_semantics.py`，未来依赖需满足其路径子树契约。

依赖位于 `src/traceopt/dependency.py`；回归为 `tests/test_dependency*.py` 与 analyze CLI。修改需运行 Full Gate 与依赖挑战集。

绑定检测位于 `src/traceopt/binding.py`；回归 `tests/test_binding*.py`，必须验证前缀与未来信息隔离。

改写与重放位于 `src/traceopt/replay.py`；回归 `tests/test_replay*.py` 和 `examples/replay_demo.py`，必须执行 Full Gate。

评估位于 `src/traceopt/evaluation.py`；回归 `tests/test_evaluation.py`、循环挑战集、独立复跑与原始指标重算。
