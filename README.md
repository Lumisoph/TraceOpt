# TraceOpt

用于研究工具调用轨迹优化的持久化 AI 开发工作台。
当前提供 mini-swe-agent-1.1 结构化 bash 轨迹的只读 Python API，以及检查和导出命令；提供受限 cat 循环重放，已通过功能与材料发布审计；0.1.0 发布候选已在独立环境完成安装、CLI、完整测试和 Ruff 验证。
验证范围以 [项目状态](PROJECT_STATE.md)、[iter_019 QA](iterations/iter_019/QA_REPORT.md) 和 [发布条件](RELEASE_CRITERIA.md) 为准。

## 安装与检查

需要 Python 3.11+。在 Windows PowerShell 的项目根目录运行：

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -e ".[dev]"
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe -m ruff check src tests examples experiments
```

运行时没有第三方依赖；开发依赖是 pytest 和 Ruff。
完整测试需要 data/README.md 指向的本地真实样本，缺失时会明确失败。
只运行独立单元测试可使用 `python -m pytest -q tests/test_trajectory.py`（需使用已安装本包的环境）。

## Python 接口

```python
from traceopt import load_trajectory

trajectory = load_trajectory("tests/fixtures/trajectory.json")
for event in trajectory.events:
    if event.kind == "tool_call":
        print(event.call_id, event.command)
print(trajectory.pending_call_ids)
```

解析不会执行命令。事件保留原始消息位置，结果按调用 ID 关联；未返回调用保持 pending。
输入错误抛出中文 TrajectoryError。完整 schema 和限制见 [事件表示](docs/architecture/canonical_ir.md)。

## 工作流与数据

按 [AGENTS.md](AGENTS.md) 的启动顺序读取；当前角色与轮次见 [项目导航](PROJECT_INDEX.md)。
角色顺序为 Planner → Developer → QA → Finalizer → 下一轮 Planner。
Finalizer 是报告驱动的同步阶段，提示词本身不是自动运行的服务。

现有输入保留在 swe-bench-top11，详见 [数据说明](data/README.md)。
实验指标入口为 [结果注册表](results/registry.yaml)，已有 EXP-002 已验证受控检测与重放评估，不代表生产性能或模型成本收益。
发布范围见 [发布条件](RELEASE_CRITERIA.md)；本地发布交接清单见 [RELEASE_HANDOFF.md](RELEASE_HANDOFF.md)。

## 命令行

```powershell
.venv/Scripts/traceopt.exe inspect tests/fixtures/trajectory.json
.venv/Scripts/python.exe -m traceopt export tests/fixtures/trajectory.json --output events.json
```

inspect 返回摘要；export 返回含 schema_version 的完整 IR。默认输出到 stdout。
--output 只创建新 UTF-8 文件，已有文件会报错；成功退出码 0，输入/输出/参数错误为 2。
JSON 字段名用于机器消费；帮助与错误为中文。用 `python -m traceopt --help` 查看帮助。

真实来源回归覆盖固定的 Claude、Gemini、DeepSeek 样本，不能推广为全数据集兼容。
固定 GPT Responses API response/output/function_call 结构已支持；未知响应项仍明确报错，不静默跳过。

## 命令 Effect 分析

```python
from traceopt import analyze_command

effect = analyze_command("cp src.txt dst.txt", cwd="/repo")
print(effect.reads, effect.writes, effect.unknown)
```

仅对 [支持矩阵](docs/architecture/command_semantics.md) 中的形式建模；不执行命令。
unknown=True 必须视为屏障。路径采用显式 POSIX cwd；链接、环境与执行安全需另行验证。

## 依赖分析

```powershell
.venv/Scripts/python.exe -m traceopt analyze tests/fixtures/trajectory.json --cwd /repo
```

--cwd 是你提供的固定工作目录假设；动态目录用 Python API 的 cwd_by_call 逐项提供。
输出保留调用 ID、事件索引、Effect 和带路径证据的依赖边。缺少上下文或未知命令形成屏障。
无依赖边不等于可以直接并行或重写，仍需绑定、确定性和重放验证。
模型与限制见 [依赖架构](docs/architecture/dependency.md)。

## 前缀路径绑定

Python API `infer_loop_at(trajectory, start_event_index, cwd_by_call=...)` 从首调用的可见前缀生成计划，
`detect_runtime_loops(trajectory, cwd_by_call=...)` 检查完整消费序列是否匹配。
支持已成功观察的 `find ROOT -type f -print0` 路径列表与单文件只读模板。
候选构造不依赖未来输出；匹配并不证明 LLM 意图、观察独立或执行安全，仍须后续重放。
详情见 [运行时绑定](docs/architecture/runtime_binding.md) 与 [确定性边界](docs/architecture/determinism.md)。

## 可执行改写与重放演示

需要本机 Bash、标准 cat/find；Windows 使用 Git 自带工具。
下面创建一个新的证据目录，实际捕获 find/cat 输出并验证原始和批处理执行：

```powershell
.venv/Scripts/python.exe examples/replay_demo.py replay-demo-output
```

目录必须尚不存在；输出包括 initial_repo、capture.traj.json、rewrite.sh 和 report.json。
脚本参数依次为仓库副本目录、已建的输出目录和 cat 可执行文件路径。
报告的 successful 要求逐项输出/退出码一致、仓库状态不变且符合历史记录。
演示是受控真实工具执行，不是模型端到端实验，不能据此声明 LLM 成本收益。
Python API 为 replay_cat_loop；细节见 [重放架构](docs/architecture/replay.md)。

## 可复现挑战集评估

先安装上述开发环境，并安装本机 Bash/cat/find（Windows 使用 Git Bash）。运行：

```powershell
.venv/Scripts/python.exe experiments/evaluate.py configs/eval_v1.json evaluation-output
```

输出目录必须尚不存在。raw.json 保留每例真值、三种方法预测与重放结果，summary.json
分别汇总精确跨度 P/R/F1 与实际 cat 重放成功率；manifest.json 记录代码和输入身份。
需要复跑时指定另一个新目录，不覆盖证据。异常和历史不符均计入重放失败分母。
这是人工设计的受控案例，不是生产分布，检测命中不能当作执行收益。
实验审核与失败案例见 [EXP-002](docs/experiments/EXP-002-controlled-loops.md)，
正式数字以 [注册表](results/registry.yaml) 的 verified 状态为准。

## 重放边界

当前重放验证的是受限工具执行片段：在相同初始仓库下实际运行 cat 批处理，并比较输出、退出码、历史记录和可观察仓库状态。TraceOpt 不启动 LLM，不复现模型采样，也不提供 LLM conversation replay；因此不能据此宣称任意 Bash 正确或模型成本下降。




