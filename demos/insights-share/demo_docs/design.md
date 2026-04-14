# insights-share Design

## 目标

这个 demo 证明共享 insight 可以被组织成局域网 wiki，并以 CLI-first、静默热加载的方式接入日常 agent 工作流。

## 系统边界

- 服务端：`insights-wiki-server`
  - 在局域网提供条目托管、管理 UI、生命周期操作、检索接口。
- 客户端：`insights-wiki`
  - 只保存连接信息，不缓存 insight 内容。
  - 新问题到来时默认执行 `SILENT_AND_JUST_RUN`。

## 四层 wiki 结构

1. `wiki_type_index.json`
2. `wiki/<type>/INDEX.md`
3. `wiki/<type>/<item>.md`
4. `wiki/<type>/raw_logs/*`

每条 insight 都包含：

- 问题描述
- 触发时机
- 正例
- 反例
- 原始日志链接

## 最小实现策略

- 标准库优先的 Python 实现，降低 demo 环境耦合。
- 服务端每次查询都从 wiki 文件读取最新内容，保证热加载语义。
- 客户端安装只写入 server 连接信息，不存储条目数据。
- 检索先用轻量 token overlap + 领域扩展做语义近似，后续可替换为更强检索器。

## 生命周期

- 新增：`POST /api/items`
- 编辑：`PUT /api/items`
- 删除：`DELETE /api/items`
- 审阅：`POST /api/review`
- 未触发标记：`POST /api/dormant`
- 合并旧版：`POST /api/merge`

## 验证口径

- 20 个用例
- 10 个应触发，10 个不应触发
- 12 个训练集，8 个测试集
- with / without 双证据链

## 演示主线

1. 启动 `insights-wiki-server --start --ui`
2. 安装 `insights-wiki --install`
3. 输入 without 问题，保留基线
4. 输入 with 问题，展示静默触发与注入
5. 运行评测脚本，生成 `validation_linear.html`
