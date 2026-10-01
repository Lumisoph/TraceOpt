# 实验记录索引

[EXP-001 受控循环检测与重放](EXP-001-controlled-loops.md)：因 BUG-001 暂缓注册，保留历史证据。

记录问题、假设、被测源码身份、数据路径与哈希、配置、命令、环境、原始产物、汇总、失败案例和 QA 复核。

正式结果使用 [注册表](../../results/registry.yaml)。verified 条目必须含 status、commit（无 Git 时为 null 并补 source_hashes）、dataset、config.path、artifacts.raw、artifacts.summary、metrics、qa_evidence.iteration 和 qa_evidence.report。

未复核结果使用 unverified，不能引用为正式数字。样本数、指标、哈希均不得填示例值。

[EXP-002 修复后受控评估](EXP-002-controlled-loops.md)：已由 iter_008 QA 验证并登记。
