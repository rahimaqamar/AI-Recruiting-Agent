# ==========================================
# resync_chroma_from_sqlite.py
# ==========================================
# Problem: SQLite (resumes.db) aur ChromaDB (vector store) do ALAG
# databases hain. Jab koi resume SQLite se delete hota hai (UI se,
# DB browser se, ya kisi cleanup script se), ChromaDB automatically
# clean nahi hota — wahan purana candidate reh jaata hai aur search
# results mein dikhta rehta hai (jaise AUTOMOBILE_1331, AVIATION_2396).
#
# Solution: SQLite ko "source of truth" maan kar ChromaDB ko poora
# reset karo, phir sirf unhi candidates ko dobara embed karo jo
# ABHI SQLite me maujood hain. Isse dono stores hamesha sync me
# rahenge aur duplicate/stale entries khatam ho jayenge.
#
# Usage:
#   python resync_chroma_from_sqlite.py

import os
import sys
import shutil

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import CHROMA_DB_DIR
from app.database import SessionLocal, Resume


def resync():

    # -------------------------------
    # Step 1: SQLite se saare current resumes padho
    # -------------------------------
    db = SessionLocal()
    resumes = db.query(Resume).all()

    print(f"SQLite me {len(resumes)} resumes mile.")

    if len(resumes) == 0:
        confirm = input(
            "SQLite me koi resume nahi hai — ChromaDB bhi khaali ho jayega. Continue? (yes/no): "
        )
        if confirm.strip().lower() != "yes":
            db.close()
            print("Cancelled.")
            return

    # -------------------------------
    # Step 2: Purana ChromaDB poora delete karo
    # -------------------------------
    if os.path.exists(CHROMA_DB_DIR):
        shutil.rmtree(CHROMA_DB_DIR)
        print(f"Purana ChromaDB deleted: {CHROMA_DB_DIR}")

    os.makedirs(CHROMA_DB_DIR, exist_ok=True)

    # -------------------------------
    # Step 3: rag.py ab import karo (isse naya, khaali, cosine-metric
    # wala collection ban jayega — kyunki humne rag.py me
    # collection_metadata={"hnsw:space": "cosine"} already set kar rakha hai)
    # -------------------------------
    from app.rag import add_resume

    # -------------------------------
    # Step 4: Har SQLite resume ko dobara ChromaDB me embed karo
    # -------------------------------
    added = 0

    for resume in resumes:

        skills = (
            [s.strip() for s in resume.skills.split(",") if s.strip()]
            if resume.skills else []
        )

        add_resume(
            candidate_id=resume.id,
            name=resume.name,
            resume_text=resume.resume_text,
            experience=resume.experience,
            skills=skills,
            education=resume.education,
            location=resume.location
        )

        added += 1
        print(f"  [{added}/{len(resumes)}] Re-embedded: {resume.name}")

    db.close()

    print(f"\nDone. ChromaDB ab SQLite ke {added} resumes ke sath fully sync hai.")


if __name__ == "__main__":
    resync()