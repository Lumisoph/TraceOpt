# iter_013 计划

状态：冻结。核心闭环：支持固定 GPT Responses API 轨迹并完成真实来源回归（REQ-001、REQ-002、REQ-012）。

范围：在 trajectory.py 增加严格 response 对象 normalization，支持 reasoning/message/function_call 与 function_call_output；保留调用 ID、命令、输出、返回码、顺序和 pending。旧 mini-swe 消息格式行为不变。仅支持已观察 schema，不做任意 Responses API 兼容承诺。
更新 GPT 固定来源清单和集成回归；重新跑完整真实来源、pytest、Ruff、CLI。保留源文件哈希，不复制大数据。
非目标：不解析非 bash 工具、流式事件、并行语义或未知 output 类型；不改优化器与实验数字。

验收：
- AC-1301：固定 GPT 来源可加载，事件数、调用数、返回码、raw_output 和 pending 关联正确。
- AC-1302：旧格式全部回归通过；未知响应项、坏 function 参数、重复/孤立返回仍中文拒绝。
- AC-1303：真实三类来源集成、完整 pytest、Ruff 和 inspect CLI 通过；源码/数据哈希记录。
- AC-1304：文档明确 GPT 支持范围和限制，不把来源支持误写成通用格式支持。

Full Gate：真实来源映射、完整 pytest、Ruff、CLI；QA 独立确认固定源未修改。
