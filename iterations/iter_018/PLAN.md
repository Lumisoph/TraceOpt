# iter_018 计划

状态：已冻结，进入 development。

## 核心目标

恢复 TraceOpt 的权威项目快照与对外文档，使当前已验证能力、Responses API 支持边界、工具重放边界、发布条件和历史失败证据彼此一致，并可按文档复现。

## 当前证据与缺口

- iter_014 QA 已验证固定 Responses `response/output/function_call/function_call_output` 结构、拒绝未知项、保持事件顺序；BUG-002 为 `VERIFIED_FIXED`。
- iter_017 DEV/QA 已记录发布候选测试、Ruff、构建和安装检查，但尚未在机器状态中完成收尾同步。
- `PROJECT_STATE.md`、`PROJECT_INDEX.md` 仍指向 iter_015，并保留“BUG-002 OPEN”等过期叙述。
- `README.md`、`CLAIMS.md`、`docs/architecture/canonical_ir.md` 含损坏的问号占位文本；Canonical IR 架构索引仍使用旧的未验证能力状态。
- 当前目录不是 Git 工作树，版本身份只能继续使用文件 SHA-256；不得声称有 Git commit。

## 相关需求与发布条件

- REQ-001、REQ-002：真实轨迹与 Canonical Event IR 的当前支持范围必须与 iter_014 QA 一致。
- REQ-009：明确工具执行重放与 LLM 对话重放的边界。
- REQ-012、REQ-013、REQ-014：README、声明、状态、索引和证据链必须可复现且状态一致。
- RELEASE_CRITERIA：不新增能力；保留已验证发布条件及其证据路径。

## 必须完成

1. 修复 `docs/architecture/canonical_ir.md` 的可读内容，准确记录 Responses API 归一化、未知项拒绝、事件顺序和 pending 规则。
2. 清理 README、CLAIMS、架构索引、PROJECT_STATE、PROJECT_INDEX 中的损坏占位符和过期状态；明确 trajectory parsing、tool replay 与 LLM conversation replay 的区别。
3. 将 iter_018 作为当前 planning 入口，保留 iter_013/014/017 历史证据，不改写历史报告结论。
4. 建立文档一致性检查，覆盖关键状态、链接、边界措辞和机器状态指向。

## 应该完成

- 在 CHANGELOG 或迭代索引中补充本轮文档/状态同步记录。
- 文档中的正式数字只引用 `results/registry.yaml` 的 `verified` 条目。

## 明确不做

- 不修改 `src/`、`tests/`、实验数据或 EXP-002 注册项。
- 不实现 LLM 调用、模型采样复现、任意 Bash 重放或新的 pattern/adapter。
- 不删除历史失败报告，不把工具重放证据扩大为 LLM conversation replay 或模型成本收益。

## 需要读取的文件

- `AGENTS.md`、`.traceopt/workflow.yaml`、`.traceopt/state.yaml`
- `REQUIREMENTS.md`、`RELEASE_CRITERIA.md`、`IMPACT_MAP.md`
- `PROJECT_STATE.md`、`PROJECT_INDEX.md`、`CLAIMS.md`、`README.md`
- `docs/architecture/{canonical_ir,overview,replay,INDEX}.md`
- `iterations/iter_014/QA_REPORT.md`、`iterations/iter_017/{PLAN,DEV_REPORT,QA_REPORT}.md`
- `results/registry.yaml`

## 开发任务

1. 由 Developer 按本计划修复权威文档和项目快照，先读取 `IMPACT_MAP.md`，保持已验证实现不变。
2. 增加只读文档一致性测试/检查脚本，验证链接存在、关键状态唯一、边界措辞存在且无损坏占位符。

## 验收标准

- `rg` 检查权威文档不再出现损坏问号占位符、BUG-002 当前 OPEN 或 iter_015 作为当前入口。
- Canonical IR 文档准确描述固定 Responses 支持和未知项拒绝；README/CLAIMS 不宣称 LLM conversation replay、任意 Bash 等未验证能力。
- `.traceopt/state.yaml`、PROJECT_STATE、PROJECT_INDEX、iterations/INDEX 的当前入口均指向 iter_018，并保持状态枚举合法。
- 文档链接检查、针对性一致性检查、完整 `python -m pytest -q`、`python -m ruff check .` 和关键 CLI 检查均通过；结果记录在 iter_018 QA 报告。

## 对抗与回归

- 搜索历史 iter_013 失败报告时，历史文件仍保留，但当前快照不得将其当作现状。
- 搜索 `response.output` 时，只有支持边界或历史报告可出现，不得出现“当前不支持”的矛盾表述。
- 检查 LLM replay、任意 Bash、成本收益等禁止扩大声明。

## 风险

- 历史文档中的损坏字符可能来自文件本身而非编码显示，必须以字节内容检查并重写为 UTF-8。
- 当前无 Git 仓库，QA 必须记录工作目录、文件哈希和命令，不能依赖 commit。

## 交接条件

Developer 交付文档变更、检查脚本、自测命令和未完成项后进入 QA；Developer 不得宣告 VERIFIED。QA 仅依据可复现命令更新通过/失败结论，随后交给 Finalizer 同步快照。
