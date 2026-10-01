# iter_017 计划

状态：已冻结，进入 development。

核心闭环：完成 v0.1 发布候选收尾，统一项目快照与实际验证证据，并重新构建本地发行包。

交付：清理 PROJECT_STATE 过期内容；同步能力快照到 iter_015/当前 329 测试证据；构建 wheel/sdist 并检查安装与哈希；不新增功能，不改变实验注册项。

验收：pytest、Ruff、构建、干净临时环境安装和 CLI inspect 全部通过；文档不得保留 BUG-002 OPEN 或 iter013 失败作为当前状态。
