# TraceOpt v0.1.0 发布审计

状态：本地发布候选已完成审计；源码已发布到 GitHub main。

本文件只报告当前工作区可复现的证据。`VERIFIED_FULL`、`VERIFIED_LOCAL` 和 `verified` 的含义沿用 [AGENTS.md](../AGENTS.md)；受限能力不得扩大解释。

## 需求与证据映射

| 需求 | 当前证据 | 适用范围 |
|---|---|---|
| REQ-001/002 轨迹与 Canonical IR | [iter_014 QA](../iterations/iter_014/QA_REPORT.md)、[trajectory tests](../tests/test_trajectory_integration.py)、[Responses tests](../tests/test_response_qa.py) | 固定真实来源与已声明 Responses 结构 |
| REQ-003/004 命令语义与 Effect | [iter_004 QA](../iterations/iter_004/QA_REPORT.md)、[语义测试](../tests/test_semantics.py)、[支持矩阵](architecture/command_semantics.md) | 白名单词法 POSIX 模型 |
| REQ-005 依赖 | [iter_004 QA](../iterations/iter_004/QA_REPORT.md)、依赖单元/集成/挑战测试 | RAW/WAR/WAW 与 unknown 屏障 |
| REQ-006/007 绑定与前缀确定性 | [iter_007 QA](../iterations/iter_007/QA_REPORT.md)、绑定 QA 测试 | NUL 枚举与受限单文件模板；不证明未来 LLM 意图 |
| REQ-008/009 改写、重放与状态 | [iter_006 QA](../iterations/iter_006/QA_REPORT.md)、[重放集成测试](../tests/test_replay_integration.py)、[iter_019 证据](../iterations/iter_018/evidence/replay-demo/report.json) | 受限 cat、明确初始状态、可信本机工具 |
| REQ-010/011 评估、基线、消融与失败 | [EXP-002](experiments/EXP-002-controlled-loops.md)、[结果注册表](../results/registry.yaml) | 45 个人工受控案例，数字仅以 `status: verified` 为准 |
| REQ-012 工程与复现 | [iter_019 QA](../iterations/iter_019/QA_REPORT.md)、[README](../README.md)、[发布证据](../iterations/iter_019/evidence) | Windows 本地环境与当前 Python 版本证据 |
| REQ-013 面试材料 | [iter_009 QA](../iterations/iter_009/QA_REPORT.md)、[面试索引](interview/INDEX.md)、[声明](../CLAIMS.md) | 只使用有证据和限制的表述 |
| REQ-014 持久工作台 | [状态入口](../.traceopt/state.yaml)、[流程](../.traceopt/workflow.yaml)、[iter_020 QA](../iterations/iter_020/QA_REPORT.md) | 角色交接、状态枚举和证据链 |

## 当前发布候选证据

- 版本：`pyproject.toml` 中为 `0.1.0`。
- 构建：`python -m build` 成功生成 wheel/sdist；文件哈希和源码身份见 [iter_019 evidence](../iterations/iter_019/evidence)。
- 安装：独立 `.venv-release-019` 安装 wheel 后，CLI、完整 pytest（333 passed）和 Ruff 通过。
- 最新工作区回归：iter_020 QA 记录 334 passed、Ruff、CLI 和状态快照对抗检查通过。
- 结果：EXP-002 已在注册表中标记 `verified`；不代表生产分布、模型成本或端到端收益。

## 远程发布事实与边界

源码仓库：[Lumisoph/TraceOpt](https://github.com/Lumisoph/TraceOpt)，首次发布提交
`881c38a688da9245637b381c67e0949c98d9bf87` 已通过远程 main 哈希核对。
原始工作区不是 Git 工作树，发布使用独立克隆。
新克隆独立环境复现证据见 [iter_024 QA](../iterations/iter_024/QA_REPORT.md)。
未创建 GitHub Release、未上传安装包或发布 PyPI；不能用源码发布声称这些动作已完成。

## 不能由本审计推出的结论

TraceOpt 不支持任意 Bash 语义恢复、LLM conversation replay、模型采样复现、全数据集兼容或模型成本下降结论。未知命令、副作用、文件别名、并发和不确定外部状态仍按保守拒绝处理。

## 相关入口

- [发布条件](../RELEASE_CRITERIA.md)
- [当前状态](../PROJECT_STATE.md)
- [结果注册表](../results/registry.yaml)
- [对外声明](../CLAIMS.md)

