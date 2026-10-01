# iter_006 QA 报告

状态：completed。结论：passed。执行 Full Gate，新增执行能力限定 VERIFIED_LOCAL。

## 身份与环境

Python 3.13.5、Windows、项目 .venv，实际使用本机 Git Bash/cat/find。
工作目录：G:/Advance_tool_mining/TraceOpt。
[执行记录](evidence/qa_execution.json) 保存命令、退出码、源码/测试/数据和产物哈希。
QA 核对开发文件身份一致；仅新增 tests/test_replay_qa.py，未修改实现。

## 验收结果

| 编号 | 结果 | 证据 |
|---|---|---|
| AC-601 | 通过 | 真正运行逐项 cat 和 Bash 批处理，stdout/stderr/退出码逐项相同 |
| AC-602 | 通过 | 源不变，初始/原始/优化快照一致，覆盖目录、字节哈希、权限、mtime 与只读文件 |
| AC-603 | 通过 | 实际硬链接与 Windows junction 拒绝；伪造计划、越界、非 cat、.. 和缺失记录拒绝 |
| AC-604 | 通过 | 实际 find/cat 捕获 → 轨迹加载 → 检测 → 原始与优化重放成功 |
| AC-605 | 通过 | 历史不符为 unsuccessful；枚举变化拒绝；实际超时终止，工具缺失报错 |

## Full Gate

- 完整 pytest：252 passed，退出码 0，[日志](evidence/qa_pytest.log)。
- 实际重放集成：1 passed，退出码 0，[日志](evidence/qa_integration.log)。
- 依赖挑战集：41 项检查通过，退出码 0，[日志](evidence/qa_challenges.log)。
- Ruff（src/tests/examples）：通过，退出码 0，[日志](evidence/qa_ruff.log)。
- analyze CLI：通过，退出码 0，[日志](evidence/qa_cli.log)。
- 可复现演示：successful=true，退出码 0，[日志](evidence/qa_demo.log)。

准确命令见执行记录。QA 对抗检查包括真实 junction 和 BASH_ENV 启动注入，均未绕过约束。
Full Gate 无跳过项；范围为已有模型与受控 cat 候选片段。

## 保存的执行证据

- [实际捕获轨迹](evidence/live_capture/capture.traj.json)
- [初始仓库](evidence/live_capture/initial_repo)
- [可执行改写](evidence/live_capture/rewrite.sh)
- [完整报告](evidence/live_capture/report.json)

报告经核对：equivalent、state_unchanged、matches_recording、successful 均为 true。
真实工具捕获是受控实验输入，不是生产模型的自动决策；没有据此计算 LLM 成本收益。
工具边界计数仅说明批处理形式。没有正式性能实验注册项。

## 判定边界

rewrite/replay 为 VERIFIED_LOCAL，限单文件 cat 循环、显式虚拟根、普通无别名仓库。
新增可执行正例支持该模式实际运行，但不扩大至所有绑定模板或任意 Bash。
没有发现可复现缺陷；错误历史、链接、目录变化、工具缺失、超时均未误记为通过。

## 结构化同步结论

```yaml
iteration: 6
verdict: passed
gate: full
capabilities:
  rewrite: VERIFIED_LOCAL
  replay: VERIFIED_LOCAL
defects: []
experiments: {}
claims:
  - id: CLAIM-003
    status: VERIFIED_LOCAL
    claim: 对受限 cat 循环生成可执行批处理，并比较原始和优化执行的逐项结果及仓库状态。
    scope: 受控真实工具执行，单文件 cat 模板、明确初始状态与无别名普通路径；不是模型端到端成本实验。
    evidence: [tests/test_replay.py, tests/test_replay_integration.py, tests/test_replay_qa.py, iterations/iter_006/QA_REPORT.md, iterations/iter_006/evidence/live_capture/report.json]
    allowed: 在受限读取循环上，通过实际重放核对逐项输出、退出码、历史记录和仓库状态。
    forbidden: 证明任意 Bash 优化正确，或宣称已经测得模型调用成本下降。
```
