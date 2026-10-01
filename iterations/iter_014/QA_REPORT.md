# iter_014 QA 报告

状态：completed。结论：passed。BUG-002 已验证修复。

- 三项 Responses 对抗测试通过：缺失 call_id 拒绝、未知内容拒绝、output 顺序保持。
- 固定 GPT 真实来源逐项回归通过，25 个 bash 调用、83 个事件、pending ID 和源哈希正确。
- 完整 pytest：329 passed；Ruff、真实来源回归、GPT inspect CLI 均通过。
- [执行记录](evidence/qa_execution.json) 保存命令、退出码、源码/fixture 哈希。

BUG-002：VERIFIED_FIXED。适配范围仍限固定 Responses response/output/function_call/function_call_output 结构；未知项、computer_call、流式和并行语义拒绝。旧 EXP-002 结果不变，不重注册。

```yaml
iteration: 14
verdict: passed
gate: full
capabilities:
  trajectory: VERIFIED_FULL
  canonical_ir: VERIFIED_FULL
defects:
  - id: BUG-002
    status: VERIFIED_FIXED
    summary: Responses 适配保留关联、未知内容拒绝、输出顺序不变
    evidence: tests/test_response_qa.py
experiments: []
```
