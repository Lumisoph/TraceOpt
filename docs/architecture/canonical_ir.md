# Canonical Event IR

## 状态

轨迹读取与 Canonical Event IR 已在固定真实来源上通过 iter_014 QA，状态为 `VERIFIED_FULL`。支持范围以真实来源和适配器测试为准，不代表全数据集兼容。

## 职责

将 mini-swe-agent-1.1 结构化消息映射为保留原始顺序的不可变事件序列，关联工具调用与结果，并保留未返回调用的 pending 状态。

## 输入与输出

入口为 `traceopt.load_trajectory(path)`。输出 `Trajectory` 包含来源哈希、事件序列、调用 ID 映射和 `pending_call_ids`；解析阶段不执行命令、不恢复动态 cwd。

## Responses API 适配边界

固定的 GPT Responses `response/output/function_call/function_call_output` 结构已支持。`response.output` 中的 function_call 依据 `call_id` 关联对应的 function_call_output；消息内容只提取已定义的文本字段，事件顺序以原始 output 顺序为准。缺失关联字段、未知 output 类型、流式或并行语义均明确拒绝，不静默跳过。

## 不变量

- 事件顺序与输入消息顺序一致；同一调用的结果只按明确 ID 关联。
- 缺失结果的调用保留为 pending，不能伪造成功返回。
- 未知格式返回中文 `TrajectoryError`，不会降级成部分解析。
- Canonical IR 只表示轨迹事实，不表示模型意图、执行等价或安全重写结论。

## 与重放的边界

Trajectory parsing 只读取并归一化轨迹；tool replay 只在受限 cat 模板、明确初始仓库和可信本机工具前提下重放工具执行；LLM conversation replay（模型调用、采样和完整对话再生成）当前不支持。工具重放成功不能替代对模型采样或未来动作的验证。

## 已知限制与测试

不覆盖未知 Responses item、computer_call、流式事件、任意供应商格式或全数据集兼容。测试见 `tests/test_trajectory.py`、`tests/test_trajectory_integration.py`、`tests/test_response_qa.py`，结论见 [iter_014 QA](../../iterations/iter_014/QA_REPORT.md)。

## 关联需求

REQ-001、REQ-002，见 [REQUIREMENTS.md](../../REQUIREMENTS.md)。
