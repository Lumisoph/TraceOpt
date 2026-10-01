# 执行依赖

## 摘要

状态：VERIFIED_FULL（iter_004 词法资源模型范围内）。src/traceopt/dependency.py 构建词法路径模型下的 RAW/WAR/WAW 及未知屏障。

## 职责

比较有序 Effect，为潜在文件资源冲突生成带见证路径的前向边，保持调用来源映射。

## 不负责的内容

不执行命令，不推断运行时 cwd，不检测循环或证明无边调用可以安全并行。

## 输入

build_dependencies 接受有序 CommandEffect 序列。analyze_trajectory 接受 Trajectory 和显式 cwd_by_call 映射。
CLI analyze 的 --cwd 是用户断言所有调用共享固定上下文，并非自动恢复出的事实。

## 输出

不可变 Dependency 元组，source/target 为调用序号，kind 为 RAW/WAR/WAW/BARRIER。
left_resource/right_resource 保存冲突证据，屏障没有具体路径。

## 数据结构

TrajectoryAnalysis 含 source_sha256、call_ids、event_indices、effects、edges。
位置一致的数组将调用序号映射回原始轨迹和事件；失败或未返回调用也保留。

## 算法

按 i<j 比较全部调用对。任一端 unknown 时生成一条 BARRIER；
否则分别比较写读、读写、写写的资源笛卡尔积。资源相等或为祖先/后代视作重叠。
根路径与任何路径重叠；/a 与 /ab 不重叠。输出类型与资源排序固定，去重但不做传递约简。

## 不变量

所有边都从较早调用指向较晚调用，构成有向无环图。读读不产生数据冲突边。
未知节点与全部前驱、后继建立屏障，不能被当作空读写的独立节点。
缺失 cwd 保守产生 unknown，不从宿主环境或未来观察猜测。

## 假设

沿用 Effect 的普通 POSIX 路径模型，无文件别名、环境副作用或并发变更。
输入上下文须由调用者保证。图只提供资源冲突约束，不覆盖全部控制和观察依赖。

## 错误处理

手工构造的非规范路径、非 CommandEffect 输入、多余 cwd 映射 ID 以中文 ValueError 拒绝。
未知命令和缺失上下文是有效但保守的分析结果，不伪装为无冲突。

## 复杂度

调用数 N、每调用最多 K 个资源时，比较复杂度 O(N²K²)，另含资源排序与路径比较开销。
保存所有直接冲突，最坏输出同阶。当前优先透明正确性，不做大型图索引优化。

## 已知限制

没有自动 cwd 恢复或并行执行。unknown 较多时图会稠密，这是保守结果。
无边不等于观察独立、确定性或执行安全；后续绑定、确定性和重放需要额外验证。

## 测试策略

test_dependency.py 验证类型、路径边界、屏障、稳定性与 .. 前提。
test_dependency_integration.py 验证真实轨迹的调用映射、完整性和屏障。
[人工挑战集](../../data/challenges/dependency_v1.json) 由独立固定标签定义预期边类型；
test_dependency_challenges.py 全量校验，未将实现结果反向生成标签。
CLI 同时测试已知 RAW 与未知屏障。结论见 [QA](../../iterations/iter_004/QA_REPORT.md)。

## 关联需求

REQ-005、REQ-004、REQ-010、REQ-012。

## 关联 ADR

当前无 Accepted ADR。

## 面试备注

解释 RAW/WAR/WAW 与屏障的区别、子树过度近似及无边不代表可安全执行。
对外措辞仍由 [CLAIMS](../../CLAIMS.md) 控制。
