from __future__ import annotations

import math
import re
from dataclasses import asdict
from dataclasses import dataclass
from typing import Iterable

from insights_share.wiki_store import WikiItem, WikiStore


WORD_RE = re.compile(r"[a-z0-9_]+|[\u4e00-\u9fff]{1,}", re.IGNORECASE)


def _normalize_tokens(text: str) -> list[str]:
    raw = [match.group(0).lower() for match in WORD_RE.finditer(text)]
    tokens: list[str] = []
    for token in raw:
        if re.fullmatch(r"[\u4e00-\u9fff]+", token):
            tokens.extend(token[i : i + 2] for i in range(max(1, len(token) - 1)))
            tokens.append(token)
        else:
            tokens.append(token)
    expanded: list[str] = []
    for token in tokens:
        expanded.append(token)
        if token in {"postgres", "pg"}:
            expanded.extend(["database", "postgresql"])
        if token in {"pg_locks", "pglock", "locks"}:
            expanded.extend(["lock", "timeout", "阻塞", "阻塞链", "事务"])
        if token in {"lock", "timeout", "阻塞"}:
            expanded.extend(["并发", "阻塞链", "事务"])
        if token in {"io", "iops"}:
            expanded.extend(["磁盘", "缓存"])
    return expanded


def _weighted_text(item: WikiItem) -> str:
    return "\n".join(
        [
            item.title,
            item.title,
            item.problem,
            item.problem,
            " ".join(item.triggers),
            " ".join(item.triggers),
            " ".join(item.positive_examples),
            " ".join(item.negative_examples),
            item.wiki_type,
        ]
    )


@dataclass(slots=True)
class RetrievalMatch:
    slug: str
    wiki_type: str
    title: str
    score: float
    problem: str

    @classmethod
    def from_item(cls, item: WikiItem, score: float) -> "RetrievalMatch":
        return cls(
            slug=item.slug,
            wiki_type=item.wiki_type,
            title=item.title,
            score=round(score, 4),
            problem=item.problem,
        )


@dataclass(slots=True)
class RetrievalResult:
    triggered: bool
    matches: list[RetrievalMatch]
    injection: str
    reason: str

    def to_dict(self) -> dict:
        return {
            "triggered": self.triggered,
            "matches": [asdict(match) for match in self.matches],
            "injection": self.injection,
            "reason": self.reason,
        }


class InsightRetriever:
    def __init__(self, store: WikiStore, trigger_threshold: float = 0.18) -> None:
        self.store = store
        self.trigger_threshold = trigger_threshold

    def query(self, question: str, top_k: int = 3) -> RetrievalResult:
        candidates = self.store.list_items()
        if not candidates:
            return RetrievalResult(False, [], "", "empty_wiki")
        question_tokens = _normalize_tokens(question)
        if not question_tokens:
            return RetrievalResult(False, [], "", "empty_query")
        scored = [(item, self._score(question_tokens, item)) for item in candidates]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        best_score = scored[0][1]
        if best_score < self.trigger_threshold:
            return RetrievalResult(False, [], "", "no_relevant_insight")
        matches = [RetrievalMatch.from_item(item, score) for item, score in scored[:top_k] if score >= self.trigger_threshold]
        best_item = scored[0][0]
        injection = self._build_injection(best_item)
        return RetrievalResult(True, matches, injection, "matched")

    def _score(self, question_tokens: Iterable[str], item: WikiItem) -> float:
        item_tokens = _normalize_tokens(_weighted_text(item))
        if not item_tokens:
            return 0.0
        question_set = set(question_tokens)
        item_set = set(item_tokens)
        overlap = len(question_set & item_set)
        if overlap == 0:
            return 0.0
        precision = overlap / len(item_set)
        recall = overlap / len(question_set)
        f1 = 2 * precision * recall / (precision + recall)
        domain_boost = 0.06 if item.wiki_type in question_set or "database" in question_set and item.wiki_type == "database" else 0.0
        title_boost = 0.04 if any(token in set(_normalize_tokens(item.title)) for token in question_set) else 0.0
        return min(1.0, f1 + domain_boost + title_boost + math.log1p(overlap) / 20)

    def _build_injection(self, item: WikiItem) -> str:
        positives = "；".join(item.positive_examples[:2])
        negatives = "；".join(item.negative_examples[:1])
        return (
            f"命中共享 insight《{item.title}》：先按 {positives} 执行。"
            f"避免 {negatives}。问题背景：{item.problem}"
        )
