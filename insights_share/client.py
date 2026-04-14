from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib import request


@dataclass(slots=True)
class ClientConfig:
    server_url: str
    mode: str
    installed_at: str


def install_client(server_url: str, config_path: Path, mode: str = "SILENT_AND_JUST_RUN") -> ClientConfig:
    with request.urlopen(f"{server_url}/health") as response:
        health = json.loads(response.read().decode("utf-8"))
    if not health.get("ok"):
        raise RuntimeError("server health check failed")
    config = ClientConfig(
        server_url=server_url.rstrip("/"),
        mode=mode,
        installed_at=datetime.now(UTC).replace(microsecond=0).isoformat(),
    )
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(asdict(config), ensure_ascii=False, indent=2), encoding="utf-8")
    return config


def load_client(path: Path) -> ClientConfig:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return ClientConfig(**payload)


def silent_query(question: str, config: ClientConfig) -> dict:
    payload = json.dumps({"question": question}).encode("utf-8")
    req = request.Request(
        f"{config.server_url}/api/query",
        method="POST",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))
    result["mode"] = config.mode
    return result


def baseline_query(question: str) -> dict:
    return {
        "triggered": False,
        "matches": [],
        "injection": "",
        "reason": "insight_disabled",
        "mode": "WITHOUT_SHARED_INSIGHT",
        "question": question,
    }
