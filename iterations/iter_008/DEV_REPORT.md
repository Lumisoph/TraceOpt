# iter_008 开发报告

状态：completed，交 QA 验证。

BUG-001 修复：validate_dataset 在读取字段前检查调用必需键集合，缺失立即抛中文 ValueError。
显式 null 仍接受，检测和重放语义不变；未修改任何数据标注与原 QA 失败测试。
新增全部调用字段缺失矩阵、显式 null、实际命令入口退出码/中文消息/无 traceback 回归。
状态仅为 FIXED_UNVERIFIED，evaluation 为 IMPLEMENTED_UNVERIFIED。

[自测执行记录](evidence/dev_execution.json) 保存命令、cwd、环境、退出码与被测文件 SHA-256。
定向 pytest 72 passed，Ruff 通过，实际评估退出码 0；详见 [pytest](evidence/dev_pytest.log)、
[Ruff](evidence/dev_ruff.log)、[评估](evidence/dev_evaluation.log)。
新产物 [results/exp002](../../results/exp002) 独立保存，exp001 和 iter_007 失败证据未覆盖。

验收对应：AC-801 字段验证与实际入口；AC-802 保留原失败测试与 null 语义；
AC-803 已完成开发侧实际评估，待 QA 独立复跑重算；AC-804 待 QA Full Gate。
限制沿用受控数据、生产 cat 重放范围，不新增模型收益结论。
