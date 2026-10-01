# 改写与重放

## 1. 怎样保证相同初始状态？

输入仓库表示候选片段开始前的状态。先记录源快照，复制基线和执行目录，运行原始 cat 后保存状态；再从基线恢复同一个执行目录，核对快照后运行批处理。同一绝对执行路径也减少错误输出路径不同造成的比较歧义。
证据：[实现](../../src/traceopt/replay.py)、[真实集成](../../tests/test_replay_integration.py)。

## 2. 应比较哪些仓库状态？

比较目录及普通文件的相对路径、类型、权限位、mtime、文件大小和字节 SHA-256；源仓库也需保持不变。读取产生的 atime 明确忽略，不声称覆盖全部操作系统元数据、扩展属性或外部状态。
证据：[snapshot_repository](../../src/traceopt/replay.py)、[重放测试](../../tests/test_replay.py)。

## 3. 输出相同是否足以证明等价？

不够。逐调用比较 stdout/stderr 原始字节和返回码，还要求仓库状态不变；successful 另外要求与历史 raw_output 和返回码匹配。L014 原始与优化执行一致，但历史内容错误，仍应判失败。
证据：[L014 报告](../../results/exp002/L014/replay-0.json)、[EXP-002](../experiments/EXP-002-controlled-loops.md)。

## 4. 如何处理执行失败？

非成功历史、枚举变化、工具缺失或不支持路径会报中文 ReplayError；实际执行超时会终止进程树。评估将重放异常和 unsuccessful 都放入失败分母，不把未执行或跳过当通过。无尝试时成功率为 null。
证据：[实现](../../src/traceopt/replay.py)、[分母回归](../../tests/test_evaluation.py)。

## 5. 重放中如何隔离文件写入？

只在私有临时仓库副本执行固定允许的工具，报告写到副本外的产物目录；拒绝链接与重解析点，清理环境以排除 BASH_ENV 启动注入。它不是操作系统沙箱，不执行任意轨迹 Bash，也不允许用它承载不可信外部程序。
证据：[真实注入与别名测试](../../tests/test_replay_qa.py)、[实现](../../src/traceopt/replay.py)。

## 6. 重放成功的适用边界是什么？

只说明指定初始状态、可信工具和无并发修改前提下，这段受限 cat 的执行满足比较条件。它不证明所有输入上的等价，也不证明模型收到合并观察后会作相同决定。实际工具边界减少不能转换成未经测量的模型成本下降。
证据：[CLAIM-003](../../CLAIMS.md#claim-003)、[iter_006 QA](../../iterations/iter_006/QA_REPORT.md)。
