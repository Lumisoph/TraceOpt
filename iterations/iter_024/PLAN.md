# iter_024 PLAN

状态：冻结。角色：Planner。

## Objective 与 Evidence

完成已公开源码的发布事实同步和新克隆复现闭环。远程 main 已指向
`881c38a688da9245637b381c67e0949c98d9bf87`，但交接文档仍称未发布，数据说明新增段落乱码，
本轮报告仍为占位。先前直接修改和推送未完成角色交接；本计划记录恢复事实，不追认旧验证。

## Relevant Requirements

REQ-001、REQ-012、REQ-014；原始目标要求公开 GitHub、可复现且保留原始实验与限制。

## Must / Should / Out of Scope

- Must：修复数据说明和来源记录；保持四个真实来源哈希不变；提交文本换行规则。
- Must：同步发布事实；从候选 Git 提交的新克隆、独立环境运行 Full Gate 并存证。
- Should：确认 README 安装命令和样本定位适用于公开克隆。
- Out of Scope：新产品功能、扩大模型覆盖、上传安装包、声称生产性能收益。

## Required Reading 与 Implementation Tasks

读取 IMPACT_MAP、iter_023 QA、README、data/README、来源清单、发布交接、发布审计和文档测试。
任务一：修复源码公开后的文档、样本说明、换行配置与文档断言。
任务二：在独立克隆验证并完成当前轮证据、状态和远程同步。

## Acceptance Criteria / Regression Tests

1. 数据说明可读，无问号占位；清单同时记录公开路径和原始来源，SHA-256 校验通过。
2. 发布交接和审计明确 main 已公开；不冒称 GitHub Release、PyPI 或 wheel 上传。
3. 新克隆不依赖工作区外部数据或原包，独立环境完整 pytest、Ruff、CLI 通过。
4. replay_demo 和全量受控评估实际运行，固定检测与重放计数与 verified EXP-002 一致。
5. QA 证据保存命令、环境、目录、退出码、日志及候选 commit；最终 main 与本地一致。

Gate：Full Gate。对抗检查：真实样本哈希、无完整数据集、无乱码与陈旧未发布声明。
风险：Windows Git 自动换行可破坏样本哈希；通过 .gitattributes 与新克隆验证处理。
SCOPE_EXCEPTION：文档和交接同步超过 8 文件软预算，均属同一发布事实与复现闭环。

## Definition of Done

Developer 报告交接 QA，QA 独立执行并明确结论；Finalizer 据报告同步，最后原子更新机器状态。
远程更新仅包含本轮计划内修复，保留历史证据与受限能力声明。
