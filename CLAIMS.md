# 对外声明注册表

已有下列经 QA 验证的声明；适用范围和限制必须随声明保留。
仅 VERIFIED_FULL 或附明确适用范围的 VERIFIED_LOCAL 可用于最终简历。
性能数字另须引用 results/registry.yaml 中 status: verified 的条目。

## 新声明模板

```text
编号：CLAIM-NNN
声明：
状态：PLANNED
适用范围与限制：
证据：测试路径、QA 报告及章节；数字附实验编号
允许措辞：
禁止措辞：
```

模板不是正式声明；Finalizer 仅在 QA 提供新结论时登记。

## CLAIM-001

声明：基于文件读写 Effect 构建带资源证据的 RAW/WAR/WAW 依赖，并保守处理未知调用。

状态：VERIFIED_FULL

适用范围：显式 POSIX 工作目录、普通路径子树模型；不覆盖文件别名、环境副作用及控制依赖。

证据：

- [tests/test_dependency.py](tests/test_dependency.py)
- [tests/test_dependency_integration.py](tests/test_dependency_integration.py)
- [tests/test_dependency_challenges.py](tests/test_dependency_challenges.py)
- [iterations/iter_004/QA_REPORT.md](iterations/iter_004/QA_REPORT.md)

允许措辞：在明确的路径模型假设下，实现带资源证据的工具调用依赖分析与未知调用屏障。

禁止措辞：完整恢复任意 Bash 程序依赖，或仅凭无依赖边证明可安全并行。

## CLAIM-002

声明：从可见路径枚举与首调用构造运行时绑定计划，并验证未来信息隔离。

状态：VERIFIED_LOCAL

适用范围：人工轨迹中的 NUL 路径枚举与单文件只读模板；固定真实样本无此类正例，不证明未来 LLM 意图。

证据：

- [tests/test_binding.py](tests/test_binding.py)
- [tests/test_binding_integration.py](tests/test_binding_integration.py)
- [tests/test_binding_qa.py](tests/test_binding_qa.py)
- [iterations/iter_005/QA_REPORT.md](iterations/iter_005/QA_REPORT.md)

允许措辞：在受限路径枚举模式上实现前缀可见的参数绑定，并以对抗测试验证不使用未来输出。

禁止措辞：证明任意工具调用可程序化，或证明真实模型后续动作与执行结果必然等价。

## CLAIM-003

声明：对受限 cat 循环生成可执行批处理，并比较原始和优化执行的逐项结果及仓库状态。

状态：VERIFIED_LOCAL

适用范围：受控真实工具执行，单文件 cat 模板、明确初始状态与无别名普通路径；不是模型端到端成本实验。

证据：

- [tests/test_replay.py](tests/test_replay.py)
- [tests/test_replay_integration.py](tests/test_replay_integration.py)
- [tests/test_replay_qa.py](tests/test_replay_qa.py)
- [iterations/iter_006/QA_REPORT.md](iterations/iter_006/QA_REPORT.md)
- [iterations/iter_006/evidence/live_capture/report.json](iterations/iter_006/evidence/live_capture/report.json)

允许措辞：在受限读取循环上，通过实际重放核对逐项输出、退出码、历史记录和仓库状态。

禁止措辞：证明任意 Bash 优化正确，或宣称已经测得模型调用成本下降。

## 明确边界

以上声明只覆盖各自列出的验证范围。trajectory parsing、tool replay 与 LLM conversation replay 是三个不同对象；当前没有 LLM 调用、采样复现或完整模型会话重放证据。


