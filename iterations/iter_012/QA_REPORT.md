# iter_012 QA 报告

状态：completed。结论：passed。`0.1.0` 本地发布候选包通过独立验证。

## 证据

- [执行记录](evidence/qa_execution.json)：构建产物文件、源码哈希、命令和退出码。
- 新虚拟环境安装 wheel 后，`traceopt.__file__` 位于 site-packages，版本元数据为 `0.1.0`，退出 0。
- 包内完整 pytest、Ruff、真实 replay demo、EXP-002 评估和独立指标复算均退出 0。
- wheel 与 sdist 中 9 个 Python 文件逐字节匹配工作区 `src/traceopt`；包中无本地大数据集或临时证据目录。
- 注册表 EXP-002 的源码哈希、数据哈希和配置哈希仍匹配。

## 判定

AC-1201～1204 全部通过。版本从开发版封为 `0.1.0`，但本轮只生成本地候选包，未上传、打 tag 或发布外部仓库。
既有功能限制仍然有效：GPT 嵌套格式、任意 Bash、生产模型泛化和端到端成本收益均未声明支持。

```yaml
iteration: 12
verdict: passed
gate: full
capabilities:
  release_package: VERIFIED_FULL
defects: []
experiments: {}
release_candidate: VERIFIED_FULL
published_externally: false
```
