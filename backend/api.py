from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

# === Existing NLP Engine (DO NOT TOUCH) ===
from nlp_engine import match_interest, match_skills, match_job

# === HuggingFace + Rule-based Engine ===
from hf_engine import hf_match_careers

# ---------------------------
# Initialize Flask app
# ---------------------------
app = Flask(
    __name__,
    static_folder="../frontend",      # optional: serve your frontend
    static_url_path="/"               # root URL serves frontend
)
CORS(app)

# ==================================================
# 🔍 EXISTING SEARCH
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

    # Remove duplicates by career name
    unique = {c["name"]: c for c in results}
    return jsonify(list(unique.values()))


# ==================================================
# 🤖 HF + RULE-BASED SEARCH
# ==================================================
@app.route("/hf-search", methods=["POST"])
def hf_search():
    """
    Input JSON:
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
# 🏠 ROOT / HEALTH CHECK
# ==================================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "success", "message": "Career Explorer API is running ✅"})


# ==================================================
# 🚀 RUN SERVER (DEV + PROD SAFE)
# ==================================================
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true"
    )
