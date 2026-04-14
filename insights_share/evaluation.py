from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from insights_share.client import ClientConfig, silent_query


@dataclass(slots=True)
class EvaluationCase:
    case_id: str
    split: str
    should_trigger: bool
    question: str
    expected_slug: str | None
    note: str


def load_cases(path: Path) -> list[EvaluationCase]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [EvaluationCase(**entry) for entry in payload["cases"]]


def run_evaluation(config: ClientConfig, cases: list[EvaluationCase]) -> dict:
    rows: list[dict] = []
    for case in cases:
        result = silent_query(case.question, config)
        predicted_slug = result["matches"][0]["slug"] if result["matches"] else None
        passed = result["triggered"] == case.should_trigger
        if case.should_trigger and case.expected_slug:
            passed = passed and predicted_slug == case.expected_slug
        rows.append(
            {
                "case_id": case.case_id,
                "split": case.split,
                "question": case.question,
                "should_trigger": case.should_trigger,
                "triggered": result["triggered"],
                "expected_slug": case.expected_slug,
                "predicted_slug": predicted_slug,
                "passed": passed,
                "reason": result["reason"],
            }
        )
    total = len(rows)
    passed = sum(1 for row in rows if row["passed"])
    triggered_expected = [row for row in rows if row["should_trigger"]]
    no_trigger_expected = [row for row in rows if not row["should_trigger"]]
    hit = sum(1 for row in triggered_expected if row["triggered"])
    true_negative = sum(1 for row in no_trigger_expected if not row["triggered"])
    return {
        "summary": {
            "total": total,
            "passed": passed,
            "accuracy": round(passed / total, 4) if total else 0.0,
            "trigger_recall": round(hit / len(triggered_expected), 4) if triggered_expected else 0.0,
            "non_trigger_accuracy": round(true_negative / len(no_trigger_expected), 4) if no_trigger_expected else 0.0,
        },
        "rows": rows,
    }


def render_validation_html(report: dict) -> str:
    rows_html = "\n".join(
        f"<tr><td>{row['case_id']}</td><td>{row['split']}</td><td>{'Y' if row['should_trigger'] else 'N'}</td><td>{'Y' if row['triggered'] else 'N'}</td><td>{row['expected_slug'] or '-'}</td><td>{row['predicted_slug'] or '-'}</td><td>{'PASS' if row['passed'] else 'FAIL'}</td></tr>"
        for row in report["rows"]
    )
    summary = report["summary"]
    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>validation_linear</title>
    <style>
      body {{ font-family: Georgia, serif; margin: 32px; background: #f7f3e8; color: #1d252a; }}
      table {{ width: 100%; border-collapse: collapse; background: #fff; }}
      th, td {{ border: 1px solid #d9cfb5; padding: 8px 10px; text-align: left; }}
      th {{ background: #efe6d1; }}
      .hero {{ margin-bottom: 24px; }}
    </style>
  </head>
  <body>
    <section class="hero">
      <h1>insights-share validation</h1>
      <p>总用例 {summary['total']}，通过 {summary['passed']}，accuracy {summary['accuracy']}</p>
      <p>trigger recall {summary['trigger_recall']}，non-trigger accuracy {summary['non_trigger_accuracy']}</p>
    </section>
    <table>
      <thead>
        <tr><th>ID</th><th>split</th><th>should trigger</th><th>triggered</th><th>expected</th><th>predicted</th><th>result</th></tr>
      </thead>
      <tbody>
        {rows_html}
      </tbody>
    </table>
  </body>
</html>"""
