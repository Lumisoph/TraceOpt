# iter_005 QA 报告

状态：completed。结论：passed。执行 Full Gate，新增能力仍限定 VERIFIED_LOCAL。

## 环境与身份

Python 3.13.5、Windows、项目 .venv，工作目录 G:/Advance_tool_mining/TraceOpt。
[执行记录](evidence/qa_execution.json) 含命令、退出码、日志、时间、源码/测试/挑战集哈希。
QA 核对开发交付文件未变，仅增加 tests/test_binding_qa.py；未修改实现。

## 验收

| 编号 | 结果 | 证据 |
|---|---|---|
| AC-501 | 通过 | 冻结计划、来源位置、多路径、模板和绑定来源核对 |
| AC-502 | 通过 | 替换未来命令、输出、哈希、上下文和前缀截断后计划不变；禁止读取未来 cwd 的映射测试 |
| AC-503 | 通过 | 失败/未知生产者、空/重复/截断/越界/危险路径、缺少上下文及未完成/冲突前序拒绝 |
| AC-504 | 通过 | 同序匹配接受，缺失、换序、改常量、插入工具或用户指令拒绝 |
| AC-505 | 通过 | find -print0 Effect 一致性，完整语义、依赖及 CLI 回归 |

## 实际检查

- 完整 pytest：231 passed，退出码 0，[日志](evidence/qa_pytest.log)。
- 绑定集成：2 passed，退出码 0，[日志](evidence/qa_integration.log)。
- 依赖挑战集：41 项检查通过，退出码 0，[日志](evidence/qa_challenges.log)。
- Ruff：通过，退出码 0，[日志](evidence/qa_ruff.log)。
- analyze CLI：通过，退出码 0，[日志](evidence/qa_cli.log)。

准确命令见执行记录；Full Gate 无跳过项。
QA 额外验证未来上下文未被读取、新用户指令打断、未完成的中间调用为屏障。

## 能力与限制

runtime_binding 和 determinism 为 VERIFIED_LOCAL，覆盖 NUL 路径枚举与单文件只读模板。
本轮“确定性”指前缀内计划构造及参数来源，不证明 LLM 将来必定选择这些命令。
正例为人工轨迹，经真实加载器解析；固定真实样本无匹配候选，此项仅支持不误报结论。
已修改的 find 语义与 Effect 经完整回归恢复 VERIFIED_FULL，仍限其词法模型。
没有执行、重放或性能收益实验，未发现可复现缺陷。

## 结构化同步结论

```yaml
iteration: 5
verdict: passed
gate: full
capabilities:
  runtime_binding: VERIFIED_LOCAL
  determinism: VERIFIED_LOCAL
  command_semantics: VERIFIED_FULL
  effects: VERIFIED_FULL
defects: []
experiments: {}
claims:
  - id: CLAIM-002
    status: VERIFIED_LOCAL
    claim: 从可见路径枚举与首调用构造运行时绑定计划，并验证未来信息隔离。
    scope: 人工轨迹中的 NUL 路径枚举与单文件只读模板；固定真实样本无此类正例，不证明未来 LLM 意图。
    evidence: [tests/test_binding.py, tests/test_binding_integration.py, tests/test_binding_qa.py, iterations/iter_005/QA_REPORT.md]
    allowed: 在受限路径枚举模式上实现前缀可见的参数绑定，并以对抗测试验证不使用未来输出。
    forbidden: 证明任意工具调用可程序化，或证明真实模型后续动作与执行结果必然等价。
```
