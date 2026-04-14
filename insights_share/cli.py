from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

from insights_share.client import baseline_query, install_client, load_client, silent_query
from insights_share.server import start_server
from insights_share.wiki_store import WikiItemDraft, WikiStore


DEFAULT_RUNTIME = Path(".insights-share")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="insights-share")
    subparsers = parser.add_subparsers(dest="tool", required=True)

    server_parser = subparsers.add_parser("insights-wiki-server")
    server_parser.add_argument("--start", action="store_true")
    server_parser.add_argument("--ui", action="store_true")
    server_parser.add_argument("--host", default="0.0.0.0")
    server_parser.add_argument("--port", type=int, default=8765)
    server_parser.add_argument("--wiki-root", type=Path, default=Path("demos/insights-share/demo_codes/wiki"))
    server_parser.add_argument("--seed-demo", action="store_true")

    client_parser = subparsers.add_parser("insights-wiki")
    client_parser.add_argument("--install", action="store_true")
    client_parser.add_argument("--server", default="http://127.0.0.1:8765")
    client_parser.add_argument("--config", type=Path, default=DEFAULT_RUNTIME / "client.json")
    client_parser.add_argument("--question")
    client_parser.add_argument("--baseline", action="store_true")
    client_parser.add_argument("--print-json", action="store_true")

    return parser


def seed_demo_data(store: WikiStore) -> None:
    if store.list_items():
        return
    store.create_item(
        WikiItemDraft(
            wiki_type="database",
            slug="postgres-concurrency",
            title="Postgres 并发等待排查",
            problem="事务阻塞导致 lock timeout、吞吐下降和请求排队。",
            triggers=["lock timeout", "事务阻塞", "高并发排队", "pg_locks"],
            positive_examples=["先看阻塞链，再确认锁类型与热点事务。"],
            negative_examples=["直接扩大连接池。"],
            raw_logs=["postgres/postgres-concurrency-session.jsonl"],
            status="reviewed",
        )
    )
    store.create_item(
        WikiItemDraft(
            wiki_type="database",
            slug="postgres-io",
            title="Postgres 磁盘读取 IO 排查",
            problem="缓存未命中或慢盘导致读 IO 激增。",
            triggers=["iops", "read io", "shared buffers miss"],
            positive_examples=["先区分缓存未命中和底层慢盘。"],
            negative_examples=["看到 IO 高就立刻扩容。"],
            raw_logs=["postgres/postgres-io.txt"],
            status="reviewed",
        )
    )
    store.create_item(
        WikiItemDraft(
            wiki_type="agent",
            slug="context-injection-boundary",
            title="共享 insight 注入边界",
            problem="把底层日志原样塞进上下文会挤爆有效工作区，导致 agent 失焦。",
            triggers=["上下文过长", "无差别粘贴日志", "prompt 噪声高"],
            positive_examples=["只注入高层经验和判定依据，原始日志保留链接。"],
            negative_examples=["把整段导出日志直接塞给下游 agent。"],
            raw_logs=["agent/context-injection.txt"],
            status="reviewed",
        )
    )
    store.create_item(
        WikiItemDraft(
            wiki_type="agent",
            slug="with-without-demo-method",
            title="With / Without 对比演示方法",
            problem="没有基线对照时，PM 无法判断共享 insight 是否真的带来提升。",
            triggers=["需要展示效果差异", "PM review", "validation"],
            positive_examples=["同题材分别录制 without 和 with 两条证据链。"],
            negative_examples=["只有接入后的单边演示，没有基线。"],
            raw_logs=["agent/with-without-demo.txt"],
            status="reviewed",
        )
    )


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.tool == "insights-wiki-server":
        store = WikiStore(args.wiki_root)
        if args.seed_demo:
            seed_demo_data(store)
        handle = start_server(store=store, host=args.host, port=args.port)
        if args.ui:
            print(f"dashboard: http://{args.host if args.host != '0.0.0.0' else '127.0.0.1'}:{handle.port}/ui")
        if args.start or args.ui:
            print(f"server listening on http://{args.host}:{handle.port}")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                handle.shutdown()
                return 0
        parser.error("insights-wiki-server requires --start or --ui")

    if args.tool == "insights-wiki":
        if args.install:
            config = install_client(args.server, args.config)
            print(json.dumps(asdict(config), ensure_ascii=False, indent=2))
            return 0
        if args.question:
            result = baseline_query(args.question) if args.baseline else silent_query(args.question, load_client(args.config))
            if args.print_json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(result["injection"] if result["triggered"] else "[no-insight]")
            return 0
        parser.error("insights-wiki requires --install or --question")
    return 0


def main() -> None:
    raise SystemExit(run(sys.argv[1:]))


if __name__ == "__main__":
    main()
