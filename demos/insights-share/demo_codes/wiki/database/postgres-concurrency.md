<!-- INSIGHTS_SHARE_META
{
  "wiki_type": "database",
  "slug": "postgres-concurrency",
  "title": "Postgres 并发等待排查",
  "problem": "事务阻塞导致 lock timeout、吞吐下降和请求排队。",
  "triggers": [
    "lock timeout",
    "事务阻塞",
    "高并发排队",
    "pg_locks"
  ],
  "positive_examples": [
    "先看阻塞链，再确认锁类型与热点事务。"
  ],
  "negative_examples": [
    "直接扩大连接池。"
  ],
  "raw_logs": [
    "postgres/postgres-concurrency-session.jsonl"
  ],
  "status": "reviewed",
  "review_notes": [],
  "merged_from": [],
  "created_at": "2026-04-14T03:35:42+00:00",
  "updated_at": "2026-04-14T03:35:42+00:00",
  "version": 1
}
-->

# Postgres 并发等待排查

## 问题描述
事务阻塞导致 lock timeout、吞吐下降和请求排队。

## 触发时机
- lock timeout
- 事务阻塞
- 高并发排队
- pg_locks

## 正例
- 先看阻塞链，再确认锁类型与热点事务。

## 反例
- 直接扩大连接池。

## 原始日志
- `raw_logs/postgres-concurrency-session.jsonl` <- `postgres/postgres-concurrency-session.jsonl`