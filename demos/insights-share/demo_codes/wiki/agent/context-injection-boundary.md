<!-- INSIGHTS_SHARE_META
{
  "wiki_type": "agent",
  "slug": "context-injection-boundary",
  "title": "共享 insight 注入边界",
  "problem": "把底层日志原样塞进上下文会挤爆有效工作区，导致 agent 失焦。",
  "triggers": [
    "上下文过长",
    "无差别粘贴日志",
    "prompt 噪声高"
  ],
  "positive_examples": [
    "只注入高层经验和判定依据，原始日志保留链接。"
  ],
  "negative_examples": [
    "把整段导出日志直接塞给下游 agent。"
  ],
  "raw_logs": [
    "agent/context-injection.txt"
  ],
  "status": "reviewed",
  "review_notes": [],
  "merged_from": [],
  "created_at": "2026-04-14T03:35:42+00:00",
  "updated_at": "2026-04-14T03:35:42+00:00",
  "version": 1
}
-->

# 共享 insight 注入边界

## 问题描述
把底层日志原样塞进上下文会挤爆有效工作区，导致 agent 失焦。

## 触发时机
- 上下文过长
- 无差别粘贴日志
- prompt 噪声高

## 正例
- 只注入高层经验和判定依据，原始日志保留链接。

## 反例
- 把整段导出日志直接塞给下游 agent。

## 原始日志
- `raw_logs/context-injection.txt` <- `agent/context-injection.txt`