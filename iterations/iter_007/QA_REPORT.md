# iter_007 QA 报告

状态：completed。结论：failed。不得以合法数据的成功评估覆盖输入校验缺陷。

## 证据与身份

[执行记录](evidence/qa_execution.json) 含命令、cwd、Python/Windows 环境、退出码、源码与产物哈希。
开发交接文件身份核对一致；QA 仅新增 tests/test_evaluation_qa.py 和独立重算脚本，未改实现。

| 验收 | 结果 | 证据 |
|---|---|---|
| AC-701 | 合法挑战集通过，输入字段缺失失败 | 45 例检测与 QA 新增缺失字段回归 |
| AC-702 | 通过 | 精确跨度/空分母测试、独立重算、单因素消融回归 |
| AC-703 | 通过 | 两次实际评估、逐报告核对输出/历史/状态布尔结论 |
| AC-704 | 部分通过 | 预测与汇总复跑一致；畸形输入未在创建目录前拒绝 |
| AC-705 | 失败案例已记录，注册暂缓 | 实验文档六例与逐例原始产物可追溯 |

## Full Gate

- 完整 pytest：315 passed、2 failed，退出码 1，[日志](evidence/qa_pytest.log)。两处失败均为 BUG-001。
- Ruff src/tests/examples/experiments：通过，[日志](evidence/qa_ruff.log)。
- 重放集成：通过，[日志](evidence/qa_integration.log)。
- 依赖与循环挑战集/评估测试：通过，[日志](evidence/qa_challenges.log)。
- analyze CLI：通过，[日志](evidence/qa_cli.log)。
- 独立实际评估：退出码 0，[日志](evidence/qa_evaluation.log)。
- 不调用产品计分函数的独立重算：退出码 0，[日志](evidence/qa_metrics.log)，
  [脚本](evidence/verify_metrics.py) 重算全部跨度、重放分母、逐项输出/历史/状态判断。

完整 Gate 因两个真实失败未通过，无跳过项。合法挑战集两次预测/指标相同，但本轮不注册正式实验。
绑定原有回归和新增挑战通过，恢复 runtime_binding/determinism 的已有 VERIFIED_LOCAL 范围。

## BUG-001（OPEN）

位置：src/traceopt/evaluation.py 的 validate_dataset 与 _trajectory。
步骤：删除合法调用中的 output 或 cwd 键，调用 run_evaluation。
期望：字段校验给出中文 ValueError，且尚未创建输出目录。
实际：get() 将缺失与显式 null 混淆，校验放行；创建目录后索引字段触发 KeyError。
复现：`.venv/Scripts/python.exe -m pytest -q tests/test_evaluation_qa.py`。
影响：畸形输入导致非约定异常与不完整产物；不改变已保存合法挑战集数值。
下一轮必须修复校验并保持显式 null 支持，重跑评估与 Full Gate。

## 结构化同步结论

```yaml
iteration: 7
verdict: failed
gate: full
capabilities:
  runtime_binding: VERIFIED_LOCAL
  determinism: VERIFIED_LOCAL
  evaluation: BROKEN
defects:
  - id: BUG-001
    status: OPEN
    summary: 评估调用缺少 output/cwd 时校验放行并在创建产物后触发 KeyError
    evidence: tests/test_evaluation_qa.py
experiments: {}
claims: []
```
