# 评估与证据

## 1. Precision、Recall、F1 的分母如何定义？

单位是案例 ID 与完整调用 ID 序列。预测跨度完全匹配真值才为 TP，额外预测为 FP，遗漏真值为 FN；每例集合去重后微平均。P=TP/(TP+FP)，R=TP/(TP+FN)，F1=2TP/(2TP+FP+FN)，对应分母为零返回 null。
证据：[计分实现](../../src/traceopt/evaluation.py)、[精确跨度回归](../../tests/test_evaluation.py)。

## 2. 挑战集应覆盖哪些失败类型？

来源失败、缺失输出、NUL 截断、重复/越界路径、顺序/模板改变、cwd 改变、写入/unknown 屏障与用户中断。执行层另覆盖历史不符和仓库枚举变化。EXP-002 有 45 个人工设计案例，但按当前契约设计，不是独立留出数据或生产采样。
证据：[标注集](../../data/challenges/loops_v1.json)、[verified 注册项](../../results/registry.yaml)。

## 3. 朴素基线如何保证公平？

三方法使用同一轨迹、同一标签和同一精确跨度计分。基线只把连续同 argv 前缀调用归为最长序列，不检查来源和依赖；它刻意朴素，不代表已有方法的最优水平。消融与生产共享算法，只有依赖屏障开关不同。
证据：[实现](../../src/traceopt/evaluation.py)、[EXP-002 方法说明](../experiments/EXP-002-controlled-loops.md)。

## 4. 重放成功率的样本集合如何选择？

分母是生产检测全部 cat 候选，不仅成功进入执行的样本；异常和历史不符都算失败。EXP-002 为 12 次尝试、8 次成功、4 次失败，另有 5 个非 cat 候选不适用。这个集合与结构检测真值分母不同，不能混用。
证据：[verified 注册项](../../results/registry.yaml)、[逐例原始产物](../../results/exp002/raw.json)。

## 5. 如何区分离线估计与实际收益？

轨迹结构只能估计可合并的工具边界。当前实际执行验证了受限片段的输出和状态，没有运行完整模型会话或测量模型计费，因此没有端到端调用成本、延迟或任务成功率收益结论。挑战集上的理想检测分数也不代表生产可靠性。
证据：[实验限制](../experiments/EXP-002-controlled-loops.md)、[声明边界](../../CLAIMS.md)。

## 6. 哪些结果可以写入简历？

只使用 VERIFIED_FULL 或带明确范围的 VERIFIED_LOCAL 声明；数字还须来自 verified 实验注册项，连同数据范围和分母解释。当前三条材料分别描述依赖模型、前缀绑定和受限重放；不把上游 SWE-bench 成绩或未经执行的规划当个人项目成果。
证据：[简历表述](resume.md)、[注册表](../../results/registry.yaml)、[iter_008 QA](../../iterations/iter_008/QA_REPORT.md)。
