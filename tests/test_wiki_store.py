from pathlib import Path

from insights_share.wiki_store import WikiItemDraft, WikiStore


def test_create_item_builds_four_layer_wiki_structure(tmp_path: Path) -> None:
    store = WikiStore(tmp_path / "wiki")

    item = store.create_item(
        WikiItemDraft(
            wiki_type="database",
            slug="postgres-concurrency",
            title="Postgres 并发等待排查",
            problem="事务等待和锁冲突导致接口抖动。",
            triggers=["出现 lock timeout", "慢 SQL 与高并发同时出现"],
            positive_examples=["先看阻塞链，再看锁类型。"],
            negative_examples=["只盯 CPU 使用率，不看 pg_locks。"],
            raw_logs=["postgres/postgres-concurrency-session.jsonl"],
            status="reviewed",
        )
    )

    assert item.slug == "postgres-concurrency"
    assert (tmp_path / "wiki" / "wiki_type_index.json").exists()
    assert (tmp_path / "wiki" / "database" / "INDEX.md").exists()
    assert (tmp_path / "wiki" / "database" / "postgres-concurrency.md").exists()
    assert (tmp_path / "wiki" / "database" / "raw_logs" / "postgres-postgres-concurrency-session.jsonl").exists()

    loaded = store.get_item("database", "postgres-concurrency")
    assert loaded is not None
    assert loaded.problem == "事务等待和锁冲突导致接口抖动。"
    assert loaded.status == "reviewed"


def test_merge_items_marks_old_item_and_preserves_history(tmp_path: Path) -> None:
    store = WikiStore(tmp_path / "wiki")
    current = store.create_item(
        WikiItemDraft(
            wiki_type="database",
            slug="postgres-memory",
            title="Postgres 内存参数排查",
            problem="共享缓冲和 work_mem 配置不合理。",
            triggers=["频繁磁盘回表"],
            positive_examples=["结合 explain analyze 与缓存命中率。"],
            negative_examples=["只盯单个 SQL 文本。"],
            raw_logs=["postgres/postgres-memory.txt"],
        )
    )
    legacy = store.create_item(
        WikiItemDraft(
            wiki_type="database",
            slug="postgres-memory-legacy",
            title="Postgres 内存旧版经验",
            problem="旧版经验条目。",
            triggers=["老环境升级"],
            positive_examples=["保留背景结论。"],
            negative_examples=["复制旧结论直接套用。"],
            raw_logs=["postgres/postgres-memory-legacy.txt"],
        )
    )

    merged = store.merge_items(
        wiki_type="database",
        target_slug=current.slug,
        source_slug=legacy.slug,
        note="合并旧版经验到主条目",
    )

    assert merged.slug == "postgres-memory"
    assert legacy.slug in merged.merged_from
    old_item = store.get_item("database", "postgres-memory-legacy")
    assert old_item is not None
    assert old_item.status == "merged"
