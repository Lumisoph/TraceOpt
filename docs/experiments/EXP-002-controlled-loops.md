# EXP-002：受控循环检测与实际重放

状态：verified，经 [iter_008 QA](../../iterations/iter_008/QA_REPORT.md) 独立复跑与重算，已登记 EXP-002。数据标签、计分规则与实验范围未改变。

## 问题与方法

在人工设计的受控结构案例中，前缀来源和依赖屏障能否减少仅看连续模板的误报？
结构命中与实际执行一致性是否必须分开检查？
数据为 [loops_v1.json](../../data/challenges/loops_v1.json)，配置为 [eval_v1.json](../../configs/eval_v1.json)。
使用同一输入比较 production、naive、no_dependency_guard；消融只关闭中间依赖屏障。
完整标注策略与计分定义见 [评估架构](../architecture/evaluation.md)。

## 复现和身份

在仓库根执行 `.venv/Scripts/python.exe experiments/evaluate.py configs/eval_v1.json 新输出目录`。
需要 Python 与本机 Bash/cat/find；Windows 本轮使用 Git 自带工具。
原始开发产物：[manifest](../../results/exp002/manifest.json)、[raw](../../results/exp002/raw.json)、
[summary](../../results/exp002/summary.json)。无 Git commit，manifest 保存源码、配置和数据哈希。
QA 已完成独立复跑与重算；正式数字来自 [注册表](../../results/registry.yaml)。

## 失败案例

| 案例 | 失败机制 | 应查看的证据 |
|---|---|---|
| L014 | 原始/优化输出相同但与历史不符，successful=false | [执行报告](../../results/exp002/L014/replay-0.json) |
| L015 | 初始仓库含额外文件，重放枚举与前缀列表不一致 | [结果](../../results/exp002/L015/result.json) |
| L016 | 历史消费者返回失败，不满足成功读取前提 | [结果](../../results/exp002/L016/result.json) |
| L017 | 历史 raw_output 缺失，不能核验记录 | [结果](../../results/exp002/L017/result.json) |
| L033 | 中间 touch 写绑定文件，去掉依赖屏障产生误报 | [三种预测](../../results/exp002/L033/result.json) |
| L018 | find 失败；朴素基线只看模板仍预测循环 | [三种预测](../../results/exp002/L018/result.json) |

这些失败属于刻意设计的挑战案例，不是发现后隐藏的排除项。
全部生产 cat 候选的重放错误保留在分母，非 cat 明确单列不适用。

## 结论边界

数据按当前契约设计，不提供生产模型上的泛化精度，也不测 LLM 成本、时延或任务成功率。
基线与消融仅比较检测，不执行其不满足生产安全检查的候选。
当前真实生产轨迹正例覆盖仍不足，需保持此限制。

## 已验证受控结果

以下数值复制自注册表 EXP-002，不能推广为生产精度。

| 方法 | TP | FP | FN | P | R | F1 |
|---|---|---|---|---|---|---|
| production | 17 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| naive | 16 | 24 | 1 | 0.4000 | 0.9412 | 0.5614 |
| no_dependency_guard | 17 | 7 | 0 | 0.7083 | 1.0000 | 0.8293 |

生产 cat 重放尝试 12 个，成功 8 个、失败 4 个，成功率 66.6667%；另有 5 个非 cat 候选不适用。
