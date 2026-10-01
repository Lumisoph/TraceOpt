# iter_007 开发报告

状态：completed，交接 QA；不作验收通过判定。

## 实现映射

- AC-701：loops_v1.json 固定 45 个手工设计案例，逐例包含真值、理由、调用上下文和片段初始仓库。
- AC-702：evaluation.py 以精确调用跨度计算集合 TP/FP/FN 与微平均，空分母 null。基线仅比较连续 argv 前缀，消融仅关闭绑定中间依赖屏障，公共接口保持启用。
- AC-703：所有生产 cat 候选实际重放，异常与 unsuccessful 计失败，非 cat 单列；保存逐项执行报告。
- AC-704：配置、数据、产品代码哈希和执行环境写 manifest；新目录独占输出。独立复跑交 QA 核验。
- AC-705：实验文档记录六个具体失败案例与原始证据；尚未注册 verified。

新增一个产品模块 evaluation.py，修改 binding.py 共享私有消融实现；新增评估入口、配置、数据、测试与文档。
无新增依赖。runtime_binding/determinism 因内部调整已撤销当前验证至 IMPLEMENTED_UNVERIFIED，历史证据保留。

## 自测

[执行记录](evidence/dev_execution.json) 含命令、cwd、环境、退出码和完整被测哈希。
完整 pytest：313 passed，退出码 0；Ruff src/tests/examples/experiments：退出码 0。
[pytest 日志](evidence/dev_pytest.log)、[Ruff 日志](evidence/dev_ruff.log)。
实际执行 `.venv/Scripts/python.exe experiments/evaluate.py configs/eval_v1.json results/exp001`，退出码 0。
[manifest](../../results/exp001/manifest.json)、[原始记录](../../results/exp001/raw.json)、[汇总](../../results/exp001/summary.json)。
数字仍属待审核产物，不用于正式对外结论。

## 限制与 QA 重点

人工案例按当前契约设计，非生产分布、非独立留出集。没有新增真实模型正例或成本数据。
重放只执行生产 cat 候选，非 cat 检测候选不适用；基线/消融不执行不安全候选。
检查指标重算、重复与空分母、非法输入不写越界文件、历史不符与异常完整计数。
两次运行可能因目录/mtime 不同产生不同原始状态值，预测与汇总应一致。
QA 可增加验证测试，但不得修改产品实现或标签来追求通过。
