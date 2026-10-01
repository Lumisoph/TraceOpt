# iter_008 计划

状态：冻结。核心闭环：修复 BUG-001 并完成受控评估证据注册。
需求 REQ-010、REQ-011、REQ-012、REQ-014；继承 iter_007 AC-701～705，不降低门槛。

## 范围与路径

修复 evaluation.py 的调用必需字段存在性校验；显式 output=null/cwd=null 仍有效。
QA 原有缺失字段失败测试必须原样保留；增加调用必需字段缺失矩阵及入口中文错误/退出码回归。
新运行写 results/exp002；保留 exp001 和失败 QA，不覆盖历史证据。
辅助：EXP-002 文档、README、注册表与发布评估条件按 QA 同步。
SCOPE_EXCEPTION：产物/报告/索引同步超过文件数软预算；无新增产品模块和依赖。
不扩展检测模型、数据标签、重放模板、生产数据范围或职业材料。

## 验收

- AC-801：删除任一调用必需字段时，创建输出目录前抛出中文 ValueError；CLI 退出 2，无 traceback。
- AC-802：显式 null 与真实失败/历史错误保持既有语义；原标签不变，既有 BUG-001 两项测试通过。
- AC-803：新被测版本上独立实际运行两次评估，预测与汇总一致，QA 重新从原始跨度/执行报告计算所有指标与分母。
- AC-804：完整 pytest、Ruff、实际重放集成、两套挑战集、inspect/analyze CLI、评估入口通过；只有 QA 可确认 VERIFIED_FIXED 并授权注册。

## 验证、风险、交接

Fast Gate：pytest tests/test_evaluation.py tests/test_evaluation_qa.py；对抗缺失字段、显式 null、无覆盖输出。
Full Gate：pytest -q；ruff check src tests examples experiments；重放集成；挑战集；关键 CLI；两次 evaluate；独立 verify_metrics.py。
所有命令、cwd、环境、退出码、日志、源码/配置/数据/结果哈希写本轮 evidence。
人工受控评估不是泛化结果；不宣称生产优化收益。Developer 只能标记 FIXED_UNVERIFIED，交 QA 独立判定。
