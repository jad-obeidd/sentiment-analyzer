"""Flask API for the AI-powered sentiment analyzer."""

from __future__ import annotations

import os

from flask import Flask, jsonify, request
from flask_cors import CORS

from analyzer import MAX_CHARS, DistilBertAnalyzer
from database import Database

VALID_LABELS = {"POSITIVE", "NEGATIVE", "NEUTRAL"}
MAX_BATCH = 20


def create_app(analyzer=None, db_path: str | None = None) -> Flask:
    app = Flask(__name__)
    CORS(app, origins=os.getenv("CLIENT_ORIGIN", "http://localhost:5173"))

    analyzer = analyzer or DistilBertAnalyzer()
    db = Database(db_path or os.getenv("DATABASE_PATH", "sentiment.db"))

    def bad_request(message: str):
        return jsonify({"error": message}), 400

    def validate_text(value):
        if not isinstance(value, str) or not value.strip():
            return None, "Text is required"
        if len(value) > MAX_CHARS:
            return None, f"Text must be at most {MAX_CHARS} characters"
        return value.strip(), None

    @app.get("/api/health")
    def health():
        return jsonify({"ok": True, "model": getattr(analyzer, "model_name", "custom")})

    @app.post("/api/analyze")
    def analyze():
        text, error = validate_text((request.get_json(silent=True) or {}).get("text"))
        if error:
            return bad_request(error)
        result = analyzer.analyze(text)
        return jsonify(db.insert(text, result)), 201

    @app.post("/api/analyze/batch")
    def analyze_batch():
        texts = (request.get_json(silent=True) or {}).get("texts")
        if not isinstance(texts, list) or not texts:
            return bad_request("texts must be a non-empty list")
        if len(texts) > MAX_BATCH:
            return bad_request(f"At most {MAX_BATCH} texts per batch")
        cleaned = []
        for value in texts:
            text, error = validate_text(value)
            if error:
                return bad_request(error)
            cleaned.append(text)
        return jsonify({"results": [db.insert(t, analyzer.analyze(t)) for t in cleaned]}), 201

    @app.get("/api/history")
    def history():
        try:
            limit = max(1, min(int(request.args.get("limit", 20)), 100))
        except ValueError:
            return bad_request("limit must be a number")
        label = request.args.get("label")
        if label and label.upper() not in VALID_LABELS:
            return bad_request("label must be POSITIVE, NEGATIVE or NEUTRAL")
        return jsonify({"items": db.history(limit, label.upper() if label else None)})

    @app.delete("/api/history/<int:analysis_id>")
    def delete_one(analysis_id: int):
        if not db.delete(analysis_id):
            return jsonify({"error": "Not found"}), 404
        return "", 204

    @app.delete("/api/history")
    def clear():
        return jsonify({"deleted": db.clear()})

    @app.get("/api/stats")
    def stats():
        return jsonify(db.stats())

    return app


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    create_app().run(host="127.0.0.1", port=port, debug=os.getenv("FLASK_DEBUG") == "1")
