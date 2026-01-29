import os
import json
import torch
from sentence_transformers import SentenceTransformer, util

# ---------------------------
# CONFIG
# ---------------------------
DATASET_DIR = "../datasets"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
SIMILARITY_THRESHOLD = 0.35

# ---------------------------
# LOAD MODEL (ONCE)
# ---------------------------
model = SentenceTransformer(MODEL_NAME)

# ---------------------------
# LOAD DATASETS (ONCE)
# ---------------------------
all_careers = []

for file in os.listdir(DATASET_DIR):
    if file.endswith(".json"):
        with open(os.path.join(DATASET_DIR, file), "r", encoding="utf-8") as f:
            data = json.load(f)
            category = data.get("category", "")
            for c in data.get("careers", []):
                c["category"] = category
                all_careers.append(c)

# ---------------------------
# BUILD TEXT & EMBEDDINGS (ONCE)
# ---------------------------
career_texts = []
career_embeddings = []

for career in all_careers:
    skills = []

    req = career.get("required_skills", {})
    for level in req.values():
        skills.extend(level)

    skills.extend(career.get("related_skills", []))

    text = " ".join(
        skills + [
            career.get("category", ""),
            career.get("name", "")
        ]
    )

    career_texts.append(text.lower())

with torch.no_grad():
    career_embeddings = model.encode(
        career_texts,
        normalize_embeddings=True,
        show_progress_bar=False
    )

# ---------------------------
# MAIN MATCH FUNCTION (API SAFE)
# ---------------------------
def hf_match_careers(interest=None, skills=None, job=None):
    """
    Supports:
    - single input
    - multiple inputs
    - comma separated
    - up to 9+ keywords
    """

    parts = []
    if interest:
        parts.append(interest)
    if skills:
        parts.append(skills)
    if job:
        parts.append(job)

    if not parts:
        return []

    user_input = " ".join(parts).lower()
    keywords = [k.strip() for k in user_input.split(",") if k.strip()]

    # ---------------------------
    # RULE-BASED FILTER (FAST)
    # ---------------------------
    candidates = []
    candidate_embeddings = []

    for idx, text in enumerate(career_texts):
        if any(k in text for k in keywords):
            candidates.append(all_careers[idx])
            candidate_embeddings.append(career_embeddings[idx])

    if not candidates:
        return []

    # ---------------------------
    # SEMANTIC MATCH (TRANSFORMER)
    # ---------------------------
    with torch.no_grad():
        user_embedding = model.encode(
            user_input,
            normalize_embeddings=True
        )

    scores = util.cos_sim(user_embedding, candidate_embeddings)[0]

    results = []
    for i, score in enumerate(scores):
        if score.item() >= SIMILARITY_THRESHOLD:
            results.append((score.item(), candidates[i]))

    results.sort(key=lambda x: x[0], reverse=True)
    return [r[1] for r in results]