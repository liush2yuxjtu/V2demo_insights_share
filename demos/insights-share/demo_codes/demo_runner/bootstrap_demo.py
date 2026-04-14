import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from insights_share.cli import seed_demo_data
from insights_share.wiki_store import WikiStore


def main() -> None:
    root = Path(__file__).resolve().parents[1] / "wiki"
    store = WikiStore(root)
    seed_demo_data(store)
    print(f"seeded demo wiki at {root}")


if __name__ == "__main__":
    main()
