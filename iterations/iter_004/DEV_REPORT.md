# iter_004 开发报告

状态：completed。dependency 与修改后的 CLI 为 IMPLEMENTED_UNVERIFIED，等待 QA。

## 实现与验收映射

AC-401：dependency.py 比较全部有序调用对，输出 RAW/WAR/WAW 和资源见证；稳定排序去重。
AC-402：按 / 边界比较祖先/后代，根资源覆盖全树；unknown 为前后全局屏障；保留 .. 前提。
AC-403：TrajectoryAnalysis 保留调用 ID、事件索引和输入哈希；缺失上下文保守，多余 ID 拒绝。
AC-404：analyze CLI 要求显式 --cwd 并记录 explicit_fixed，错误目录与覆盖输出明确失败。
AC-405：建立 data/challenges/dependency_v1.json，40 个固定人工标签附说明；不是由实现生成真值。

## 自测

完整 pytest：186 passed，Ruff 通过。工作目录为 G:/Advance_tool_mining/TraceOpt。
Python 3.13.5、Windows、项目 .venv。无新第三方依赖、无 Git commit。
[执行记录与哈希](evidence/dev_execution.json) 包含命令、退出码、源码、测试和挑战集身份。
[pytest 摘要](evidence/dev_pytest.log)、[Ruff 日志](evidence/dev_ruff.log)。

## 变更与限制

新增 dependency.py、依赖/集成/挑战测试及标注数据；修改公共入口、CLI、使用说明和依赖架构。
未修改 Effect 或 IR 语义。无自动 cwd 恢复，无调度、改写或执行安全证明。
Full Gate 由 QA 实际执行；开发自测不授验证状态。无性能实验或新对外声明。
