from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


META_START = "<!-- INSIGHTS_SHARE_META"
META_END = "-->"


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


@dataclass(slots=True)
class WikiItemDraft:
    wiki_type: str
    slug: str
    title: str
    problem: str
    triggers: list[str]
    positive_examples: list[str]
    negative_examples: list[str]
    raw_logs: list[str]
    status: str = "draft"
    review_notes: list[str] = field(default_factory=list)
    merged_from: list[str] = field(default_factory=list)


@dataclass(slots=True)
class WikiItem(WikiItemDraft):
    created_at: str = field(default_factory=now_iso)
    updated_at: str = field(default_factory=now_iso)
    version: int = 1

    def to_public_dict(self) -> dict[str, Any]:
        return asdict(self)


class WikiStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self._ensure_root_index()

    def create_item(self, draft: WikiItemDraft) -> WikiItem:
        self._ensure_type(draft.wiki_type)
        existing = self.get_item(draft.wiki_type, draft.slug)
        if existing is not None:
            raise ValueError(f"item already exists: {draft.wiki_type}/{draft.slug}")
        item = WikiItem(**asdict(draft))
        self._write_item(item)
        self._refresh_indexes()
        return item

    def list_types(self) -> list[str]:
        index = self._load_json(self.root / "wiki_type_index.json", default={"types": []})
        return [entry["name"] for entry in index["types"]]

    def list_items(self, wiki_type: str | None = None) -> list[WikiItem]:
        types = [wiki_type] if wiki_type else self.list_types()
        items: list[WikiItem] = []
        for current_type in types:
            type_dir = self.root / current_type
            if not type_dir.exists():
                continue
            for path in sorted(type_dir.glob("*.md")):
                if path.name == "INDEX.md":
                    continue
                items.append(self._load_item_file(path))
        return items

    def get_item(self, wiki_type: str, slug: str) -> WikiItem | None:
        path = self._item_path(wiki_type, slug)
        if not path.exists():
            return None
        return self._load_item_file(path)

    def update_item(self, wiki_type: str, slug: str, patch: dict[str, Any]) -> WikiItem:
        item = self.get_item(wiki_type, slug)
        if item is None:
            raise KeyError(f"unknown item: {wiki_type}/{slug}")
        data = item.to_public_dict()
        for key, value in patch.items():
            if key in data and value is not None:
                data[key] = value
        data["updated_at"] = now_iso()
        data["version"] = item.version + 1
        updated = WikiItem(**data)
        self._write_item(updated)
        self._refresh_indexes()
        return updated

    def delete_item(self, wiki_type: str, slug: str) -> None:
        path = self._item_path(wiki_type, slug)
        if not path.exists():
            raise KeyError(f"unknown item: {wiki_type}/{slug}")
        path.unlink()
        self._refresh_indexes()

    def merge_items(self, wiki_type: str, target_slug: str, source_slug: str, note: str) -> WikiItem:
        target = self.get_item(wiki_type, target_slug)
        source = self.get_item(wiki_type, source_slug)
        if target is None or source is None:
            raise KeyError("merge target or source not found")
        merged_from = [*target.merged_from]
        if source.slug not in merged_from:
            merged_from.append(source.slug)
        review_notes = [*target.review_notes, f"merge:{source.slug}:{note}"]
        updated = self.update_item(
            wiki_type,
            target_slug,
            {
                "merged_from": merged_from,
                "review_notes": review_notes,
            },
        )
        self.update_item(
            wiki_type,
            source_slug,
            {
                "status": "merged",
                "review_notes": [*source.review_notes, f"merged_into:{target.slug}:{note}"],
            },
        )
        return updated

    def mark_reviewed(self, wiki_type: str, slug: str, note: str) -> WikiItem:
        item = self.get_item(wiki_type, slug)
        if item is None:
            raise KeyError(f"unknown item: {wiki_type}/{slug}")
        return self.update_item(
            wiki_type,
            slug,
            {
                "status": "reviewed",
                "review_notes": [*item.review_notes, note],
            },
        )

    def mark_dormant(self, wiki_type: str, slug: str, note: str) -> WikiItem:
        item = self.get_item(wiki_type, slug)
        if item is None:
            raise KeyError(f"unknown item: {wiki_type}/{slug}")
        return self.update_item(
            wiki_type,
            slug,
            {
                "status": "dormant",
                "review_notes": [*item.review_notes, note],
            },
        )

    def _ensure_root_index(self) -> None:
        path = self.root / "wiki_type_index.json"
        if not path.exists():
            path.write_text(json.dumps({"types": []}, ensure_ascii=False, indent=2), encoding="utf-8")

    def _ensure_type(self, wiki_type: str) -> None:
        type_dir = self.root / wiki_type
        (type_dir / "raw_logs").mkdir(parents=True, exist_ok=True)
        index_path = type_dir / "INDEX.md"
        if not index_path.exists():
            index_path.write_text(f"# {wiki_type}\n\n", encoding="utf-8")
        self._refresh_indexes()

    def _write_item(self, item: WikiItem) -> None:
        self._ensure_type(item.wiki_type)
        path = self._item_path(item.wiki_type, item.slug)
        meta = json.dumps(item.to_public_dict(), ensure_ascii=False, indent=2)
        body = self._render_markdown(item)
        path.write_text(f"{META_START}\n{meta}\n{META_END}\n\n{body}", encoding="utf-8")
        self._sync_raw_logs(item)

    def _refresh_indexes(self) -> None:
        types: list[dict[str, str]] = []
        for type_dir in sorted(path for path in self.root.iterdir() if path.is_dir()):
            wiki_type = type_dir.name
            items = [
                self._load_item_file(path)
                for path in sorted(type_dir.glob("*.md"))
                if path.name != "INDEX.md"
            ]
            index_path = type_dir / "INDEX.md"
            lines = [f"# {wiki_type}", "", "| slug | title | status |", "| --- | --- | --- |"]
            for item in items:
                lines.append(f"| {item.slug} | {item.title} | {item.status} |")
            index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            types.append({"name": wiki_type, "index": f"{wiki_type}/INDEX.md"})
        (self.root / "wiki_type_index.json").write_text(
            json.dumps({"types": types}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _render_markdown(self, item: WikiItem) -> str:
        raw_log_links = "\n".join(f"- `raw_logs/{Path(log).name.replace('/', '-')}` <- `{log}`" for log in item.raw_logs)
        return "\n".join(
            [
                f"# {item.title}",
                "",
                "## 问题描述",
                item.problem,
                "",
                "## 触发时机",
                *[f"- {entry}" for entry in item.triggers],
                "",
                "## 正例",
                *[f"- {entry}" for entry in item.positive_examples],
                "",
                "## 反例",
                *[f"- {entry}" for entry in item.negative_examples],
                "",
                "## 原始日志",
                raw_log_links or "- 无",
            ]
        )

    def _sync_raw_logs(self, item: WikiItem) -> None:
        raw_dir = self.root / item.wiki_type / "raw_logs"
        for source in item.raw_logs:
            name = source.replace("/", "-")
            target = raw_dir / name
            if not target.exists():
                target.write_text(
                    "\n".join(
                        [
                            '{"event":"source_link"}',
                            json.dumps({"source": source, "item": item.slug}, ensure_ascii=False),
                        ]
                    )
                    + "\n",
                    encoding="utf-8",
                )

    def _item_path(self, wiki_type: str, slug: str) -> Path:
        return self.root / wiki_type / f"{slug}.md"

    def _load_item_file(self, path: Path) -> WikiItem:
        text = path.read_text(encoding="utf-8")
        start = text.index(META_START) + len(META_START)
        end = text.index(META_END, start)
        meta = json.loads(text[start:end].strip())
        return WikiItem(**meta)

    def _load_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

