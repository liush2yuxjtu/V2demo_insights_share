<!-- INSIGHTS_SHARE_META
{
  "wiki_type": "database",
  "slug": "postgres-io",
  "title": "Postgres 磁盘读取 IO 排查",
  "problem": "缓存未命中或慢盘导致读 IO 激增。",
  "triggers": [
    "iops",
    "read io",
    "shared buffers miss"
  ],
  "positive_examples": [
    "先区分缓存未命中和底层慢盘。"
  ],
  "negative_examples": [
    "看到 IO 高就立刻扩容。"
  ],
  "raw_logs": [
    "postgres/postgres-io.txt"
  ],
  "status": "reviewed",
  "review_notes": [],
  "merged_from": [],
  "created_at": "2026-04-14T03:35:42+00:00",
  "updated_at": "2026-04-14T03:35:42+00:00",
  "version": 1
}
-->

# Postgres 磁盘读取 IO 排查

## 问题描述
缓存未命中或慢盘导致读 IO 激增。

## 触发时机
- iops
- read io
- shared buffers miss

## 正例
- 先区分缓存未命中和底层慢盘。

## 反例
- 看到 IO 高就立刻扩容。

## 原始日志
- `raw_logs/postgres-io.txt` <- `postgres/postgres-io.txt`