from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# === Existing engine (DO NOT TOUCH) ===
from nlp_engine import match_interest, match_skills, match_job

# === NEW HuggingFace + Rule-based engine ===
from hf_engine import hf_match_careers

app = Flask(__name__)
CORS(app)

# ==================================================
# 🔍 EXISTING SEARCH (UNCHANGED)
# ==================================================
@app.route("/search", methods=["POST"])
def search():
    data = request.json
    results = []

    if data.get("interest"):
        results.extend(match_interest(data["interest"]))
    if data.get("skills"):
        results.extend(match_skills(data["skills"]))
    if data.get("job"):
        results.extend(match_job(data["job"]))

    # Remove duplicates by job name
    unique = {c["name"]: c for c in results}
    return jsonify(list(unique.values()))


# ==================================================
# 🤖 NEW HF + RULE BASED SEARCH (INDEPENDENT)
# ==================================================
@app.route("/hf-search", methods=["POST"])
def hf_search():
    """
    Takes combined skills + interests text
    Example input:
    {
        "query": "python data analysis research biology"
    }
    """
    data = request.json
    query = data.get("query", "")

    if not query.strip():
        return jsonify([])

    results = hf_match_careers(query)
    return jsonify(results)


# ==================================================
# 🚀 RUN SERVER (DEV SAFE + PROD SAFE)
# ==================================================
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true"
    )