import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from insights_share.client import load_client
from insights_share.evaluation import load_cases, render_validation_html, run_evaluation


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    project_root = base.parents[2]
    demo_root = base.parents[0]
    config = load_client(project_root / ".insights-share" / "client.json")
    cases = load_cases(base / "fixtures" / "trigger_cases.json")
    report = run_evaluation(config, cases)
    output_json = demo_root / "demo_docs" / "validation_report.json"
    output_html = demo_root / "demo_docs" / "validation_linear.html"
    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    output_html.write_text(render_validation_html(report), encoding="utf-8")
    print(f"wrote {output_json}")
    print(f"wrote {output_html}")


if __name__ == "__main__":
    main()
