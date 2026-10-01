# iter_006 计划

状态：已冻结。需求：REQ-008、REQ-009，关联 REQ-006/007。里程碑：M4。
核心闭环：已检测 cat 循环 → 可执行 Bash 批处理 → 同初始状态原始/优化重放 → 结果与仓库状态比较。
不执行任意轨迹命令，不支持其他消费者模板。复用本机 Git Bash/标准 cat/find，无新 Python 依赖。

## 接口与执行契约

replay_cat_loop(trajectory, loop, repository, virtual_root, cwd_by_call, timeout=...) 返回冻结 ReplayReport。
先重新检测并验证 loop 与当前轨迹/上下文完全一致；只接受单文件 cat 模板和无 .. 的原始操作数。
所有虚拟路径必须处于显式 virtual_root；映射到仓库副本，不把轨迹绝对路径交给宿主执行。
要求记录中消费者有成功、完整结果。缺失结果、未知或写模板均拒绝。

工具 discover_toolchain 返回 Bash、cat、find 的绝对路径；Windows 使用已安装 Git 的工具，
其他平台查找本机工具；缺失时中文错误，不静默跳过验证。运行环境清除 BASH_ENV/函数等注入，
显式固定语言环境；命令与路径使用 argv 或 shell 安全引用，不执行原始命令字符串。

源 repository 只读快照后复制到私有临时目录。快照保存普通目录/文件、SHA-256、大小、权限与 mtime，
不比较 atime。拒绝软链接、Windows reparse/junction、硬链接与特殊文件。
检查复制后快照与源一致。重跑受限 find，确认绑定路径列表与计划完全一致。

原始执行逐个调用 cat；优化脚本一次 Bash 调用循环执行 cat，并将每条命令的 stdout/stderr/退出码
保存到仓库外的独立文件，保持命令边界。两次执行使用同一个临时 workspace 路径，
运行优化前从不变 baseline 恢复；任何递归清理必须先核对该路径位于本次临时根下。
提供正的有限 timeout；超时终止本次进程树并返回中文错误，不记作验证通过。

ReplayReport 保存生成脚本、输入与计划身份、工具二进制哈希、逐命令输出（Base64 无损）、
初始/结束快照、equivalent、state_unchanged、matches_recording、successful。
equivalent 比较原始与优化的输出、退出码和相同状态；successful 另要求全部成功且匹配记录。
目录内容不同、历史输出不符或命令失败不得计作成功。报告中工具边界计数不是 LLM 成本收益。
该重放验证候选片段，不声称重放整个模型会话；输入仓库必须是该片段初始状态。

## 冻结验收

AC-601：至少一个真实可执行批处理脚本；相同初始快照下与逐命令 cat 输出/返回码一致。
AC-602：源仓库不变，原始/优化末状态与初始快照一致；保留目录和普通文件状态证据。
AC-603：硬链接/软链接或重解析点、越界、伪造计划、非 cat、..、缺失历史结果执行前拒绝。
AC-604：捕获实际 find/cat 输出形成可解析轨迹，检测循环并实际重放成功。
AC-605：历史输出不符标 unsuccessful；文件列表变化拒绝；超时与工具缺失是错误而非通过。

## 修改与 Gate

新增 replay.py、重放单元/集成测试；更新公共接口、架构、README、IMPACT_MAP、当前证据。
改写生成与重放同属一个功能模块，避免先造通用执行框架。
SCOPE_EXCEPTION：快照、实际执行测试、文档和交接使文件数超过八个。
Full Gate：完整 pytest；tests/test_replay_integration.py；依赖挑战集全量；Ruff；现有 analyze CLI。
工具为 .venv/Scripts/python.exe 与本机发现的 Bash/cat/find。所有实际执行仅在临时测试仓库内。
本轮可达 VERIFIED_LOCAL，限受控 cat 片段；无端到端模型性能数字或普适等价证明。
