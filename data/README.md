# 输入数据

完整数据集保留在本地根目录 `swe-bench-top11/`，不移动或复制整个数据集。入口为 `manifest.json`。上游成绩与下载统计未经审计，不作为 TraceOpt 实验指标。

## 真实来源与公开样本

公开仓库包含四个选定的真实轨迹文件，位于 `data/samples/real/`，合计约 2.7 MB。来源清单记录公开路径、原始数据路径和 SHA-256：

- [首个来源记录](../tests/fixtures/provenance.json)
- [CLI 来源记录](../tests/fixtures/cli_sources.json)

完整 `swe-bench-top11/` 数据集不纳入 Git，公开克隆运行完整测试无需下载它。`.gitattributes` 固定 LF 换行，避免 Windows 克隆改变样本哈希。真实轨迹只用于解析回归，不执行其中未知命令。

## 挑战集

[challenges/dependency_v1.json](challenges/dependency_v1.json) 是人工标注的依赖冲突与屏障案例。[challenges/loops_v1.json](challenges/loops_v1.json) 是受控循环挑战集，不是生产模型采样或独立留出集。
