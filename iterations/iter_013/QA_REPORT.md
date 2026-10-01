# iter_013 QA 报告

状态：completed。结论：failed。

新增独立对抗 tests/test_response_qa.py 复现三项失败；未修改产品实现。
完整测试结果、退出码、源码与测试身份见 [执行记录](evidence/qa_execution.json)、[完整日志](evidence/qa_full.log)、[对抗日志](evidence/qa_response.log)。Ruff 日志见 [检查](evidence/qa_ruff.log)。

## BUG-002 OPEN：Responses 适配损失语义

1. function_call 缺少 call_id 时以 item.id 替代，错误接受无法按正确关联 ID 对齐的输入。
2. message.content 含未知类型时静默丢弃，违反未知内容明确拒绝约束。
3. output 顺序为调用、文本时，将后面的文本合并到前面的 assistant 消息，破坏事件顺序及前缀可见性。

复现命令：`.venv/Scripts/python.exe -m pytest -q tests/test_response_qa.py`，三项均失败。
旧真实来源及受控评估通过不覆盖这些新边界。AC-1301/1302 未满足，AC-1303 Full Gate 失败；文档不得把 GPT 适配标为已验证。
EXP-002 保留原版本的历史 verified 结论，不覆盖原 manifest，也不把当前复跑直接替换成新 verified 实验。
新适配应严格区分调用关联 ID、逐项保留来源/顺序、显式拒绝不支持内容，并加强真实源逐项映射测试。

```yaml
iteration: 13
verdict: failed
gate: full
capabilities:
  trajectory: BROKEN
  canonical_ir: BROKEN
defects:
  - id: BUG-002
    status: OPEN
    summary: Responses 适配替代调用ID、丢弃未知内容并重排消息
    evidence: tests/test_response_qa.py
experiments: {}
claims: []
```
