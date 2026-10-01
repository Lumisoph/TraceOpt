# 架构索引

Canonical IR 与轨迹读取在固定真实来源上已获 iter_014 的 VERIFIED_FULL；命令语义、Effect 与依赖已获 iter_004 的 VERIFIED_FULL（词法模型范围内），绑定和前缀计划获 iter_005 的 VERIFIED_LOCAL，改写和重放获 iter_006 的 VERIFIED_LOCAL，评估获 iter_008 的 VERIFIED_FULL（人工受控挑战集范围内）。
文档中的设计目标不代表已有实现。

| 模块 | 文档 | 需求 |
|---|---|---|
| 架构概览 | [overview](overview.md) | REQ-001 至 REQ-014 |
| 规范事件表示 | [canonical_ir](canonical_ir.md) | REQ-001、REQ-002 |
| 命令语义 | [command_semantics](command_semantics.md) | REQ-003 |
| 读写效果 | [effects](effects.md) | REQ-004 |
| 执行依赖 | [dependency](dependency.md) | REQ-005 |
| 运行时绑定 | [runtime_binding](runtime_binding.md) | REQ-006 |
| 前缀可见确定性 | [determinism](determinism.md) | REQ-007 |
| 可执行改写 | [rewrite](rewrite.md) | REQ-008 |
| 执行重放 | [replay](replay.md) | REQ-009 |
| 评估 | [evaluation](evaluation.md) | REQ-010、REQ-011 |

