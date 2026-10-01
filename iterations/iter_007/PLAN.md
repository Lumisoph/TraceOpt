# iter_007 计划

状态：冻结。角色：Planner。核心闭环：可复现挑战集评估与证据注册。
需求：REQ-010、REQ-011；回归 REQ-006～009、REQ-012、REQ-014。

## 范围

建立一个 evaluation 模块、至少 40 个明确标注的受控轨迹案例、固定配置及执行入口。
比较生产检测器、朴素连续同模板基线、仅关闭枚举后依赖屏障的消融。
生产检测接口始终启用屏障；消融仅由评估内部入口调用。
精确循环调用 ID 序列为计分单位，保存逐例真值、预测、TP/FP/FN 和总体 P/R/F1。
对生产预测中的 cat 候选执行已有重放器，保存每次报告或错误；失败不移除分母。
非 cat 候选单独记录不适用，空分母用 null，禁止记作 100%。
挑战集为人工设计受控案例，不冒充模型生产分布；不计算模型成本或速度收益。
辅助任务：评估文档、至少四个具体失败案例、可复现 README 和正式结果注册。

## 非目标

不扩展任意 Bash、GPT 嵌套格式、在线模型执行、统计泛化结论和职业材料。
不改变现有检测默认策略、重放安全边界与验收语义。

## 修改路径与预算

新增 src/traceopt/evaluation.py；修改 binding.py 以共享唯一算法的私有消融开关。
新增 tests/test_evaluation.py、data/challenges/loops_v1.json、configs/eval_v1.json。
新增 experiments/evaluate.py；更新 evaluation 架构、数据说明、README、实验文档。
结果写入 results/exp001，QA 复跑独立目录，收尾依据 QA 注册。
SCOPE_EXCEPTION：超过 8 文件软预算；数据、配置、原始结果、QA、索引各自承担证据职责。
仅新增一个产品模块，不引入依赖。

## 验收

- AC-701：至少 40 个唯一 ID、独立人工标签与逐例中文理由；正负例覆盖合法循环、来源缺失、失败来源、NUL/顺序/重复、上下文变化、写入/unknown 屏障、插入调用或用户消息。
- AC-702：三种方法共享输入；生产与消融仅依赖屏障这一因素不同。精确跨度计分正确，重复预测不重复计分；空分母 null；保存所有逐例结果与分母。
- AC-703：实际执行所有生产 cat 预测，错误及不成功均进入尝试分母；非 cat 明确不适用；报告包含输出与仓库状态证据。标注检测与重放成功独立。
- AC-704：新目录独占输出；固定配置、数据和被测代码哈希、工具哈希、命令与环境可追溯；两次运行的预测与汇总指标相同。
- AC-705：至少四个具体失败案例有来源、机制、真实预测/执行证据与适用边界；QA 核验后才登记 verified 和对外数字。

## 验证

Fast Gate：.venv/Scripts/python.exe -m pytest -q tests/test_evaluation.py tests/test_binding.py tests/test_binding_qa.py
对抗：重复 ID/非法路径输入、零预测与零真值、重放报错保留分母、生产屏障始终启用。
Full Gate：完整 pytest；Ruff check src tests examples experiments；重放集成；两套挑战集；inspect/analyze CLI；评估入口两次实际运行。
工作目录均为仓库根，完整命令与退出码写 evidence/qa_execution.json。

## 风险与交接

受控案例不是随机样本，不能用其分数推断生产收益。目录枚举顺序可能影响重放，失败如实记录。
修改绑定内部后 runtime_binding/determinism 撤销当前验证，历史证据保留，待 QA 重验。
Developer 交付逐项报告与代码身份给 QA；QA 不修改实现；失败也交 Finalizer 保存。
