# TraceOpt v0.1.0 发布交接清单

状态：**源码已发布到 GitHub main；安装包仍仅在本地验证。**

仓库：[Lumisoph/TraceOpt](https://github.com/Lumisoph/TraceOpt)。
首次源码发布提交：`881c38a688da9245637b381c67e0949c98d9bf87`。
发布后复现与文档同步证据见 [iter_024 QA](iterations/iter_024/QA_REPORT.md)。

## 版本身份

- 项目：`traceopt`
- 版本：`0.1.0`（见 [pyproject.toml](pyproject.toml)）
- 原始开发工作区仍不含 .git；发布克隆保留 Git commit，历史包证据使用 SHA-256。
- 构建清单：[iter_019 dist_manifest.json](iterations/iter_019/evidence/dist_manifest.json)
- wheel 源码逐文件身份：[package_identity.json](iterations/iter_019/evidence/package_identity.json)

## 可上传产物

| 文件 | SHA-256 | 用途 |
|---|---|---|
| `dist/traceopt-0.1.0-py3-none-any.whl` | `881efd39dfa3be0389a9e95fdf1405f7b2ef2afc980d95070f11a114d63f2c96` | Python 安装包 |
| `dist/traceopt-0.1.0.tar.gz` | `04d0878c0c112e716ae6d7035100e3da46fb6bdd9593d7e6e7ecca84d0631ff1` | 源码分发包 |

上传前必须重新计算哈希；若不同，保留旧证据并重新执行发布 QA。

## 已验证命令

在项目根目录执行：

```powershell
python -m build
python -m pytest -q
python -m ruff check .
python -m traceopt --help
```

独立 wheel 环境的 333 项测试、Ruff 和 CLI 证据见 [iter_019 QA](iterations/iter_019/QA_REPORT.md)。工作区最新状态快照检查见 [iter_020 QA](iterations/iter_020/QA_REPORT.md)，发布审计见 [iter_021 QA](iterations/iter_021/QA_REPORT.md)。

## 发布后可使用的表述

可以说：TraceOpt 在明确的词法路径模型和受限 cat 模板上实现了轨迹解析、依赖分析、前缀绑定、可执行改写与状态重放，并有对应 QA/实验证据。

不能说：已上传 GitHub Release 或 PyPI 安装包、支持任意 Bash、复现 LLM conversation、证明模型成本下降、覆盖全数据集或证明生产泛化。

## 外部动作

源码已推送到上述仓库的 main。未创建 GitHub Release，未上传 wheel/sdist 或发布 PyPI；
这些安装包发布动作不属于本轮源码公开任务，不以源码推送代替包发布证据。

## 证据入口

- [发布审计](docs/release_audit.md)
- [发布条件](RELEASE_CRITERIA.md)
- [当前状态](PROJECT_STATE.md)
- [正式结果注册表](results/registry.yaml)
- [对外声明](CLAIMS.md)

