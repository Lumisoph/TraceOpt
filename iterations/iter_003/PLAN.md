# iter_003 计划

状态：已冻结。需求：REQ-003、REQ-004。里程碑：M2。
核心闭环：显式 cwd 的单条命令 → 白名单语义 → 保守路径读写 Effect。
不实现依赖、重写、执行或新增轨迹格式；不宣称分析结果直接证明可安全执行。

## 接口与支持范围

新增 semantics.py：analyze_command(command, *, cwd) 返回冻结 CommandEffect，含
command、argv、cwd、reads、writes、unknown、reason。路径为规范 POSIX 绝对路径，
资源表示该路径及其子树，后续依赖分析必须按祖先/后代重叠比较，不能仅比较字符串相等。
不支持时 unknown=True 且 reason 为中文；消费者必须把 unknown 当作全局屏障。

支持明确形式：cat FILE...；head/tail [-n N] FILE...；wc [-l|-w|-c] FILE...；
sort FILE；uniq FILE；grep [-n|-i|-F] PATTERN FILE...；
rg --no-config --no-ignore [-n|-i|-F] PATTERN FILE...；ls [-a|-l|-la] PATH...；
find PATH -type f；touch FILE...；mkdir [-p] PATH...；rm [-f] FILE...；cp SRC DST；mv SRC DST。
至少十种命令，每种都有正反例。无操作数的 stdin 形式拒绝；不支持的选项拒绝。
为避免隐式配置，rg 必须含上述两个选项，并保守读取 cwd 子树。
引用用 shlex 解析；任何 shell 控制符、展开符、反斜杠、注释或换行（即使被引用）均保守拒绝。
单独 -- 可结束选项，文件名仍不得是 -，且不接收 /dev、/proc、/sys 等特殊资源路径。
所有命令只做静态分析，不触及真实文件系统。

## 模型边界

词法路径模型假定普通 POSIX 文件/目录，无符号链接、硬链接、别名函数、外部并发修改，
固定环境且无输入输出到特殊设备。该模型不能解决这些假设的真实性；未来重放必须检查。
不建模 atime、locale、umask 等环境效果。touch 读写同一路径，cp 读源写目标，
mv 读源且写源与目标，mkdir/rm 写指定路径；目录范围使用保守子树解释。
未知情况的空集合不是无副作用。

## 验收

AC-301：上述命令形式提取预期读写路径，至少十个命令的参数化正例。
AC-302：相对路径、引号空格、重复路径、绝对路径、.. 规范化且不依赖宿主 Windows cwd。
AC-303：未知工具、非法选项、stdin、展开、管道、重定向、命令替换、设备路径全为 unknown。
AC-304：未执行命令、未读写被分析路径；对抗测试证实副作用标记不产生。
AC-305：既有轨迹及 CLI 全部回归通过。

修改路径：src/traceopt/semantics.py、__init__.py、tests/test_semantics.py、
两份架构文档、README、IMPACT_MAP、当前轮产物。
SCOPE_EXCEPTION：交接与文档计入后超过八个文件；仅新增一个功能模块。
Fast Gate：.venv/Scripts/python.exe -m pytest -q；-m ruff check src tests；
-m traceopt inspect tests/fixtures/trajectory.json。最高 VERIFIED_LOCAL，不宣布里程碑完成。
