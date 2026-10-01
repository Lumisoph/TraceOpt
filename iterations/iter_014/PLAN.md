# iter_014 计划

状态：冻结。核心闭环：修复 BUG-002，按 Responses output 项保序生成 Canonical Event。

范围：重构 response normalization，使每个 response 保留原始 message_index，并按 output 顺序产出 assistant message、tool_call 事件；function_call 必须有非空 call_id，message content 只接受 output_text，未知项拒绝。function_call_output 保留其原始位置并关联 call_id。同步真实 GPT 映射断言。
非目标：不扩展 computer_call、流式事件、并行执行或任意 Responses schema；旧 mini-swe 格式不变。

验收：
- AC-1401：三个 QA 对抗测试通过，调用 ID 不替代、未知内容不丢弃、顺序不改变。
- AC-1402：固定 GPT 源逐项调用命令、返回码、raw_output、pending 与 event 顺序核对；文件哈希不变。
- AC-1403：旧格式回归、完整 pytest、Ruff、CLI 通过；无新失败。
- AC-1404：BUG-002 仅 QA 可确认 VERIFIED_FIXED；文档保持严格支持边界。

Full Gate：真实轨迹、完整 pytest、Ruff、CLI；评估结果若输入身份未变可复核但不重注册。
