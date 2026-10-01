# iter_019 计划

状态：已冻结，进入 development。

## 核心目标

把 v0.1 发布候选的文档与分发证据恢复为可读、可复现、可审计的状态，确保项目可以按当前发布条件对外呈现。

## 当前证据与缺口

- RELEASE_CRITERIA 的能力项均有历史 QA 或 EXP-002 证据，当前不新增能力。
- iter_018 QA 已验证 333 项测试、Ruff、CLI 和受限重放，但收尾审计仍暴露 `README.md`、`CLAIMS.md`、`PROJECT_INDEX.md` 中的字面量 `` `r`n ``。
- iter_017 QA 报告包含损坏的问号占位文本，且未保存可读的构建/安装证据目录；不能单独作为本轮发布候选的强证据。
- `dist/` 中已有 0.1.0 wheel/sdist，需重新构建并在干净临时环境核对包内源码身份和 CLI。

## 相关需求

- REQ-012：pytest、Ruff、CLI、可复现 README 和发布检查。
- REQ-014：状态、索引、角色产物与证据链一致。
- RELEASE_CRITERIA：只补强已有发布条件证据，不改变能力勾选或 EXP-002。

## 必须完成

1. 修复权威文档中的字面量换行占位，并扩展一致性检查防止其回归。
2. 重新构建 0.1.0 wheel/sdist，记录构建命令、文件哈希和包内 Python 源码哈希。
3. 在新的临时虚拟环境安装 wheel，运行包内 CLI、完整 pytest 和 Ruff；保留可读证据到 `iterations/iter_019/evidence/`。
4. 更新发布候选快照和 CHANGELOG，但不改写历史 QA 报告。

## 明确不做

- 不修改 `src/`、功能测试、实验数据或结果注册表。
- 不实现 LLM conversation replay、任意 Bash 语义、模型成本实验或新 pattern。
- 不把包安装成功扩大为全平台或全数据集兼容。

## 验收标准

- 权威文档不含 `` `r`n ``、`` `n`n ``、损坏标题或过期当前状态。
- `python -m build` 成功生成 0.1.0 wheel/sdist；新临时环境安装成功，`traceopt --help` 成功。
- 完整 `python -m pytest -q`、`python -m ruff check .` 和包身份检查通过，证据含命令、cwd、退出码、文件哈希和源码哈希。
- 受影响回归至少包含文档一致性、轨迹/Responses 和重放集成；至少 1 个对抗检查确认历史失败未被伪装成当前状态。

## 交接

Developer 只修复文档和证据脚本并记录自测；QA 独立执行 Fast/Full Gate 并决定是否通过；Finalizer 仅复制 QA 结论。
