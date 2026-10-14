import pytest

from analyzer import classify
from app import create_app


class FakeAnalyzer:
    """Keyword-based stand-in so tests run without downloading the model."""

    model_name = "fake"

    def analyze(self, text):
        t = text.lower()
        if "love" in t or "great" in t:
            return classify(0.95, 0.03, 0.02)
        if "hate" in t or "awful" in t:
            return classify(0.02, 0.08, 0.90)
        return classify(0.44, 0.31, 0.25)


@pytest.fixture
def client(tmp_path):
    app = create_app(analyzer=FakeAnalyzer(), db_path=str(tmp_path / "test.db"))
    app.testing = True
    return app.test_client()


def test_classify_thresholds():
    assert classify(0.9, 0.05, 0.05).label == "POSITIVE"
    assert classify(0.1, 0.1, 0.8).label == "NEGATIVE"
    assert classify(0.15, 0.65, 0.2).label == "NEUTRAL"
    # A weak positive lean is reported as neutral...
    weak = classify(0.44, 0.31, 0.25)
    assert weak.label == "NEUTRAL"
    assert weak.confidence == 0.44
    # ...unless the threshold is lowered.
    assert classify(0.44, 0.31, 0.25, threshold=0.4).label == "POSITIVE"


def test_analyze_saves_result(client):
    res = client.post("/api/analyze", json={"text": "  I love this product  "})
    assert res.status_code == 201
    body = res.get_json()
    assert body["label"] == "POSITIVE"
    assert body["text"] == "I love this product"
    assert body["id"] == 1
    assert client.get("/api/history").get_json()["items"][0]["id"] == 1


def test_analyze_validates_input(client):
    assert client.post("/api/analyze", json={}).status_code == 400
    assert client.post("/api/analyze", json={"text": "   "}).status_code == 400
    assert client.post("/api/analyze", json={"text": "x" * 2001}).status_code == 400
    assert client.post("/api/analyze", data="not json").status_code == 400


def test_batch_and_stats(client):
    res = client.post("/api/analyze/batch", json={"texts": ["Great day", "Awful service", "It is Tuesday"]})
    assert res.status_code == 201
    assert [r["label"] for r in res.get_json()["results"]] == ["POSITIVE", "NEGATIVE", "NEUTRAL"]

    stats = client.get("/api/stats").get_json()
    assert stats["total"] == 3
    assert stats["counts"] == {"POSITIVE": 1, "NEGATIVE": 1, "NEUTRAL": 1}

    assert client.post("/api/analyze/batch", json={"texts": []}).status_code == 400
    assert client.post("/api/analyze/batch", json={"texts": ["ok"] * 21}).status_code == 400


def test_history_filter_delete_and_clear(client):
    for text in ["I love it", "I hate it", "I love that too"]:
        client.post("/api/analyze", json={"text": text})

    positives = client.get("/api/history?label=positive").get_json()["items"]
    assert [p["text"] for p in positives] == ["I love that too", "I love it"]
    assert client.get("/api/history?label=happy").status_code == 400
    assert client.get("/api/history?limit=abc").status_code == 400

    assert client.delete(f"/api/history/{positives[0]['id']}").status_code == 204
    assert client.delete(f"/api/history/{positives[0]['id']}").status_code == 404
    assert len(client.get("/api/history").get_json()["items"]) == 2

    assert client.delete("/api/history").get_json() == {"deleted": 2}
    assert client.get("/api/stats").get_json()["total"] == 0
