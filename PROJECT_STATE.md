# 当前项目状态

## 当前里程碑

M4 可执行改写和重放已完成受限验证，受控评估已登记。当前 iter_024 / qa。iter_023 最终发布候选回归已通过 QA。iter_022 v0.1.0 发布交接清单与哈希证据已通过 QA。iter_021 v0.1.0 发布审计与外部边界已通过 QA。iter_020 权威快照可读性与证据指向已通过 QA。iter_019 发布候选证据与文档完整性已通过 QA。
iter_008 Full Gate、iter_009 职业材料、iter_010 发布审计、iter_014 Responses 适配和 iter_017 发布候选检查均已有历史 QA 证据；本轮不新增产品能力。
机器入口：[state.yaml](.traceopt/state.yaml)。

## 当前事实

- mini-swe-agent-1.1 结构化 bash 轨迹读取与不可变事件 IR 已在固定真实来源（含 GPT Responses API）上验证。
- 固定 GPT Responses `response/output/function_call/function_call_output` 结构已支持；未知 item、流式和并行语义拒绝。
- 命令白名单提取词法 POSIX 读写 Effect，RAW/WAR/WAW 附路径见证；unknown 为全局屏障。
- CLI 提供 inspect/export/analyze；上下文需显式提供，不能自动恢复动态 cwd。
- NUL find 来源支持前缀绑定计划与连续消费结构匹配；前缀构造不读取未来信息。
- 受限 cat 可生成可执行 Bash 批处理，实际比对原始/优化/历史记录及仓库状态。
- 人工循环挑战集已建立三方法比较与实际重放，原始产物、配置和代码哈希可追溯。
- Python 产品运行时无第三方依赖；重放需要可信本机 Bash/cat/find。当前目录不是 Git 工作树，版本身份使用 SHA-256。

## 能力快照

| 能力 | 状态 | 证据与限制 |
|---|---|---|
| 轨迹读取 | VERIFIED_FULL | iter_014 QA；固定真实来源与 Responses 适配范围 |
| Canonical Event IR | VERIFIED_FULL | iter_014 QA；保序、关联与 pending |
| CLI | VERIFIED_LOCAL | iter_010 QA；inspect/export/analyze |
| 命令语义 | VERIFIED_FULL | iter_004 QA；明确词法支持矩阵 |
| 读写 Effect | VERIFIED_FULL | iter_004 QA；路径子树模型 |
| RAW/WAR/WAW | VERIFIED_FULL | iter_004 QA；未知调用屏障 |
| 运行时绑定 | VERIFIED_LOCAL | iter_007 QA；受限 NUL 枚举与单文件模板 |
| 前缀可见确定性 | VERIFIED_LOCAL | iter_007 QA；不证明未来 LLM 意图 |
| 可执行改写 | VERIFIED_LOCAL | iter_006 QA；受限 cat 批处理 |
| 重放 | VERIFIED_LOCAL | iter_006 QA；普通无别名仓库、逐项结果与历史 |
| 评估 | VERIFIED_FULL | iter_008 QA；人工受控挑战集 |
| 发布包 | VERIFIED_FULL | iter_019 QA；独立环境构建、安装与源码身份检查 |

## 最新验证与缺陷

[iter_014 QA](iterations/iter_014/QA_REPORT.md) 验证了 Responses 适配；[iter_019 QA](iterations/iter_019/QA_REPORT.md) 记录了最新发布候选检查。BUG-001、BUG-002 均为 `VERIFIED_FIXED`，当前无 OPEN 缺陷。iter_013 的失败报告保留为历史证据，不代表当前状态。

## 已验证实验与声明

[EXP-002](docs/experiments/EXP-002-controlled-loops.md) 已写入 [注册表](results/registry.yaml)，正式数字仅引用 `status: verified` 条目。[CLAIM-001/002/003](CLAIMS.md) 规定对外表述边界。

## 限制和剩余工作

词法模型不覆盖文件别名、环境副作用和并发修改；无边不等于可以安全执行。前缀计划不证明未来 LLM 意图，受控重放不代表任意 Bash 或整个模型会话的等价。人工挑战集非独立留出样本，不支持生产精度、模型成本或速度收益。

iter_018 至 iter_023 已完成文档修复、发布候选重建、独立环境验证、状态快照清理、发布审计、交接清单和最终回归；下一轮由 Planner 根据最新证据确定是否仍有发布阻塞。

## 复现入口

- 完整检查：`python -m pytest -q`、`python -m ruff check .`
- 受控重放：`examples/replay_demo.py`
- 受控评估：`experiments/evaluate.py configs/eval_v1.json <new-output-dir>`
- 证据注册表：[results/registry.yaml](results/registry.yaml)

## 对外边界

当前验证对象依次为 trajectory parsing、受限 tool replay 和状态比较；LLM conversation replay（模型调用、采样与完整会话再生成）尚未实现或验证。不得把工具重放证据表述为任意 Bash 正确性或模型成本下降。



















