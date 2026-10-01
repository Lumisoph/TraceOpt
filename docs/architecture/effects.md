# 读写效果

## 摘要

状态：VERIFIED_FULL（iter_004 支持矩阵和词法模型范围内）。实现位于 src/traceopt/semantics.py。

## 职责

描述已支持命令的读写资源和未知副作用。

## 不负责的内容

不承担相邻模块职责；具体边界随冻结计划明确。

## 输入

单条命令文本与显式 POSIX 绝对 cwd，使用白名单解析结果。

## 输出

CommandEffect.reads 与 writes 路径元组，附 unknown 与中文 reason。

## 数据结构

CommandEffect：command、argv、cwd、reads、writes、unknown、reason。所有字段不可变。

## 算法

先拒绝 shell 控制和展开字符，再用 shlex 分词；按白名单校验选项和操作数，
用 posixpath 规范化路径并保序去重。unknown 必须由消费者当作全局屏障。

## 不变量

未知副作用不能等价于空读写集合。

## 假设

只建模普通 POSIX 路径，无符号链接、硬链接、命令别名、特殊设备或外部并发写入；
假设固定标准命令环境。未建模 atime、locale、umask 及临时目录等环境效果。
这些假设必须由未来重放验证，Effect 本身不是可安全执行的证明。

## 错误处理

不支持的语法和路径返回 unknown=True 及中文原因；不会执行命令或访问被分析路径。

## 复杂度

时间与命令长度、路径字符总数线性相关；内存保存分词与去重后的路径。

## 已知限制

不支持 shell 组合、重定向、展开、反斜杠、注释、隐式 stdin 或任意选项。
即使被引用的控制字符也保守拒绝，因此可能拒绝实际上安全的字面量。
rg 必须显式 --no-config --no-ignore，并保守读取 cwd 子树。

## 测试策略

tests/test_semantics.py 覆盖支持矩阵、路径、未知语法与只分析不执行的边界。
结论见 [iter_003 QA](../../iterations/iter_003/QA_REPORT.md)。

## 关联需求

REQ-004，见 [需求](../../REQUIREMENTS.md)。

## 关联 ADR

当前无 Accepted ADR，见 [决策索引](../decisions/INDEX.md)。

## 面试备注

仅可在已验证的词法路径模型范围内描述实现；对外表述见 [CLAIMS](../../CLAIMS.md)。

## 资源重叠契约

每个路径资源覆盖该路径及其子树。未来依赖分析必须比较祖先/后代关系，
例如 ls /repo 与 touch /repo/a 冲突；不得只比较路径字符串相等。
该表示有意过度近似，可能产生额外依赖。unknown 的空集合不等于无副作用。

路径中被 .. 消去的目录另记入 reads；例如 rm a/../b 读取 a 的可达性并写 b，避免归一化丢失依赖。
