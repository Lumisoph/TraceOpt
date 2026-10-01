# iter_004 QA 报告

状态：completed。结论：passed。Gate：full。由同一会话按角色阶段执行。

## 身份与环境

Python 3.13.5、Windows、项目 .venv，工作目录 G:/Advance_tool_mining/TraceOpt。
[执行记录与源码/挑战集哈希](evidence/qa_execution.json) 保存命令、退出码、时间与身份。
QA 核对开发交付哈希一致，仅新增 QA 测试，未修改产品实现。

## 验收结果

| 编号 | 结果 | 证据 |
|---|---|---|
| AC-401 | 通过 | 所有冲突类型、路径见证、空输入、稳定去重和前向边测试 |
| AC-402 | 通过 | 子树、根、相似前缀、.. 前提、unknown 全局屏障 |
| AC-403 | 通过 | 真实固定样本映射；缺失 cwd 为 unknown，多余 ID 拒绝，pending 调用保留 |
| AC-404 | 通过 | CLI 与 API 对齐、已知 RAW、未知屏障、中文错误和输出不覆盖 |
| AC-405 | 通过 | 40 个手工标注依赖案例全量验证，标签有独立说明 |

## Full Gate 实际执行

- 完整 pytest：189 passed，退出码 0，[日志](evidence/qa_pytest.log)。
- 真实依赖集成：2 passed，退出码 0，[日志](evidence/qa_integration.log)。
- 挑战集：40 个案例及 1 个完整性检查，41 passed，退出码 0，[日志](evidence/qa_challenges.log)。
- Ruff：通过，退出码 0，[日志](evidence/qa_ruff.log)。
- analyze CLI：通过，退出码 0，[日志](evidence/qa_cli.log)；inspect/export 在完整测试中回归。
- [依赖环境](evidence/qa_environment.log)。所有准确命令见执行记录。

QA 额外检查未来调用不改变前缀边、屏障路径不可跨越、中文相似目录前缀不产生假边。
完整 Full Gate 已执行，无跳过项；结论仅覆盖当前词法资源依赖模型。

## 能力边界与声明

dependency 为 VERIFIED_FULL：支持 RAW/WAR/WAW、资源子树重叠、unknown 屏障和来源映射。
已有命令语义与 Effect 经完整回归及依赖挑战覆盖，在既定支持矩阵内为 VERIFIED_FULL。
CLI 修改通过，保持 VERIFIED_LOCAL；尚无优化/重放等后续子命令。
不声称恢复任意 Bash 依赖，不证明独立调用可安全并行；环境与文件别名假设仍需重放验证。
挑战集是依赖标签，不替代端到端优化标签、基线、精确率/召回率或重放成功率。
本轮没有性能实验，不修改结果注册表。未发现可复现缺陷。

## 结构化同步结论

```yaml
iteration: 4
verdict: passed
gate: full
capabilities:
  command_semantics: VERIFIED_FULL
  effects: VERIFIED_FULL
  dependency: VERIFIED_FULL
  cli: VERIFIED_LOCAL
defects: []
experiments: {}
claims:
  - id: CLAIM-001
    status: VERIFIED_FULL
    claim: 基于文件读写 Effect 构建带资源证据的 RAW/WAR/WAW 依赖，并保守处理未知调用。
    scope: 显式 POSIX 工作目录、普通路径子树模型；不覆盖文件别名、环境副作用及控制依赖。
    evidence: [tests/test_dependency.py, tests/test_dependency_integration.py, tests/test_dependency_challenges.py, iterations/iter_004/QA_REPORT.md]
    allowed: 在明确的路径模型假设下，实现带资源证据的工具调用依赖分析与未知调用屏障。
    forbidden: 完整恢复任意 Bash 程序依赖，或仅凭无依赖边证明可安全并行。
```
