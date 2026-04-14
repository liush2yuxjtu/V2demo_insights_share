<!-- INSIGHTS_SHARE_META
{
  "wiki_type": "database",
  "slug": "postgres-memory",
  "title": "Postgres 内存排查",
  "problem": "共享缓冲和 work_mem 配置不合理会让执行计划和延迟抖动。",
  "triggers": [
    "work_mem",
    "shared buffers",
    "缓存命中率"
  ],
  "positive_examples": [
    "先把执行计划和缓存命中率一起看。"
  ],
  "negative_examples": [
    "只盯单条 SQL 文本。"
  ],
  "raw_logs": [
    "postgres/postgres-memory.txt"
  ],
  "status": "draft",
  "review_notes": [],
  "merged_from": [],
  "created_at": "2026-04-14T03:35:57+00:00",
  "updated_at": "2026-04-14T03:35:57+00:00",
  "version": 1
}
-->

# Postgres 内存排查

## 问题描述
共享缓冲和 work_mem 配置不合理会让执行计划和延迟抖动。

## 触发时机
- work_mem
- shared buffers
- 缓存命中率

## 正例
- 先把执行计划和缓存命中率一起看。

## 反例
- 只盯单条 SQL 文本。

## 原始日志
- `raw_logs/postgres-memory.txt` <- `postgres/postgres-memory.txt`