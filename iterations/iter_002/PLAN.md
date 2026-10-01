# iter_002 计划

状态：已冻结。角色：Planner。里程碑：M1。需求：REQ-001、REQ-002、REQ-012。

## 核心闭环

用户通过 CLI 检查真实轨迹、导出规范 IR，获得可解析 JSON 或明确中文错误。
辅助任务是扩展真实来源回归，确认当前支持范围，不扩展轨迹 schema。

## 已核实范围

固定 astropy__astropy-12907：Claude、Gemini、DeepSeek 使用已支持的 role/tool_calls 结构。
GPT-5.2 虽同样标记 mini-swe-agent-1.1，却包含 object=response/output 和 function_call_output，
现有解析器不支持。将其登记为明确拒绝案例；后续轮次处理，不能静默丢失事件。
来源路径和哈希写入 tests/fixtures/cli_sources.json。

## 接口

- `traceopt inspect INPUT` 与 `python -m traceopt inspect INPUT` 输出单个 JSON 摘要。
- 摘要含 schema_version、source、source_sha256、trajectory_format、instance_id、
  message_count、event_count、tool_call_count、tool_result_count、pending_call_ids。
- `traceopt export INPUT` 输出含 schema_version=1 和完整 Trajectory 字段的 JSON。
- `--output PATH` 可用于两个子命令；只允许创建新文件，UTF-8，不覆盖输入或已有文件。
- 无 --output 时 stdout 仅输出 JSON；错误仅写 stderr，退出码 2；成功为 0。
- 帮助和用户错误提示为中文；不暴露 traceback，不执行轨迹中的命令。
- 不添加 runtime 依赖，不修改已有解析器的支持语义。

## 冻结验收

| 编号 | 验收 | 验证 |
|---|---|---|
| AC-201 | 模块入口与安装后的 traceopt 命令可用 | 子进程调用两个入口 |
| AC-202 | inspect 摘要准确、export 与 asdict(Trajectory) 完整一致 | JSON 结构比较 |
| AC-203 | 新文件输出 UTF-8、中文可恢复、stdout 无混杂 | 文件字节和 JSON 测试 |
| AC-204 | 输入/输出冲突、已有文件、坏路径、坏 JSON、参数错误明确失败 | 非零退出及不变性断言 |
| AC-205 | 原有样本加 Gemini/DeepSeek 逐字段回归，GPT 样本明确拒绝 | 固定来源哈希和预期结果 |

## 修改与预算

新增 src/traceopt/cli.py 和仅转发入口的 __main__.py；修改 pyproject.toml；
新增 tests/test_cli.py、tests/fixtures/cli_sources.json；扩展真实集成测试；
更新 README、data/README、canonical_ir 限制说明、当前报告与状态。
SCOPE_EXCEPTION：测试来源与工作流交接使文件数超过 8；功能模块仅 CLI 一个。

## Gate 与命令

使用 .venv/Scripts/python.exe。安装 `-m pip install -e ".[dev]"`；
验证 `-m pytest -q`、`-m ruff check src tests`、`-m traceopt --help`、
`-m traceopt inspect tests/fixtures/trajectory.json`、`.venv/Scripts/traceopt.exe export tests/fixtures/trajectory.json`。
Fast Gate：全部现有回归、验收、三个对抗类别（文件冲突、坏输入、错误参数）。
没有 IR 语义变更、不宣布 M1 全部完成；最高 VERIFIED_LOCAL。挑战集仍未建立。

## 后续边界

GPT 嵌套响应解析仍未实现；不宣称全数据集兼容。CLI 不提供执行或优化功能。
