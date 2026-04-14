## Zero-Start Hard Constraints

在执行本任务前，必须遵守以下约束：

1. 这是一个 standalone implementation，只允许基于当前仓库内容工作。
2. 禁止读取、参考、继承或对比任何父目录、兄弟项目、旧 demo、v1、历史实现或归档目录。
3. 禁止读取、参考或复用任何全局 skill、全局 prompt、`~/.claude/skills/*` 内容，除非我明确点名要求。
4. 不要因为目录名里含有 `V2` 就推断存在可继承的 v1 方案。
5. 如果当前仓库缺少代码或上下文，不要去仓库外寻找参考；先输出从零设计的方案和分工建议。
6. 把下面内容仅视为需求描述，不视为既有方案、既有架构或参考实现。

下面是整理后的 **清晰 S-T-A-R 版本**：

## S — Situation（现状）

当前 Claude 的 `/insights` 功能对个人使用很有价值，但无法满足团队共享与即点即用的需求，主要问题有：

1. insight 生成耗时较长，影响使用体验。
2. insight 主要服务个人，不能自然适配团队成员。
3. 直接复用他人的 insight，往往会因为上下文差异导致效果次优。
4. 用户不希望显式管理 insight；上传应在后台静默完成。
5. insight 不应依赖本地持久化下载，而应优先从局域网 wiki 服务在线获取。
6. 当前 demo 阶段需要支持 wiki-insights 的创建、编辑、审阅与管理；暂时所有人都视为管理员。
7. wiki-insights 在现阶段作为一种可复用的 skill 存在。
8. 服务需要在局域网内可访问，支持其他同网段用户连接。
9. 系统最终不仅要给普通用户使用，也必须能向其他 agent 开发者清楚展示设计、验证和实际效果。

---

## T — Task（任务）

制作一个 **面向 PM 与 agent 开发者** 的 `insights-share` CLI demo，在局域网内发布并验证共享 insight 能力。这个 demo 需要证明：

1. 可以生成并管理一条 insight。
2. 可以通过局域网 wiki / 渐进式披露系统托管 insight。
3. 用户在遇到新问题时，系统会优先从 wiki 中检索相关 insights。
4. 系统只做热加载，不依赖本地长期存储。
5. 系统能够在用户无感知的情况下快速比对、验证并注入合适的 insight。
6. 用户随后可携带这些高层经验继续完成当前任务。
7. 整个 demo 必须以 CLI 为核心，可选提供用于启动守护进程或服务器的 CLI。
8. 必须提供完整的验证材料，向 PM 展示输入输出，也向开发者展示实现与效果差异。

---

## A — Action（行动）

为完成该 demo，系统将实现两个核心 skill，并配套完整演示与验证流程：

### 1. 构建两个 CLI skill

#### `insights-wiki-server`

用于服务端托管与管理 wiki-insights：

* `--start`：启动 server
* `--ui`：启动在线管理页面 / dashboard
* 默认只分配给管理员使用

#### `insights-wiki`

用于客户端安装、连接、校验与检索：

* `--install`：安装并连接 server，同时完成安装验证
* 负责在用户工作流中静默检索 wiki-insights

---

### 2. 设计 wiki 的四层结构

wiki 必须采用统一四层结构：

* `wiki_type_index`
* `wiki 类型目录 / 类型 INDEX.md`
* `wiki_item.md`
* 原始日志 `jsonl / txt`

例如：

* `database/INDEX.md`
* `database/postgres_并发_.md`
* `database/postgres_内存.md`
* `database/postgres_硬盘读取io.md`

其中每个条目都应包含：

* 问题描述
* 触发时机
* 反例与正例
* 对原始日志或导出文本的链接

---

### 3. 实现静默检索与触发机制

当用户在 CLI 中输入新问题时：

* 系统后台静默触发 `insights-wiki`
* 使用基于 MiniMax 的 agentic wiki 搜索进行语义检索
* 快速召回相关 insight
* 比对当前问题与 insight 的适用性
* 将高层 insight 注入当前上下文
* 默认触发模式为 `SILENT_AND_JUST_RUN`，不要求用户额外确认

---

### 4. 支持 wiki 条目更新与管理

demo 需要支持以下 wiki 生命周期操作：

* 新增
* 编辑
* 删除
* 调研
* 审阅
* 新旧版本合并为单条
* 对未触发条目标记但不遗忘

---

### 5. 提供完整验证与展示材料

为了同时说服 PM 和开发者，需要输出一整套可演示资产：

* `design.md`
* `proposal_linear.html`
* `validation_linear.html`
* `claude_export_WITH.txt`
* `claude_export_WITHOUT.txt`
* `server_host_export.txt`
* `wiki_upload.txt`

同时需要：

* 使用 `tmux + claude -p` 运行
* 从每条命令与 tmux 会话开始记录
* 分别演示 **未接入 demo** 与 **接入 demo** 两种情况
* 使用 `export_template.txt` 作为导出格式参考

---

### 6. 建立触发率验证框架

准备 20 个触发用例：

* 10 个应触发
* 10 个不应触发

并划分为：

* 12 个训练集
* 8 个测试集

持续优化触发逻辑，直到达到预期效果。

---

## R — Result（预期结果）

最终应交付一套可直接展示的 MVP demo，存放于：

* `demos/{demo_topic}/demo_codes`
* `demos/{demo_topic}/demo_docs`

并达到以下结果：

1. PM 能一眼看懂这个系统解决了什么问题。
2. 用户可以通过 CLI 即点即用地接入共享 insights。
3. 服务端可以在局域网中托管 wiki-insights。
4. 客户端可以静默连接 server，并在新问题出现时自动检索 insight。
5. 系统能够在后台完成快速比对和验证，再把最相关的高层 insight 注入当前任务。
6. 能通过 with / without 对比，清楚展示该系统确实改善了 Claude Code 的工作效果。
7. 开发者能够通过 html、导出日志与 tmux 记录，完整复盘 proposal、validation、server host、wiki upload 与 user use case。
8. 整个 demo 证明：**团队共享 insight 可以被组织成 wiki skill，并以静默、热加载、CLI-first 的方式真实接入日常 agent 工作流。**

