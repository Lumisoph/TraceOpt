# iter_010 QA 报告

状态：completed。结论：passed。现有 v0.1 功能与材料条件具备证据；批准进入版本封版，不等于已经发布。

## 最终证据

工作目录 G:/Advance_tool_mining/TraceOpt。源码及材料身份见 [哈希](evidence/qa_release_identity.json)。
[原执行记录](evidence/execution.json)、[干净环境 QA](evidence/qa_clean_execution.json) 保存命令、退出码、cwd 与日志。
最初使用 --no-build-isolation 且未安装 setuptools 的失败是检查命令造成，不是 README 安装失败。
QA 新建 .venv-release-audit，执行 README 原有 pip install -e .[dev]（保留构建隔离）成功，随后完整 pytest 和 Ruff 成功。
[干净环境测试](evidence/qa_clean_pytest.log)、[Ruff](evidence/qa_clean_ruff.log)、[安装](evidence/qa_readme_install.log)。
旧临时环境路径已不存在，未据其历史存在性声称本轮仍在运行；新环境记录是本轮复现依据。

## 逐项需求审计

| 需求 | 结论与直接证据 |
|---|---|
| REQ-001 | 固定三真实来源逐消息映射、哈希及源不变；[实际日志](evidence/qa_real.log)，GPT 变体明确不支持 |
| REQ-002 | 映射测试逐项核对顺序/调用 ID/结果/pending；同上及 tests/test_trajectory.py |
| REQ-003 | 支持矩阵覆盖 15 个命令名的明确形式；test_semantics.py 由完整 Gate 执行，不等于任意选项支持 |
| REQ-004 | Effect 路径、未知及目录遍历前提回归通过，限词法路径模型 |
| REQ-005 | 三类依赖、父子路径与 unknown 屏障回归及人工依赖挑战通过 |
| REQ-006 | 成功 NUL find 来源、模板与完整连续后缀验证；绑定测试及 45 例结构挑战通过 |
| REQ-007 | 前缀切片、未来输出变化、未来 cwd 读取保护的实际测试通过；不证明模型未来意图 |
| REQ-008 | [新生成 Bash 脚本](evidence/demo/rewrite.sh) 已实际执行 |
| REQ-009 | [新重放报告](evidence/demo/report.json) 四项布尔结论为 true；字节/退出码/历史/状态比较及源不变，链接拒绝/超时回归通过 |
| REQ-010 | EXP-002 verified，固定 45 标签、同输入基线、精确跨度 P/R/F1、实际 cat 成功分母；[独立复算](evidence/qa_metrics.log) |
| REQ-011 | 相同算法仅关闭中间依赖屏障；六个具体失败案例均有原始产物，四次重放失败保留分母 |
| REQ-012 | 干净安装后 324 测试、Ruff、CLI 子进程检查通过；README 的 inspect/export/analyze、demo、evaluate 已执行 |
| REQ-013 | iter_009 三条有范围表述、五段讲解与 30 问答；本轮身份复核，正式数字仅引用 EXP-002 |
| REQ-014 | 角色/状态/索引/报告/证据结构已存在。发现 iter_009 收尾遗漏导航阶段同步，须由 Finalizer 按本报告补齐；不改流程枚举 |

## 验收与同步判定

AC-1001～1004 通过：未勾选的 8 项有上述直接证据，可以由 Finalizer 勾选。
RELEASE_CRITERIA 没有“全部能力须 VERIFIED_FULL”的附加门槛；沿用已声明支持范围，并不改变需求。
局部验证标签保留，不把受控模式升级为任意 Bash 或生产泛化。无新产品缺陷。
版本仍为 0.1.0.dev0，下一轮仅封版、构建、安装和包内代码身份验证，不再扩展功能。
同时批准修正文档中与已验证事实冲突的占位文本、面试索引“待 QA”与机器入口不一致的位置；历史 QA 事实不删除。

## 结构化同步结论

```yaml
iteration: 10
verdict: passed
gate: full
capabilities:
  career_material: VERIFIED_LOCAL
defects: []
experiments: {}
claims: []
release_criteria_satisfied: true
release_approved: false
remaining_work: 版本封版、构建与分发包安装验证
```
