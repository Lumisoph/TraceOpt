# 项目导航

## 当前入口

- 当前轮次：iter_024；阶段：planning；角色：Planner。
- 机器入口：[state.yaml](.traceopt/state.yaml)；流程：[workflow.yaml](.traceopt/workflow.yaml)。
- [计划](iterations/iter_024/PLAN.md) · [开发报告](iterations/iter_024/DEV_REPORT.md) · [QA 报告](iterations/iter_024/QA_REPORT.md)。
- 第十二轮已收尾；0.1.0 分发包与包内源码身份验证通过。

## 核心文档

| 文档 | 用途 | 读取时机 |
|---|---|---|
| [AGENTS.md](AGENTS.md) | 长期规则与恢复协议 | 启动 |
| [REQUIREMENTS.md](REQUIREMENTS.md) | 稳定需求 | 规划、QA |
| [PROJECT_STATE.md](PROJECT_STATE.md) | 当前事实快照 | 每个角色 |
| [RELEASE_CRITERIA.md](RELEASE_CRITERIA.md) | 发布完成定义 | 里程碑规划 |
| [IMPACT_MAP.md](IMPACT_MAP.md) | 修改影响 | 实现前 |
| [CLAIMS.md](CLAIMS.md) | 对外声明边界 | README、简历 |
| [CHANGELOG.md](CHANGELOG.md) | 历史变更 | 回溯 |
| [RELEASE_HANDOFF.md](RELEASE_HANDOFF.md) | 发布交接 | 发布候选 |

## 模块与历史

| 主题 | 入口 | 读取时机 |
|---|---|---|
| 架构概览 | [overview](docs/architecture/overview.md) | 理解模块职责 |
| 事件表示 | [canonical_ir](docs/architecture/canonical_ir.md) | 轨迹、schema |
| 命令语义 | [command_semantics](docs/architecture/command_semantics.md) | Bash 解析 |
| 读写效果 | [effects](docs/architecture/effects.md) | 路径与副作用 |
| 依赖 | [dependency](docs/architecture/dependency.md) | RAW/WAR/WAW |
| 运行时绑定 | [runtime_binding](docs/architecture/runtime_binding.md) | 循环检测 |
| 确定性 | [determinism](docs/architecture/determinism.md) | 前缀可见性 |
| 改写 | [rewrite](docs/architecture/rewrite.md) | 可执行优化 |
| 重放 | [replay](docs/architecture/replay.md) | 状态比较 |
| 评估 | [evaluation](docs/architecture/evaluation.md) | 指标、实验 |
| 决策 | [ADR 索引](docs/decisions/INDEX.md) | 设计原因 |
| 面试材料 | [面试索引](docs/interview/INDEX.md) | 解释与复盘 |
| 实验记录 | [实验索引](docs/experiments/INDEX.md) | 证据追踪 |
| 迭代 | [迭代索引](iterations/INDEX.md) | 交接与恢复 |
| 正式数字 | [注册表](results/registry.yaml) | 对外引用 |
| 输入数据 | [数据说明](data/README.md) | 样本定位 |

## 待确认事项

当前无 OPEN 缺陷；GPT 适配和分发包均已通过 QA，生产模型正例仍不足。
最新发布候选证据：[iter_019 QA](iterations/iter_019/QA_REPORT.md)。

iter_013 的 QA 失败与缺陷记录仅为历史证据；iter_014 已验证修复，当前轮不应将历史失败当作现状。

## 明确边界

以上声明只覆盖各自列出的验证范围。trajectory parsing、tool replay 与 LLM conversation replay 是三个不同对象；当前没有 LLM 调用、采样复现或完整模型会话重放证据。























