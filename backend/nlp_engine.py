import os
import json
import re

DATASET_PATH = "../datasets"

def load_all_careers():
    """
    Load all careers from all JSON files in the datasets folder.
    Each career dict now includes its 'category' field.
    """
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
    return all_careers

def normalize_text(text):
    """
    Lowercase, remove special characters, and extra spaces for matching.
    """
    if not text:
        return ""
    # Remove non-alphanumeric characters except spaces
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    return text.strip().lower()

def match_interest(interest):
    """
    Match careers based on category.
    - Normalizes input and category names.
    - Matches partial words, ignores special characters like &.
    - Returns all careers where interest is part of category.
    """
    interest_norm = normalize_text(interest)
    results = []
    for c in load_all_careers():
        category_norm = normalize_text(c.get("category", ""))
        # Check if the interest keyword appears anywhere in the category
        if interest_norm in category_norm:
            results.append(c)
    return results

def match_skills(skills):
    """
    Match careers based on skills input.
    Skills are comma-separated.
    """
    skills_list = [s.strip().lower() for s in skills.split(",")]
    results = []
    for c in load_all_careers():
        career_skills = [s.lower() for s in c.get("related_skills", [])]
        if any(skill in career_skills for skill in skills_list):
            results.append(c)
    return results

def match_job(job):
    """
    Match careers based on job title.
    """
    job_lower = normalize_text(job)
    return [
        c for c in load_all_careers()
        if job_lower in normalize_text(c.get("name", ""))
    ]
