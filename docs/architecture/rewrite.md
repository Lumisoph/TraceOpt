# 可执行改写

## 摘要

状态：VERIFIED_LOCAL（iter_006 的受控 cat 片段）。src/traceopt/replay.py 实现受限 cat 循环的脚本生成与真实工具重放。

## 职责

将已检测候选重验后生成一次 Bash 调用的循环，并与逐调用原始执行比较。

## 不负责的内容

不执行任意轨迹字符串，不重放整个模型会话，不证明未来 LLM 意图或成本收益。

## 输入

Trajectory、DetectedLoop、候选片段初始 repository、virtual_root 和逐调用 cwd。
仅支持 cat 模板、完整成功的历史结果；原始操作数含 .. 或越界时拒绝。

## 输出

ReplayReport 保存脚本、输入/计划身份、工具哈希、逐项 Base64 stdout/stderr、返回码、
三份状态快照与 equivalent/state_unchanged/matches_recording/successful 标记。

## 数据结构

Toolchain 指定 Bash/cat/find；StateEntry 记录路径、类型、内容哈希、大小、权限、mtime。
CommandResult 的 Base64 可无损恢复输出；读产生的 atime 不参与快照。

## 算法

重做候选检测并校验计划 → 检查普通路径仓库 → 复制 baseline 与 workspace → 重跑 find 核对列表 →
逐个调用原始 cat → 保存状态 → 核验临时路径并恢复同一路径的初始副本 → 一次 Bash 循环调用 cat →
读取每条命令的输出/错误/状态文件 → 比较结果、状态与历史记录 → 再核对源仓库不变。

## 不变量

不在源仓库执行。原始和优化使用相同临时路径、初始内容及权限/mtime。
只运行固定工具与安全引用数据；不把原始轨迹命令字符串作为 shell 程序。
未完成结果、文件列表变更、路径越界、链接或特殊对象不能作为可执行计划通过。

## 假设

调用者提供正确片段初始状态；本机工具可信。临时目录不是操作系统安全沙箱。
本轮使用 Git Bash/标准 cat/find；环境固定 LANG/LC_ALL，清除 BASH_ENV 与函数注入。

## 错误处理

ReplayError 为中文；无效计划/上下文/工具/快照或超时是错误。
超时终止本次进程树；仅对确认属于本次临时根的 workspace 做递归清理。

## 复杂度

仓库快照与复制随总文件字节增长，读取循环随选中文件总字节增长；全部输出暂存内存/证据文件。
未声明时间或吞吐收益；工具调用边界计数不是 LLM 成本测量。

## 已知限制

仅支持受控 cat 片段；拒绝符号链接、junction/reparse、硬链接、特殊文件和父目录跳转。
不比较 atime，不验证文件别名、环境副作用或任意 shell 等价性。
即便原始与优化彼此一致，若不匹配历史 stdout/返回码，successful 仍为 false。

## 测试策略

test_replay.py 验证真实执行、快照、错误前提、历史不符和真实超时。
test_replay_integration.py 捕获实际 find/cat 输出，加载轨迹后检测并重放。
examples/replay_demo.py 可保存完整轨迹、初始仓库、脚本和报告。
结论见 [QA](../../iterations/iter_006/QA_REPORT.md)。

## 关联需求

REQ-008、REQ-009，关联 REQ-006、REQ-007。

## 关联 ADR

当前无 Accepted ADR。

## 面试备注

强调片段重放范围及三个判定：执行彼此相同、仓库不变、匹配历史；不能合并为单一无条件等价声明。
