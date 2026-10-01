# iter_001 QA 报告

状态：completed。结论：passed（本轮冻结范围）。角色按阶段切换，由同一会话执行。

## 被测版本与环境

无 Git commit；[执行记录](evidence/qa_execution.json) 包含时间、工作目录、环境、
逐条命令、退出码、源码及测试 SHA-256。产品源码与 Developer 交付哈希一致，QA 未修改实现。
Python 3.13.5、Windows；[依赖版本](evidence/qa_environment.log)。

## 验收结果

| 项目 | 结果 | 证据 |
|---|---|---|
| AC-001 | 通过 | test_real_trajectory_mapping 对固定真实样本全量逐字段映射；来源哈希匹配 |
| AC-002 | 通过 | 空输入、冻结对象、多调用、乱序结果及 pending 单元测试 |
| AC-003 | 通过 | 非法文档、非法消息、非法参数、未知工具等参数化测试 |
| AC-004 | 通过 | 输入前后字节一致、标记文件未产生、命令执行入口被拦截、返回码不猜测 |
| AC-005 | 通过 | 已安装包可导入；完整测试、Ruff 和 API 冒烟退出码均为 0 |

## 实际执行

工作目录：G:/Advance_tool_mining/TraceOpt。

- `.venv/Scripts/python.exe -m pytest -q`：35 passed，退出码 0，[日志](evidence/qa_pytest.log)。
- `.venv/Scripts/python.exe -m ruff check src tests`：通过，退出码 0，[日志](evidence/qa_ruff.log)。
- Python API 冒烟：读取人工夹具并断言 pending_call_ids，退出码 0，[日志](evidence/qa_api.log)。
  完整命令见执行记录中的 qa_api 项。
- `.venv/Scripts/python.exe -m pip freeze`：退出码 0，记录已安装工具与可编辑包。

QA 补充 tests/test_trajectory_qa.py 的三个对抗用例：
命令与提示注入文本仅作为数据；完成后的调用 ID 不得复用；预测汇总不能冒充轨迹。

## Gate 与适用范围

Fast Gate 通过，针对性测试、逐项验收、全部现有回归和三个补充对抗用例均执行。
IR 修改触发 Full Gate，完整 pytest 与真实样本集成已执行；挑战集和关键 CLI 尚未建立，
这两项未执行，因此 Full Gate 未完整通过，不授 VERIFIED_FULL。
本轮冻结范围没有失败项，不把未建设的后续能力算为已验证。

轨迹与 IR 仅在 mini-swe-agent-1.1、结构化 bash/command 输入上 VERIFIED_LOCAL。
真实来源仅 tests/fixtures/provenance.json 固定的一份；没有全数据集兼容性结论。
未执行性能实验，没有新对外声明；results/registry.yaml 与 CLAIMS.md 不需要变更。

## 缺陷与后续事项

本轮未发现可复现缺陷，不代表不存在缺陷。
后续 Planner 应决定其他来源/格式覆盖及 CLI 的优先级；M1 不作为全面完成里程碑。

## 结构化同步结论

```yaml
iteration: 1
verdict: passed
gate: fast
full_gate:
  status: incomplete
  not_run: [挑战集评估, 关键 CLI]
capabilities:
  trajectory: VERIFIED_LOCAL
  canonical_ir: VERIFIED_LOCAL
defects: []
experiments: {}
claims: []
```
