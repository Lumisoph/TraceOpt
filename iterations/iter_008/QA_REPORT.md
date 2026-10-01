# iter_008 QA 报告

状态：completed。结论：passed。Full Gate 完整通过，无跳过。

## 身份与验收

工作目录 G:/Advance_tool_mining/TraceOpt；Python 3.13.5、Windows、本机 Git Bash/cat/find。
开发交接源码/测试/数据身份一致，QA 未修改产品或数据标签。
[执行记录](evidence/qa_execution.json) 保存全部命令、cwd、环境、退出码、源码/数据/产物哈希。

| 验收 | 结果 | 证据 |
|---|---|---|
| AC-801 | 通过 | 原 QA 缺失 output/cwd 测试、全部必需字段矩阵、真实 CLI 中文错误和退出 2，均在创建目录前拒绝 |
| AC-802 | 通过 | 显式 null 回归、所有原挑战标签不变；BUG-001 两项原失败测试通过 |
| AC-803 | 通过 | 开发与 QA 两次实际评估预测/汇总一致，独立脚本不调用产品计分函数重算全部指标 |
| AC-804 | 通过 | 完整 Gate 和关键 CLI 均退出 0，见下表与执行记录 |

继承 AC-701～705 已复核：人工标签覆盖、三方法同输入、单因素依赖消融、真实重放及失败分母、身份/复现、六个失败案例均有原始证据。

## Full Gate

- 完整 pytest：324 passed，退出码 0，[日志](evidence/qa_pytest.log)。
- Ruff src/tests/examples/experiments：通过，[日志](evidence/qa_ruff.log)。
- 实际重放集成：通过，[日志](evidence/qa_integration.log)。
- 依赖与循环挑战/评估/原 QA 对抗测试：通过，[日志](evidence/qa_challenges.log)。
- inspect/analyze CLI：通过，[inspect](evidence/qa_inspect.log)、[analyze](evidence/qa_analyze.log)。
- 独立评估：[日志](evidence/qa_evaluation.log)，实际新建 [复跑产物](evidence/evaluation_rerun)。
- 独立重算：[日志](evidence/qa_metrics.log)，逐项重算跨度、重放分母与报告的输出/历史/状态判定。

## 实验审核

批准 EXP-002 为 verified，范围严格为人工设计受控案例。
基线 F1 与依赖消融差异可由原始 FP/FN 逐例解释；不意味着生产精度或收益。
重放失败案例全部进入分母，非 cat 单独列不适用。没有遗漏或删除失败。
EXP-001 仍为历史未注册产物，不覆盖；当前注册使用修复后代码身份。
本报告数字为验收证据，正式对外数字由 Finalizer 复制到 results/registry.yaml 后引用。

## 文档同步授权

将 EXP-002 状态、实验索引、README 的“无已验证实验”说明同步为受控评估已验证。
发布条件的六项评估条目与已验证结果注册表可勾选，链接本报告和 EXP-002。
其它发布项保留待最终逐项审计；不宣布 v0.1 已发布。
BUG-001 确认 VERIFIED_FIXED。evaluation 为 VERIFIED_FULL，限已声明评估管线和受控数据。

## 结构化同步结论

```yaml
iteration: 8
verdict: passed
gate: full
capabilities:
  evaluation: VERIFIED_FULL
defects:
- id: BUG-001
  status: VERIFIED_FIXED
  summary: 评估调用缺少必需字段已在创建产物前拒绝；显式 null 保持有效
  evidence: tests/test_evaluation_qa.py
experiments:
  EXP-002:
    status: verified
    commit: null
    scope: 人工设计受控循环挑战集；非生产分布、非模型成本/速度收益
    source_hashes:
      src/traceopt/__init__.py: 832218b3e83759ebc6192430f0f0f45b767c712edb65fe1555450dc1bf596f06
      src/traceopt/__main__.py: 16f9c06bb0393ecac5a070d13c647b67e55b480ba689ba6dcdba7aea891ed4e7
      src/traceopt/binding.py: f1acfd44fb97f5b01017af0eb9224a1e1e11473d5479a0f74c7a71dbc1affb77
      src/traceopt/cli.py: 0d385c0dd4020e8c2235ef050740485be45b73a6896ebee048b57476e70e2cb6
      src/traceopt/dependency.py: ac7190e40417ed785f2bb025c3fdcc29a493d81090d90f905e12deab988d86c8
      src/traceopt/evaluation.py: d1ef0fa085246ad988862e348ece679cb59f24ad6df95aefb89d946be86bd700
      src/traceopt/replay.py: 8a26596b894f93fb29450c752af01fdfa6d93170e52e92c9d6446787432dbf6f
      src/traceopt/semantics.py: accd4c223967494c38fa41fd2046a0a77c0da6d673e58a4fe3e4ab2aea3e6ff2
      src/traceopt/trajectory.py: 93b097e8de330f1be18a0cc71e88a2abdb783c73c20b1bfe42a8a547de73b607
    dataset:
      name: loops-v1
      samples: 45
      positive_cases: 17
      path: data/challenges/loops_v1.json
      sha256: 95c886c2e69e7073bf8ad2396282af2d851357e544ee88828d4158c88e70a3ef
    config:
      path: configs/eval_v1.json
      sha256: b3c0e65e487ceaf89b63ec90c096d953a3f2a23f36be58a413b1b49f2ddb7e76
    artifacts:
      raw: results/exp002/raw.json
      summary: results/exp002/summary.json
      manifest: results/exp002/manifest.json
    metrics:
      precision: 1.0
      recall: 1.0
      f1: 1.0
      replay_success: 0.6666666666666666
      methods:
        production:
          tp: 17
          fp: 0
          fn: 0
          precision: 1.0
          recall: 1.0
          f1: 1.0
        naive:
          tp: 16
          fp: 24
          fn: 1
          precision: 0.4
          recall: 0.9411764705882353
          f1: 0.5614035087719298
        no_dependency_guard:
          tp: 17
          fp: 7
          fn: 0
          precision: 0.7083333333333334
          recall: 1.0
          f1: 0.8292682926829268
      replay:
        attempted: 12
        successful: 8
        failed: 4
        not_applicable: 5
        success_rate: 0.6666666666666666
    qa_evidence:
      iteration: iter_008
      report: iterations/iter_008/QA_REPORT.md
      execution: iterations/iter_008/evidence/qa_execution.json
      independent_recalculation: iterations/iter_008/evidence/qa_metrics.log
claims: []
```
