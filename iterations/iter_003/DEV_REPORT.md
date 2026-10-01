# iter_003 开发报告

状态：completed。command_semantics、effects：IMPLEMENTED_UNVERIFIED。

## 实现与验收

AC-301：semantics.py 支持冻结矩阵中的十五种命令，提供冻结 CommandEffect。
AC-302：显式 POSIX cwd、保序去重、引号空格、-- 文件名与规范路径；
额外保留被 .. 消去的目录可达性读依赖，避免只保留最终路径漏掉前提。
AC-303：不支持语法、隐式 stdin、特殊路径、未知参数统一 unknown 和中文原因。
AC-304：纯字符串分析，没有文件访问或执行调用；touch 标记测试未产生文件。
AC-305：全量既有轨迹和 CLI 回归通过。

## 自测

`.venv/Scripts/python.exe -m pytest -q`：116 passed；Ruff 通过，退出码均为 0。
[执行记录](evidence/dev_execution.json) 保存命令、工作目录、平台、源码与测试哈希。
日志：[pytest](evidence/dev_pytest.log)、[Ruff](evidence/dev_ruff.log)。
Python 3.13.5、Windows、项目 .venv，无新增第三方依赖。
初次检查中的导入排序和字符串转义警告已在开发阶段消除。

## 限制

仅词法路径资源模型；不解决链接、环境、特殊设备、并发修改或执行安全。
unknown 的空路径集合不代表无副作用，未来依赖必须把它当作全局屏障。
未修改 IR、未实现依赖或重放，没有性能实验与对外声明。
