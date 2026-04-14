import json
from pathlib import Path
from urllib import request

from insights_share.client import ClientConfig, baseline_query, install_client, silent_query
from insights_share.server import ServerHandle, start_server
from insights_share.wiki_store import WikiItemDraft, WikiStore


def _post_json(url: str, payload: dict) -> dict:
    raw = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=raw, method="POST", headers={"Content-Type": "application/json"})
    with request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def test_install_and_silent_query_hits_live_server(tmp_path: Path) -> None:
    store = WikiStore(tmp_path / "wiki")
    store.create_item(
        WikiItemDraft(
            wiki_type="database",
            slug="postgres-concurrency",
            title="Postgres 并发等待排查",
            problem="事务阻塞导致 lock timeout。",
            triggers=["lock timeout", "事务阻塞", "高并发"],
            positive_examples=["先定位阻塞链和锁等待。"],
            negative_examples=["先重启数据库。"],
            raw_logs=["postgres/concurrency.jsonl"],
        )
    )

    server: ServerHandle = start_server(store=store, host="127.0.0.1", port=0)
    try:
        base_url = f"http://127.0.0.1:{server.port}"
        config_path = tmp_path / "client.json"

        config = install_client(
            server_url=base_url,
            config_path=config_path,
            mode="SILENT_AND_JUST_RUN",
        )

        assert isinstance(config, ClientConfig)
        assert config_path.exists()

        result = silent_query(
            question="Postgres 出现 lock timeout 应该先看什么",
            config=config,
        )

        assert result["triggered"] is True
        assert result["matches"][0]["slug"] == "postgres-concurrency"
    finally:
        server.shutdown()


def test_server_accepts_item_creation_via_http(tmp_path: Path) -> None:
    store = WikiStore(tmp_path / "wiki")
    server = start_server(store=store, host="127.0.0.1", port=0)
    try:
        base_url = f"http://127.0.0.1:{server.port}"
        created = _post_json(
            f"{base_url}/api/items",
            {
                "wiki_type": "database",
                "slug": "postgres-memory",
                "title": "Postgres 内存排查",
                "problem": "内存参数不合理导致计划抖动。",
                "triggers": ["shared buffers", "work_mem"],
                "positive_examples": ["把执行计划和缓存命中率一起看。"],
                "negative_examples": ["只盯单条 SQL。"],
                "raw_logs": ["postgres/memory.txt"],
            },
        )

        assert created["item"]["slug"] == "postgres-memory"
        items = store.list_items("database")
        assert [item.slug for item in items] == ["postgres-memory"]
    finally:
        server.shutdown()


def test_baseline_query_stays_disabled() -> None:
    result = baseline_query("Postgres 高并发下 lock timeout 怎么排查")

    assert result["triggered"] is False
    assert result["reason"] == "insight_disabled"
