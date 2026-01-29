import os
import json
import re

# ==============================
# 🔹 Config
# ==============================
DATASET_PATH = "../datasets"

# ==============================
# 🔹 Cache variable
# ==============================
_cached_careers = None

# ==============================
# 🔹 Load all careers (lazy-load & cache)
# ==============================
def load_all_careers():
    global _cached_careers
    if _cached_careers is not None:
        return _cached_careers  # return cached data

    all_careers = []
    for file in os.listdir(DATASET_PATH):
        if file.endswith(".json"):
            with open(os.path.join(DATASET_PATH, file), "r", encoding="utf-8") as f:
                data = json.load(f)
                category = data.get("category", "")
                for career in data.get("careers", []):
                    # attach category to each career
                    career["category"] = category
                    all_careers.append(career)

    _cached_careers = all_careers  # cache it
    return all_careers

# ==============================
# 🔹 Normalize text
# ==============================
def normalize_text(text):
    if not text:
        return ""
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    return text.strip().lower()

# ==============================
# 🔹 Matching functions
# ==============================
def match_interest(interest):
    interest_norm = normalize_text(interest)
    results = []
    for c in load_all_careers():
        category_norm = normalize_text(c.get("category", ""))
        if interest_norm in category_norm:
            results.append(c)
    return results

def match_skills(skills):
    skills_list = [s.strip().lower() for s in skills.split(",")]
    results = []
    for c in load_all_careers():
        career_skills = [s.lower() for s in c.get("related_skills", [])]
        if any(skill in career_skills for skill in skills_list):
            results.append(c)
    return results

def match_job(job):
    job_lower = normalize_text(job)
    return [
        c for c in load_all_careers()
        if job_lower in normalize_text(c.get("name", ""))
    ]
