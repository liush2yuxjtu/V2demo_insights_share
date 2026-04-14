from insights_share.client import ClientConfig
from insights_share.evaluation import EvaluationCase, run_evaluation


def test_run_evaluation_summarizes_trigger_and_non_trigger_results(monkeypatch) -> None:
    responses = iter(
        [
            {"triggered": True, "matches": [{"slug": "postgres-concurrency"}], "reason": "matched"},
            {"triggered": False, "matches": [], "reason": "no_relevant_insight"},
        ]
    )

    def fake_silent_query(question: str, config: ClientConfig) -> dict:
        del question, config
        return next(responses)

    monkeypatch.setattr("insights_share.evaluation.silent_query", fake_silent_query)

    report = run_evaluation(
        ClientConfig(server_url="http://demo", mode="SILENT_AND_JUST_RUN", installed_at="2026-01-01T00:00:00+00:00"),
        [
            EvaluationCase(
                case_id="train-01",
                split="train",
                should_trigger=True,
                question="q1",
                expected_slug="postgres-concurrency",
                note="",
            ),
            EvaluationCase(
                case_id="test-01",
                split="test",
                should_trigger=False,
                question="q2",
                expected_slug=None,
                note="",
            ),
        ],
    )

    assert report["summary"]["accuracy"] == 1.0
    assert report["summary"]["trigger_recall"] == 1.0
    assert report["summary"]["non_trigger_accuracy"] == 1.0
