# 变更记录

## iter_024

- 修复公开仓库数据说明和来源路径，固定四个真实样本的 LF 换行与 SHA-256。
- 同步 GitHub main、发布审计和交接清单的源码发布事实，保留 GitHub Release、PyPI 和安装包边界。
- 在全新远程克隆中通过 334 项测试、Ruff、CLI、真实重放和 45 例受控评估。

## 工作台初始化 · 2026-09-22

- 建立长期规则、工作流、状态、导航、角色提示词和证据模板。
- 首轮停留在 planning，所有产品能力为 PLANNED。
- 保留现有轨迹数据；没有录入示例性能结果或已验证声明。
- 初始化属于工作台搭建，不计作已完成的产品迭代。

## iter_001

- 实现只读 mini-swe-agent-1.1 轨迹解析和最小不可变事件 IR。
- 保留来源哈希、消息位置、调用关联与未返回调用，不执行命令。
- QA 验证通过，轨迹与 IR 标为 VERIFIED_LOCAL；Full Gate 缺少 CLI 和挑战集检查。
- 证据：[QA 报告](iterations/iter_001/QA_REPORT.md)。收尾后进入 iter_002 / planning。

## iter_002

- 增加 inspect/export CLI，UTF-8 JSON 输出，已有文件不覆盖。
- 扩展真实来源回归，明确拒绝 GPT 嵌套响应。
- [QA](iterations/iter_002/QA_REPORT.md) 通过，CLI 为 VERIFIED_LOCAL；进入 iter_003 / planning。

## iter_003

- 实现十五种明确命令形式与词法路径读写 Effect。
- unknown 明确标记，保留 .. 消去目录的可达性依赖。
- [QA](iterations/iter_003/QA_REPORT.md) 通过，能力为 VERIFIED_LOCAL；进入 iter_004 / planning。

## iter_004

- 实现 RAW/WAR/WAW、unknown 屏障、轨迹来源映射与 analyze CLI。
- 增加人工依赖挑战集，完成 [Full Gate](iterations/iter_004/QA_REPORT.md)。
- 登记受限 CLAIM-001；进入 iter_005 / planning，未完成全产品发布。

## iter_005

- 实现 NUL 路径枚举绑定、前缀计划生成与事后连续命令匹配。
- 测试未来信息隔离、冲突和未完成调用屏障；[QA](iterations/iter_005/QA_REPORT.md) 通过。
- 登记受限 CLAIM-002，进入 iter_006 / planning；尚无执行等价性结论。

## iter_006

- 生成可执行 cat 批处理，并在相同状态副本中进行真实工具重放。
- 核对逐项输出、返回码、历史记录与仓库状态，拒绝链接、越界与无效计划。
- [QA](iterations/iter_006/QA_REPORT.md) 保存实际捕获和脚本产物；登记受限 CLAIM-003，进入 iter_007 / planning。

## iter_007

新增受控循环评估、45 个标注案例、朴素基线和单因素消融，保存逐例实际重放。
QA 独立复跑与重算一致；315 passed、2 failed，记录 BUG-001 输入字段缺失，暂缓正式结果注册。

## iter_008

修复 BUG-001 缺失字段校验，原失败测试与完整 324 项测试通过。
QA 独立复跑并重算，登记 EXP-002 为 verified；受控结果不代表生产模型收益。

## iter_009

完成三条有证据边界的简历表述、三分钟讲解、30 个面试问答、架构总览和发布审计清单。
QA 核对引用、限制和链接通过；仍需最终发布 QA，未宣布 v0.1。

## iter_010

逐项发布审计通过；README 原安装命令在新环境复现，324 测试与 Ruff 通过。补齐职业材料、导航同步和文档占位。只剩版本封版与包验证。

## iter_011

构建并验证 0.1.0.dev0 wheel/sdist；新环境安装、包内导入、CLI、完整测试和 Ruff 通过。

## iter_012

版本元数据封为 0.1.0，wheel/sdist 的 9 个 Python 文件逐字节匹配源码；新环境安装、完整测试、Ruff、demo 和评估复算通过。生成本地发布候选，未上传外部仓库。

## iter_013

QA 发现三项 Responses 语义丢失，326 passed、3 failed，记录 BUG-002。保留失败证据，未注册新实验。

## iter_014

修复 BUG-002，固定 GPT Responses API 轨迹逐项保序解析；329 项测试、真实来源回归、Ruff 和 CLI 通过。

## iter_018

修复权威文档中的损坏占位符和过期状态，明确 Responses API、工具重放与 LLM conversation replay 的边界。
新增文档一致性检查；完整 333 项测试、Ruff、关键 CLI 和受限 cat 实际重放通过。未新增能力、实验或对外声明。

## iter_019

修复发布文档中的字面量换行占位；重建 0.1.0 wheel/sdist，并在独立环境安装验证。
源码与 wheel 的 9 个 Python 文件逐项 SHA-256 一致；独立环境完整测试 333 passed、Ruff 和 CLI 通过。未新增能力、实验或声明。

## iter_020

清理机器状态中的乱码缺陷摘要，更新 README 与项目导航到最新发布候选证据。
新增状态快照可读性检查；334 项测试、Ruff、CLI 和受影响回归通过。未新增能力、实验或声明。

## iter_021

将发布审计从过期草稿更新为 v0.1.0 本地发布候选的逐项证据映射，明确 GitHub 远程发布尚未发生。
发布审计链接、完整 334 项测试、Ruff、CLI 和受影响回归通过。未新增能力、实验或声明。

## iter_022

新增 v0.1.0 发布交接清单，绑定 wheel/sdist 哈希、源码身份、QA 证据和外部发布边界。
修正证据 manifest 编码；交接哈希检查、完整 334 项测试、Ruff、CLI 和受影响回归通过。未新增能力、实验或声明。

## iter_023

完成最终发布候选回归，修复一致性测试的陈旧迭代断言。
334 项测试、Ruff、CLI 和发布条件检查通过；本地候选完成，GitHub 远程动作仍未执行。
