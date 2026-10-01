# iter_003 QA 报告

状态：completed。结论：passed。Gate：fast。由同一会话按阶段执行。

## 环境与身份

Python 3.13.5、Windows、项目 .venv，工作目录 G:/Advance_tool_mining/TraceOpt。
[执行记录](evidence/qa_execution.json) 包含命令、退出码、日志、时间和源码哈希。
QA 对比开发版本哈希一致；仅新增 tests/test_semantics_qa.py，没有修改实现。

## 验收

| 编号 | 判定 | 证据 |
|---|---|---|
| AC-301 | 通过 | 十五种命令正例及逐项不支持选项反例 |
| AC-302 | 通过 | 引号空格、绝对/相对路径、去重、--、被 .. 消去目录的依赖 |
| AC-303 | 通过 | 未知工具、设备路径、stdin、展开和控制语法返回 unknown 与中文原因 |
| AC-304 | 通过 | touch 分析未产生标记文件；实现不含文件或执行调用 |
| AC-305 | 通过 | 完整现有轨迹、CLI 回归和独立 CLI 冒烟 |

## 命令

- `.venv/Scripts/python.exe -m pytest -q`：119 passed，退出码 0，[日志](evidence/qa_pytest.log)。
- `.venv/Scripts/python.exe -m ruff check src tests`：通过，退出码 0，[日志](evidence/qa_ruff.log)。
- `.venv/Scripts/python.exe -m traceopt inspect tests/fixtures/trajectory.json`：通过，退出码 0，[日志](evidence/qa_cli.log)。

QA 对抗案例：复制目标的父目录遍历、用 .. 掩盖特殊设备、引用中的命令替换保守拒绝。
本轮未改变 IR、依赖核心或重放，且不宣布里程碑完成；未触发 Full Gate。

## 判定边界

command_semantics 与 effects 为 VERIFIED_LOCAL，仅限支持矩阵与词法 POSIX 资源模型。
链接、环境副作用、外部并发修改没有被模型证明安全；下游执行不得据此直接放行。
路径资源须按祖先/后代重叠，unknown 须作为全局屏障；这些是后续依赖模块的验收前提。
没有已发现的可复现产品缺陷，无实验和新对外声明。

## 结构化同步结论

```yaml
iteration: 3
verdict: passed
gate: fast
capabilities:
  command_semantics: VERIFIED_LOCAL
  effects: VERIFIED_LOCAL
defects: []
experiments: {}
claims: []
```
