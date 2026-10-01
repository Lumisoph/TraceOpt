# 简历表述与追问依据

下面三条是项目能力表述；个人职责与投入时间应按本人实际参与情况说明。

## 1. 文件依赖分析

在显式 POSIX 路径模型下，实现工具调用的读写 Effect 与 RAW/WAR/WAW 依赖分析，保留资源冲突证据，并对未知副作用设置顺序屏障。

依据：[CLAIM-001](../../CLAIMS.md#claim-001)，VERIFIED_FULL；[实现](../../src/traceopt/dependency.py)、[QA](../../iterations/iter_004/QA_REPORT.md)。
范围：词法路径子树，不覆盖文件别名、环境副作用或完整控制依赖。
可追问：为什么保守、如何处理父子路径、为什么无依赖边不代表可直接并行。

## 2. 前缀可见绑定

在受限 NUL 路径枚举与单文件只读模板上，实现从可见前缀构造参数绑定计划，并通过未来输出和上下文的对抗测试检查信息隔离。

依据：[CLAIM-002](../../CLAIMS.md#claim-002)，VERIFIED_LOCAL；[实现](../../src/traceopt/binding.py)、[QA 测试](../../tests/test_binding_qa.py)。
范围：人工轨迹的受限模式；不能声称证明未来模型意图或所有工具调用都可程序化。
可追问：前缀推断与后缀匹配的区别、如何关联来源、为何哈希不能混入未来信息。

## 3. 可执行改写验证

为受控单文件 cat 循环生成可执行批处理，在相同初始仓库状态上重放原始与优化片段，核对逐项输出、退出码、历史记录及仓库状态，并保留失败证据。

依据：[CLAIM-003](../../CLAIMS.md#claim-003)，VERIFIED_LOCAL；[实际捕获报告](../../iterations/iter_006/evidence/live_capture/report.json)、[验证后的评估](../experiments/EXP-002-controlled-loops.md)。
范围：可信标准工具、普通无别名仓库；不代表任意 Bash 或模型端到端成本下降。
可追问：为什么输出一致仍可能失败、如何恢复初始状态、为什么临时副本不是安全沙箱。
