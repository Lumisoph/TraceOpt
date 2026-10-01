# iter_024 DEV_REPORT

状态：completed，交给 QA。

## 变更

- 增加 `.gitattributes`，将文本统一为 LF，避免 Windows 克隆改变真实样本哈希。
- 重写 `data/README.md`，说明四个公开固定样本、完整数据集边界和挑战集限制。
- 为 `provenance.json`、`cli_sources.json` 增加 `original_source`，保留四个源文件的公开路径和原始路径。
- 同步 README、发布审计和发布交接中的 GitHub main 事实；明确未创建 Release、未上传 wheel/sdist 或 PyPI。
- 文档一致性测试改为接受当前轮次，并将数据说明纳入占位检查。

## 自测证据

工作目录：`G:\Advance_tool_mining\TraceOpt`。

- `python -m pytest -q`：334 passed，退出码 0。
- `python -m ruff check src tests examples experiments`：All checks passed，退出码 0。
- `python -m traceopt --help`：退出码 0。
- 四个公开样本 SHA-256 与 fixture 一致：Claude `de243a...0504`、Gemini `e58e50...cba14`、DeepSeek `43b268...cd4cc`、GPT `61513c...bd9be`。

## 限制与交接重点

本报告只记录 Developer 自测，不授予 VERIFIED。请 QA 在独立 Git 克隆中验证：完整 pytest、Ruff、CLI、样本哈希、公开仓库提交、replay_demo 和受控评估；检查克隆中不存在 `swe-bench-top11/` 或临时环境目录。
