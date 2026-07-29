"""
Job Selector

Goal text ke basis pe database se automatically
best-matching job ko select karta hai.
"""

import re
import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings

from app.database import SessionLocal, Job
from app.config import EMBEDDING_MODEL

embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

JOB_MATCH_CONFIDENCE_THRESHOLD = 0.55

# Common stopwords jo keyword match mein ignore karni hain
STOPWORDS = {
    "the", "a", "an", "and", "or", "for", "of", "to", "in", "on",
    "job", "role", "position", "find", "provide", "search", "developer",
    "engineer", "candidate", "candidates", "best", "good", "senior", "junior"
}


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def extract_keywords(text: str) -> set:
    """Text se meaningful words nikalta hai (stopwords hataa ke)."""
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 2}


def select_job_from_goal(goal: str):
    """
    Goal text se sabse best-matching job_id return karta hai.
    Hybrid approach: embedding similarity + keyword overlap (hard gate).
    """

    db = SessionLocal()
    jobs = db.query(Job).all()
    db.close()

    # ↓↓↓ Data quality: khaali/None title wali jobs ignore karo ↓↓↓
    jobs = [j for j in jobs if j.title and j.title.strip()]
    # ↑↑↑

    if not jobs:
        return None, None, 0.0

    goal_vector = embeddings.embed_query(goal)
    goal_keywords = extract_keywords(goal)

    print(f"\n[job_selector] Goal: '{goal}' | Keywords: {goal_keywords}", flush=True)

    best_job = None
    best_score = -1
    best_keyword_match = False

    for job in jobs:
        job_text = f"{job.title}. Required skills: {job.required_skills}. {job.description}"
        job_vector = embeddings.embed_query(job_text)

        score = cosine_similarity(goal_vector, job_vector)

        # ↓↓↓ Keyword overlap check — job title/category se ↓↓↓
        job_title_keywords = extract_keywords(job.title)
        job_category_keywords = extract_keywords(getattr(job, "category", "") or "")
        job_keywords = job_title_keywords | job_category_keywords

        has_keyword_overlap = bool(goal_keywords & job_keywords)
        # ↑↑↑

        print(
            f"[job_selector]   -> '{job.title}' (ID: {job.id}): "
            f"score={score:.4f}, keyword_overlap={has_keyword_overlap}",
            flush=True
        )

        # Sirf tab consider karo agar keyword overlap hai (hard gate)
        if has_keyword_overlap and score > best_score:
            best_score = score
            best_job = job
            best_keyword_match = True

    # Agar keyword-matched koi job nahi mila, to embedding-only fallback try karo
    # lekin bahut high threshold ke saath (0.90+)
    if best_job is None:
        for job in jobs:
            job_text = f"{job.title}. Required skills: {job.required_skills}. {job.description}"
            job_vector = embeddings.embed_query(job_text)
            score = cosine_similarity(goal_vector, job_vector)
            if score > best_score:
                best_score = score
                best_job = job

        if best_score < 0.90:
            print(f"[job_selector] REJECTED — no keyword overlap, and score {best_score:.4f} below high-confidence bar 0.90", flush=True)
            return None, None, best_score

    print(f"[job_selector] Best match: '{best_job.title}' with score={best_score:.4f}, keyword_match={best_keyword_match}", flush=True)

    return best_job.id, best_job.title, best_score