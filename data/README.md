# 输入数据

已有数据保留在根目录 `swe-bench-top11/`，不移动或复制整个数据集。
入口为 `swe-bench-top11/manifest.json`，数据目录内分为 trajs、patches 等产物。
可优先定点检查 `swe-bench-top11/01_20260217_mini-v2.0.0_claude-4-5-opus-high/trajs/`。
其中 preds.json 是按实例索引的预测汇总，不应直接当作 messages 轨迹。

清单包含上游成绩与下载统计，尚未审计，不能作为 TraceOpt 实验指标。
选定测试样本后记录原路径、哈希、格式、来源与最小化方法。
本目录用于后续项目输入说明与标注数据，不重复存放原始大数据。

## 首轮固定样本

路径与 SHA-256 见 [来源记录](../tests/fixtures/provenance.json)。
读取到的 trajectory_format 为 mini-swe-agent-1.1，与下载目录中的 agent v2.0.0 标识不同。
人工夹具只借鉴结构，不复制原样本正文；真实样本不移动，集成测试直接只读访问。

## 第二轮来源

[CLI 来源记录](../tests/fixtures/cli_sources.json) 固定 Gemini、DeepSeek 和 GPT 的同一任务样本。
前两者沿用消息结构；GPT Responses API 的固定 response/output/function_call 结构已支持，未知输出类型仍明确拒绝。

## 依赖挑战集

[challenges/dependency_v1.json](challenges/dependency_v1.json) 包含人工标注的资源冲突与屏障案例，附标签理由。
仅验证词法依赖模型，不是端到端优化机会或性能评估数据。

## 循环挑战集

[challenges/loops_v1.json](challenges/loops_v1.json) 为人工设计、逐例说明理由的受控结构循环挑战集。
标签引用完整连续调用 ID 序列；标注依据为成功 NUL 枚举、显式上下文、依赖屏障与模板匹配。
后续输出不作为结构标签依据，历史错误和仓库变化可使检测正例重放失败。
每例提供候选片段初始仓库，不执行轨迹中的未知或写命令。不是生产模型采样或独立留出集。
## ??????????

???????????????????????????????????? `data/samples/real/`???????????? SHA-256?????????? `tests/fixtures/provenance.json`?`tests/fixtures/cli_sources.json` ???? `swe-bench-top11/` ?????????????????
