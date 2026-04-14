from pathlib import Path

from insights_share.retrieval import InsightRetriever
from insights_share.wiki_store import WikiItemDraft, WikiStore


def test_retriever_prioritizes_semantically_relevant_item(tmp_path: Path) -> None:
    store = WikiStore(tmp_path / "wiki")
    store.create_item(
        WikiItemDraft(
            wiki_type="database",
            slug="postgres-concurrency",
            title="Postgres 并发等待排查",
            problem="事务阻塞导致超时和吞吐下降。",
            triggers=["lock timeout", "并发请求排队", "pg_locks"],
            positive_examples=["先看阻塞链，再定位热点事务。"],
            negative_examples=["直接扩大连接池。"],
            raw_logs=["postgres/session-1.jsonl"],
        )
    )
    store.create_item(
        WikiItemDraft(
            wiki_type="frontend",
            slug="css-layout",
            title="布局抖动排查",
            problem="容器尺寸变化导致页面抖动。",
            triggers=["CLS", "layout shift"],
            positive_examples=["先测量首屏资源尺寸。"],
            negative_examples=["把所有动画都删掉。"],
            raw_logs=["frontend/layout.txt"],
        )
    )

    retriever = InsightRetriever(store)
    result = retriever.query("Postgres 高并发下 lock timeout 怎么排查")

    assert result.triggered is True
    assert result.matches[0].slug == "postgres-concurrency"
    assert "阻塞链" in result.injection


def test_retriever_can_reject_irrelevant_question(tmp_path: Path) -> None:
    store = WikiStore(tmp_path / "wiki")
    store.create_item(
        WikiItemDraft(
            wiki_type="database",
            slug="postgres-io",
            title="Postgres IO 读取排查",
            problem="磁盘读取 IO 激增。",
            triggers=["shared buffers miss", "read io", "iops"],
            positive_examples=["先分辨缓存未命中和慢盘。"],
            negative_examples=["看到 IO 高就立刻扩容。"],
            raw_logs=["postgres/io.txt"],
        )
    )

    retriever = InsightRetriever(store, trigger_threshold=0.25)
    result = retriever.query("团队周会怎么主持更高效")

    assert result.triggered is False
    assert result.matches == []
    assert result.reason == "no_relevant_insight"
