# 轨迹与事件

## 1. 为什么需要规范事件表示？

源消息同时包含对话、工具调用和工具返回。分成不可变 Event 后，下游可以按 kind 处理，并通过 index、message_index、tool_index 回到原始位置；不把自然语言内容当命令。当前 IR 只覆盖已支持结构，不是通用聊天格式转换器。
证据：[实现](../../src/traceopt/trajectory.py)、[真实映射测试](../../tests/test_trajectory_integration.py)。

## 2. 如何保留工具调用与观察的关联？

用 call_id 关联先前唯一调用。重复调用 ID、无先前调用的返回、重复返回都拒绝；会话结束仍没返回的调用记入 pending_call_ids，不能推断成功。返回码直接保留结构化字段，不从输出文字猜测。
证据：[适配器测试](../../tests/test_trajectory.py)、[iter_002 QA](../../iterations/iter_002/QA_REPORT.md)。

## 3. 如何识别非轨迹 JSON？

先校验顶层对象、trajectory_format 和 messages 数组，再逐项校验角色、调用类型和参数字段。下载数据中的 preds.json 是实例预测汇总，即使是合法 JSON 也不是轨迹。解析错误抛中文 TrajectoryError，不静默丢弃事件。
证据：[数据说明](../../data/README.md)、[实现](../../src/traceopt/trajectory.py)。

## 4. 输入格式变化如何处理？

相同格式标识不保证内部结构相同。固定 GPT 样本使用嵌套 response.output，目前明确拒绝；固定 Claude、Gemini、DeepSeek 结构已有真实映射回归。新增格式需要独立适配和证据，不能凭同一版本字符串宣布支持。
证据：[来源清单](../../tests/fixtures/cli_sources.json)、[来源回归](../../tests/test_trajectory_integration.py)。

## 5. 如何最小化真实测试夹具？

普通单元夹具手工构造结构与边界，不复制大段真实正文；另保留真实文件路径和 SHA-256，集成测试只读访问原始样本。这样最小案例定位错误，真实映射检查避免只验证自造数据。当前完整集成测试依赖本地原样本，缺失会失败。
证据：[来源记录](../../tests/fixtures/provenance.json)、[夹具](../../tests/fixtures/trajectory.json)。

## 6. 如何证明映射没有改变事件顺序？

集成测试逐消息推进游标，逐项比较角色、内容、调用顺序、命令、返回码及原始输出，并检查规范索引连续、pending 集合正确、源字节未改。证据限固定样本；格式扩展仍需重新验证。
证据：[逐项映射测试](../../tests/test_trajectory_integration.py)。
