# 依赖分析

## 1. RAW、WAR、WAW 分别约束什么？

RAW 是先写后读，WAR 是先读后写，WAW 是先写后写；交换原顺序可能改变读取值或最后状态。实现对每个先后调用对比较资源，保存冲突类型和两侧路径。读读没有此类冲突，但这不意味着一定可安全并行。
证据：[实现](../../src/traceopt/dependency.py)、[CLAIM-001](../../CLAIMS.md#claim-001)。

## 2. 未知副作用如何影响重排？

未知命令、未支持选项或缺失 cwd 产生 unknown Effect。任一端 unknown 就产生 BARRIER，不能假设它只读。绑定检测中，枚举后的未知调用也阻止继续采用原路径列表，代价是可能漏掉安全机会。
证据：[命令语义](../../src/traceopt/semantics.py)、[绑定实现](../../src/traceopt/binding.py)。

## 3. 路径别名可能造成什么错误？

不同词法路径可能由符号链接、硬链接或目录重解析点指向同一对象，造成漏依赖。静态模型声明不覆盖别名；重放在复制前拒绝这些对象，不能把 normpath 当作文件身份解析。路径 /a 与 /ab 不重叠，但 /a 与 /a/b 重叠。
证据：[依赖测试](../../tests/test_dependency.py)、[真实别名测试](../../tests/test_replay_qa.py)。

## 4. 缺失依赖和多余依赖各有什么后果？

漏依赖可能放行错误改写；多余依赖主要降低覆盖率。因此采用路径子树重叠和 unknown 屏障，优先可解释的保守判断。即便图中无边，仍需参数来源、上下文、控制流程与实际重放检查，不能把依赖图当完整安全证明。
证据：[依赖架构](../architecture/dependency.md)、[iter_004 QA](../../iterations/iter_004/QA_REPORT.md)。

## 5. 如何构造依赖反例？

用同路径写读、父子树冲突验证正例，用不同子树、路径前缀边界和纯读取验证反例；另覆盖未知命令及 a/../b 的目录遍历前提。预期标签包含冲突种类，而非简单“有边/无边”，避免错误类型碰巧通过。
证据：[人工依赖挑战集](../../data/challenges/dependency_v1.json)、[挑战测试](../../tests/test_dependency_challenges.py)。

## 6. 依赖消融实验验证什么？

EXP-002 只关闭枚举观察到首消费者之间的依赖屏障，其余检测算法与输入不变。消融在受控数据上增加 7 个 FP，例如枚举后 touch 绑定路径仍被接受。这个差异支持该屏障在这些案例中的作用，不能推出生产分布收益。
证据：[verified 注册项](../../results/registry.yaml)、[L033 原始结果](../../results/exp002/L033/result.json)、[评估实现](../../src/traceopt/evaluation.py)。
