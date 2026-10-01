# iter_015 计划

状态：已冻结，进入 development。

## 核心闭环

校正轨迹解析与重放边界的产品叙述，使 GPT Responses API 的已验证支持、工具重放的真实能力和 LLM 对话重放的未覆盖范围在架构文档、README、声明与交接状态中一致。

## 交付物

1. 更新 `docs/architecture/canonical_ir.md`，准确描述 Responses API 的归一化规则、严格拒绝未知项及事件顺序。
2. 更新 `CLAIMS.md`、README 和相关文档，明确当前 replay 是确定性的工具执行重放，不启动 LLM，也不复现模型采样过程。
3. 清理 `PROJECT_STATE.md` 中已过期的 iter013 失败叙述，保留 BUG-002 已修复的证据链。
4. 增加文档一致性检查，确保固定真实来源、当前状态和能力枚举不再互相矛盾。

## 验收标准

- 文档不再声称 GPT `response.output` 不支持。
- 文档明确区分 trajectory parsing、tool replay 与 LLM conversation replay。
- 不修改 `src/` 与 `tests/` 产品实现；本轮不新增能力声明，不改变 EXP-002。
- Fast Gate：文档链接检查、关键字符串检查、全量 pytest 与 Ruff 通过。

## 范围边界

本轮不实现 LLM 调用、模型采样复现或新的 replay 执行器；这些属于后续独立需求，不能由当前工具重放证据推导出来。
