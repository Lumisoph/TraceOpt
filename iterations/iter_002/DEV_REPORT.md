# iter_002 开发报告

状态：completed。CLI：IMPLEMENTED_UNVERIFIED，等待 QA。

## 验收映射

AC-201：console script 与 __main__ 转发同一个 CLI 入口。
AC-202：inspect 统计从 Event 推导，export 直接输出 asdict(Trajectory) 加 schema_version。
AC-203：输出统一 UTF-8；文件模式 x，只创建新文件。
AC-204：中文错误、退出码 2，不输出 traceback；坏输入不创建输出文件。
AC-205：新增固定 Gemini/DeepSeek/GPT 来源；支持样本逐字段核对，GPT 明确拒绝。

## 自测与身份

重新安装可编辑包成功。完整 pytest：51 passed，退出码 0。
首次 Ruff 仅发现一处行长问题，已调整换行；复检通过，退出码 0。
原检查见 [dev_execution](evidence/dev_execution.json)，修复后 Ruff 见 [日志](evidence/dev_ruff_fixed.log)。
最终交付文件身份见 [哈希](evidence/dev_final_hashes.json)。QA 应在最终版本重跑完整测试。
运行环境：Python 3.13.5、Windows、项目 .venv，工作目录 G:/Advance_tool_mining/TraceOpt。

## 变更与限制

新增 cli.py、__main__.py、CLI 测试与来源记录；修改包入口、真实集成测试及相关说明。
没有修改 trajectory.py 的解析语义，没有新运行时依赖。
GPT 嵌套响应仍不支持，不能把来源拒绝测试通过解释为支持该格式。
无性能实验、优化执行或全数据集兼容性结论。
