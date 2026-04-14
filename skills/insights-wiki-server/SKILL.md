# insights-wiki-server

## Purpose

服务端 skill。负责局域网托管、管理 wiki 条目、暴露 dashboard 与检索接口。

## When To Use

- 需要在局域网里托管共享 insights
- 需要新增、编辑、删除、审阅、合并 wiki 条目
- 需要为客户端 `insights-wiki` 提供检索服务

## Inputs

- wiki 四层结构内容
- 条目生命周期操作请求
- 客户端检索请求

## Core Behavior

1. 启动 server 并对局域网可达
2. 提供 dashboard / UI
3. 管理 wiki 四层结构：
   - `wiki_type_index`
   - 类型 `INDEX.md`
   - `wiki_item.md`
   - 原始日志 `jsonl/txt`
4. 支持生命周期操作：
   - 新增
   - 编辑
   - 删除
   - 调研
   - 审阅
   - 合并旧版本
   - 未触发标记但不遗忘
5. 对客户端提供检索与热加载能力

## Output Contract

- server 地址
- dashboard 地址
- CRUD 结果
- 检索结果

## Example

启动：
- `insights-wiki-server --start`
- `insights-wiki-server --ui`

期望行为：
- dashboard 可访问
- wiki 条目可被新增并立即参与检索

## Boundaries

- 不负责客户端注入时机
- 不负责最终 with/without 对比报告撰写
