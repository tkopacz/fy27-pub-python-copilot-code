import re
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import BadRequest, RequestEntityTooLarge

from triage.contracts import InvalidClassification
from triage.providers import Classifier, ProviderError, build_classifier
from triage.service import triage_report


ROOT = Path(__file__).resolve().parent.parent


def create_app(classifier: Classifier | None = None) -> Flask:
    load_dotenv(ROOT / ".env", override=False)
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 16_384
    provider = classifier if classifier is not None else build_classifier()

    @app.get("/")
    def index():
        return render_template("index.html", mode=provider.mode)

    @app.get("/health")
    def health():
        return jsonify(status="ok", mode=provider.mode, model_connectivity="not_checked")

    @app.errorhandler(BadRequest)
    def invalid_json(_error):
        return jsonify(error="Invalid JSON body."), 400

    @app.errorhandler(RequestEntityTooLarge)
    def too_large(_error):
        return jsonify(error="Request body exceeds 16 KiB."), 413

    @app.post("/api/triage")
    def triage():
        if not request.is_json:
            return jsonify(error="Content-Type must be application/json."), 415
        payload = request.get_json()
        if not isinstance(payload, dict) or set(payload) != {"text", "store_id"}:
            return jsonify(error="Expected exactly text and store_id."), 400
        text, store_id = payload["text"], payload["store_id"]
        if not isinstance(text, str) or not 1 <= len(text.strip()) <= 4000:
            return jsonify(error="text must contain 1-4000 characters."), 400
        if not isinstance(store_id, str) or not re.fullmatch(r"store-\d{3}", store_id):
            return jsonify(error="store_id must match store-001."), 400
        try:
            result = triage_report(text.strip(), store_id, provider)
        except (ProviderError, InvalidClassification) as exc:
            app.logger.warning("Triage rejected: %s", type(exc).__name__)
            return jsonify(error=str(exc)), 502
        return jsonify(result)

    return app
