from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from insights_share.retrieval import InsightRetriever
from insights_share.wiki_store import WikiItemDraft, WikiStore


@dataclass(slots=True)
class ServerHandle:
    httpd: ThreadingHTTPServer
    thread: threading.Thread
    port: int

    def shutdown(self) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=5)


class InsightRequestHandler(BaseHTTPRequestHandler):
    server_version = "InsightsShare/0.1"

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/ui"}:
            self._write_html(self._render_dashboard())
            return
        if parsed.path == "/health":
            self._write_json({"ok": True, "port": self.server.server_port})
            return
        if parsed.path == "/api/types":
            self._write_json({"types": self.server.store.list_types()})
            return
        if parsed.path == "/api/items":
            query = parse_qs(parsed.query)
            wiki_type = query.get("wiki_type", [None])[0]
            items = [item.to_public_dict() for item in self.server.store.list_items(wiki_type)]
            self._write_json({"items": items})
            return
        if parsed.path.startswith("/raw/"):
            raw_path = self.server.store.root / Path(parsed.path.removeprefix("/raw/"))
            if raw_path.exists() and raw_path.is_file():
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(raw_path.read_bytes())
                return
        self._write_json({"error": "not_found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/items":
            payload = self._read_json()
            item = self.server.store.create_item(WikiItemDraft(**payload))
            self._write_json({"item": item.to_public_dict()}, status=HTTPStatus.CREATED)
            return
        if parsed.path == "/api/query":
            payload = self._read_json()
            result = self.server.retriever.query(payload["question"])
            self._write_json(result.to_dict())
            return
        if parsed.path == "/api/review":
            payload = self._read_json()
            item = self.server.store.mark_reviewed(payload["wiki_type"], payload["slug"], payload["note"])
            self._write_json({"item": item.to_public_dict()})
            return
        if parsed.path == "/api/dormant":
            payload = self._read_json()
            item = self.server.store.mark_dormant(payload["wiki_type"], payload["slug"], payload["note"])
            self._write_json({"item": item.to_public_dict()})
            return
        if parsed.path == "/api/merge":
            payload = self._read_json()
            item = self.server.store.merge_items(
                payload["wiki_type"],
                payload["target_slug"],
                payload["source_slug"],
                payload["note"],
            )
            self._write_json({"item": item.to_public_dict()})
            return
        self._write_json({"error": "not_found"}, status=HTTPStatus.NOT_FOUND)

    def do_PUT(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/items":
            payload = self._read_json()
            item = self.server.store.update_item(payload["wiki_type"], payload["slug"], payload["patch"])
            self._write_json({"item": item.to_public_dict()})
            return
        self._write_json({"error": "not_found"}, status=HTTPStatus.NOT_FOUND)

    def do_DELETE(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/items":
            payload = self._read_json()
            self.server.store.delete_item(payload["wiki_type"], payload["slug"])
            self._write_json({"deleted": True})
            return
        self._write_json({"error": "not_found"}, status=HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(length).decode("utf-8") if length else "{}"
        return json.loads(payload)

    def _write_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        raw = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _write_html(self, html: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        raw = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _render_dashboard(self) -> str:
        items = self.server.store.list_items()
        cards = []
        for item in items:
            raw_links = "".join(
                f'<li><a href="/raw/{item.wiki_type}/raw_logs/{entry.replace("/", "-")}">{entry}</a></li>'
                for entry in item.raw_logs
            )
            cards.append(
                "\n".join(
                    [
                        '<section class="card">',
                        f"<h2>{item.title}</h2>",
                        f"<p><strong>类型:</strong> {item.wiki_type} / <strong>状态:</strong> {item.status}</p>",
                        f"<p>{item.problem}</p>",
                        f"<p><strong>触发:</strong> {' / '.join(item.triggers)}</p>",
                        f"<p><strong>正例:</strong> {' / '.join(item.positive_examples)}</p>",
                        f"<p><strong>反例:</strong> {' / '.join(item.negative_examples)}</p>",
                        f"<ul>{raw_links}</ul>",
                        "</section>",
                    ]
                )
            )
        card_html = "\n".join(cards) or '<p class="empty">当前还没有 wiki-insight 条目。</p>'
        return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>insights-share dashboard</title>
    <style>
      :root {{
        --bg: #f4f1e8;
        --ink: #1f2a2e;
        --panel: #fffaf0;
        --line: #d6c7a3;
        --accent: #8a3b12;
      }}
      body {{
        margin: 0;
        font-family: "Iowan Old Style", "Palatino Linotype", serif;
        color: var(--ink);
        background:
          radial-gradient(circle at top right, rgba(138, 59, 18, 0.18), transparent 28%),
          linear-gradient(180deg, #f7f3e8 0%, var(--bg) 100%);
      }}
      main {{
        max-width: 1080px;
        margin: 0 auto;
        padding: 40px 20px 80px;
      }}
      h1 {{
        margin-bottom: 8px;
        font-size: clamp(2.2rem, 5vw, 4rem);
      }}
      .grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 18px;
        margin-top: 28px;
      }}
      .card {{
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 10px 30px rgba(31, 42, 46, 0.08);
      }}
      .hint {{
        margin-top: 18px;
        padding: 16px 18px;
        background: rgba(255, 250, 240, 0.7);
        border-left: 4px solid var(--accent);
      }}
      .empty {{
        padding: 24px;
        background: rgba(255, 250, 240, 0.8);
        border-radius: 16px;
      }}
      code {{
        font-family: "SFMono-Regular", "Menlo", monospace;
      }}
    </style>
  </head>
  <body>
    <main>
      <p>LAN / CLI-first / hot reload</p>
      <h1>insights-share dashboard</h1>
      <p>所有 insight 条目托管在当前 wiki 根目录，客户端默认只保存连接信息，不缓存 insight 内容。</p>
      <div class="hint">
        <p><strong>管理 API</strong></p>
        <p><code>POST /api/items</code> 新增，<code>PUT /api/items</code> 编辑，<code>DELETE /api/items</code> 删除。</p>
        <p><code>POST /api/review</code> 审阅，<code>POST /api/dormant</code> 标记未触发但保留，<code>POST /api/merge</code> 合并旧版本。</p>
      </div>
      <div class="grid">{card_html}</div>
    </main>
  </body>
</html>"""


def start_server(store: WikiStore, host: str, port: int) -> ServerHandle:
    httpd = ThreadingHTTPServer((host, port), InsightRequestHandler)
    httpd.store = store
    httpd.retriever = InsightRetriever(store)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return ServerHandle(httpd=httpd, thread=thread, port=httpd.server_port)

