# insights-wiki

## Purpose

客户端 skill。负责安装、连接、静默检索和高层经验注入。

## When To Use

- 用户面对新问题时，希望优先复用团队共享 insight
- 不希望显式管理 insight
- 需要 `SILENT_AND_JUST_RUN` 式后台触发

## Inputs

- 当前用户问题
- 当前工作上下文
- 可访问的 `insights-wiki-server` 地址

## Core Behavior

1. 检查是否已安装并连接到 wiki server
2. 在后台静默检索相关 wiki insight
3. 评估当前问题与 insight 的适用性
4. 只把高层经验注入上下文，不直接倾倒原始日志
5. 默认模式为 `SILENT_AND_JUST_RUN`

## Output Contract

- `triggered`: 是否命中共享 insight
- `matches`: 候选 insight 列表
- `injection`: 注入后的高层建议
- `reason`: 命中或拒绝注入原因

## Example

问题：`Postgres 高并发下 lock timeout 怎么排查`

期望行为：
- 静默命中 `postgres-concurrency`
- 注入“先看阻塞链，再确认锁类型与热点事务”
- 不要求用户额外确认

## Boundaries

- 不负责 server 启动与条目托管
- 不负责管理 UI
- 不长期缓存 insight 内容到本地
