# iter_004 计划

状态：已冻结。需求：REQ-005，关联 REQ-004、REQ-010、REQ-012。里程碑：M2。
核心闭环：有序 Effect → 可解释依赖边 → 轨迹分析 JSON。辅助任务：建立人工标注依赖挑战集。

## 冻结接口与语义

build_dependencies(effects) 返回不可变 Dependency 元组，字段 source、target（调用序号）、
kind（RAW/WAR/WAW/BARRIER）、left_resource/right_resource（屏障为 None）。
比较所有 i<j：写→读 RAW、读→写 WAR、写→写 WAW；读→读无边。
资源按相等或带 / 边界的祖先/后代重叠，根路径覆盖所有路径。不得把 /a 与 /ab 视为重叠。
任一端 unknown，则该对只发出一条 BARRIER，连接该未知调用前后所有节点。
保留所有直接冲突及资源证据，不做传递约简；输出按调用序号、类型、资源排序稳定去重。
非法手工 Effect（非规范 POSIX 路径、非 CommandEffect）以中文 ValueError 拒绝。

analyze_trajectory(trajectory, cwd_by_call=...) 输出 source_sha256、call_ids、event_indices、
effects、edges；数组顺序均为原始调用顺序。cwd 必须来自显式映射，缺失时为 unknown。
不能从宿主目录、其他调用或未来观察推断 cwd。映射多余 ID 拒绝以暴露上下文拼写错误。
不删除失败或未返回的调用；分析不是执行或候选调度。

CLI 新增 analyze INPUT --cwd POSIX_PATH；--cwd 是用户显式断言所有调用使用相同上下文，
不是从轨迹恢复的事实；JSON 含 cwd_policy=explicit_fixed。沿用 --output 不覆盖规则。
无效 cwd 报中文错误且退出 2。动态 cwd 用户应使用 API 提供逐调用映射。

## 验收

AC-401：RAW/WAR/WAW、读读无边、全部冲突资源、方向、稳定性、空输入正确。
AC-402：祖先/后代、根、相似前缀、.. 可达性与 unknown 屏障正确。
AC-403：轨迹调用/事件索引可回溯；缺少 cwd 保守，多余 ID 明确拒绝；真实固定样本集成。
AC-404：analyze CLI 可运行，JSON 与 API 对齐，错误 cwd、缺失参数与输出冲突不伪装成功。
AC-405：40 个有说明和人工标签的依赖案例通过；不将此等同于优化器的端到端评估。

## 文件与预算

新增 dependency.py、依赖单元/集成/挑战测试、data/challenges/dependency_v1.json；
修改公共导出、CLI 与测试、依赖架构、README、IMPACT_MAP、当前轮产物。
SCOPE_EXCEPTION：文档、挑战集和交接使文件数超过八个；新增功能模块仅 dependency。

## Gate

依赖核心变更触发 Full Gate。命令使用 .venv/Scripts/python.exe：
-m pytest -q（全量）；-m pytest -q tests/test_dependency_challenges.py（挑战集全量）；
-m pytest -q tests/test_dependency_integration.py（真实集成）；-m ruff check src tests；
-m traceopt analyze tests/fixtures/trajectory.json --cwd /repo。
另检查 inspect/export 既有 CLI 回归。对抗：相似前缀、屏障穿越、遗漏上下文。
以上完整通过才可对已声明词法模型依赖能力授 VERIFIED_FULL；不扩大至真实执行安全。
不修改语义模型，不新增性能实验注册项，优化精确率/召回率与重放仍待后续实现。
