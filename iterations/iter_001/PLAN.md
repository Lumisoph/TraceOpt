# iter_001 计划

状态：已冻结。负责人：Planner。里程碑：M1。关联 REQ-001、REQ-002。

## 核心闭环与范围

真实 mini-swe-agent 轨迹 → 保持顺序和来源的最小事件 IR → 自动验证。
辅助任务：最小 Python 包、pytest 和 Ruff 配置。只提供 Python API，不实现 CLI、
Bash 语义、依赖分析、命令执行、重放或性能评估。

## 已核实输入

样本：`swe-bench-top11/01_20260217_mini-v2.0.0_claude-4-5-opus-high/trajs/astropy__astropy-12907/astropy__astropy-12907.traj.json`。
SHA-256：`de243a59920f83e36fccd5895b4cf99b4f89c18bee67998f2ada1599020a0504`。
顶层有 info、messages、trajectory_format、instance_id；format 为 mini-swe-agent-1.1。
角色为 system、user、assistant、tool、exit。assistant 的 tool_calls 可含多个 bash 调用，
function.arguments 是含 command 字符串的 JSON 字符串；tool_call_id 关联结果，
extra 保存 returncode 和 raw_output。原样本有最终未返回调用，不能假定调用总有结果。
这些是本地 schema 检查记录，不是产品能力或性能结论。

夹具采用同 schema 的人工内容，不复制任务正文、推理文本或源码；真实样本保持原位，
集成测试通过来源路径和哈希读取。来源记录在 tests/fixtures/provenance.json。

## 最小接口与约束

- `load_trajectory(path)` 返回不可变 Trajectory；`TrajectoryError` 提供中文错误。
- Trajectory：source、source_sha256、trajectory_format、instance_id（可空）、events、pending_call_ids。
- Event：连续 index、message_index、tool_index（仅调用有值）、kind、role、content、
  call_id、tool_name、command、returncode、raw_output；不适用或缺失字段为 None。
- 保留每条消息的位置，assistant 先产生 message 事件，再按数组顺序产生 tool_call 事件；
  tool 产生 tool_result，exit 产生 exit。结果只能引用先前调用，允许同批结果按不同顺序返回。
- 支持 mini-swe-agent-1.1 的上述角色与 bash/command 结构；空 messages 合法。
- 保留原始 content、结构化 raw_output 与 returncode，不从文本标签猜测返回码。
- 未返回调用保留为 pending；重复调用 ID、孤立或重复结果、非法字段、未知格式/角色/工具
  必须拒绝。旧 function_call 非空也拒绝，不能静默丢弃调用。
- 未知的非执行性元数据忽略；参数只支持 command，不忽略未知执行参数。
- 输入只读，不启动子进程，不执行命令；来源文件与 SHA-256 保证可追踪。

## 修改路径

pyproject.toml、.gitignore、src/traceopt/__init__.py、src/traceopt/trajectory.py、
tests/test_trajectory.py、tests/test_trajectory_integration.py、tests/fixtures/trajectory.json、
tests/fixtures/provenance.json、README.md、docs/architecture/canonical_ir.md、
IMPACT_MAP.md、data/README.md、当前轮报告与证据、流程状态文件。
SCOPE_EXCEPTION：首轮同时建立包配置、测试和交接证据，文件数超过 8；产品功能模块仅 trajectory 一个。

## 冻结验收

| 编号 | 验收 | 证据 |
|---|---|---|
| AC-001 | 固定真实样本全部事件顺序、调用、结果、来源可追溯 | 全轨迹逐字段映射断言和样本哈希 |
| AC-002 | 空轨迹不造事件；未返回调用保留 pending；多调用正确关联 | 单元测试 |
| AC-003 | 非法 JSON、缺失字段、未知格式/工具、非法角色、关联冲突提供中文错误 | 参数化反例 |
| AC-004 | 输入不变；命令不执行；返回码缺失保持未知 | 前后哈希、带副作用命令的对抗测试 |
| AC-005 | 安装、完整 pytest、Ruff 可复现 | 环境、命令、退出码、日志、源码哈希 |

## 命令与 Gate

环境：Python 3.11+，项目 .venv；运行时仅标准库。开发依赖 pytest、Ruff。
安装：`python -m venv .venv`，`.venv/Scripts/python.exe -m pip install -e ".[dev]"`。
验收：`.venv/Scripts/python.exe -m pytest -q`；
`.venv/Scripts/python.exe -m ruff check src tests`。
定点集成：`.venv/Scripts/python.exe -m pytest -q tests/test_trajectory_integration.py`。
对抗测试组：恶意命令不执行；伪造/重复调用关联；错误格式不伪装成功。

IR 变更触发 Full Gate，执行本轮全部单元及真实样本集成验证。
挑战集评估和关键 CLI 因对应能力尚未实现不适用，明确记录未执行；
因此不授 VERIFIED_FULL，本轮最高 VERIFIED_LOCAL。M1 仅完成受限格式的首个闭环。

## 风险与交接

仅验证一个格式和一个真实来源，不推广到所有模型或所有 mini-swe-agent 版本。
无 Git 时使用源码与测试 SHA-256 清单。真实样本丢失或哈希变化时测试失败，不静默跳过。
验收标准已冻结，Developer 可开始实现；QA 失败需照常收尾交给下一轮规划。
