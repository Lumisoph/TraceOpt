# iter_023 计划

状态：已冻结，进入 development。

## 核心目标

完成最终发布候选回归，确认发布交接清单、机器状态和一致性测试在迭代收尾后仍保持同步。

## 必须完成

1. 修复一致性测试对当前迭代号的陈旧硬编码，改为当前 iter_023 入口。
2. 独立运行完整 pytest、Ruff、CLI 和发布条件勾选检查。
3. 记录本地发布候选已完成、GitHub 远程动作未执行的最终证据。

## 明确不做

不初始化 Git、不上传远程仓库、不修改 `src/`、实验或结果注册表，不新增产品能力。

## 验收标准

- 完整 pytest 通过，Ruff 和 CLI 通过。
- state、PROJECT_INDEX、PROJECT_STATE 均指向 iter_023 合法阶段。
- RELEASE_CRITERIA 无未勾选项，RELEASE_HANDOFF 明确远程发布边界。

## 交接

Developer 记录修复，QA 独立执行最终回归，Finalizer 完成最后一次状态同步。
