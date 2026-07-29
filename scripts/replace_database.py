from database import SessionLocal, Resume
from utils import (
    extract_experience,
    extract_education
)
from llm_extractor import extract_resume_information
from sqlalchemy import or_

db = SessionLocal()

# ==========================================
# Sirf wahi resumes query karo jinhe fix karna hai
# (saari 5000 fetch karne ki jagah, sirf "problematic" wali)
# ==========================================

resumes = db.query(Resume).filter(
    or_(
        Resume.skills == None,
        Resume.skills == "",
        Resume.location == "Unknown",
        Resume.category == None,
        Resume.category == "Unknown",
        Resume.category == "General",
        Resume.name.like("DESIGNER_%"),
        Resume.name.like("SALES_%"),
        Resume.name.like("ACCOUNTANT_%")
    )
).all()

print(f"Fix karne wali resumes: {len(resumes)}")

updated = 0
failed = 0

for resume in resumes:

    if not resume.resume_text:
        continue

    print(f"Processing: {resume.file_name}")

    text = resume.resume_text

    # ----------------------------
    # FAST LOCAL EXTRACTION
    # ----------------------------

    education = extract_education(text)
    experience = extract_experience(text)

    # ----------------------------
    # LLM ONLY FOR HARD FIELDS
    # ----------------------------

    need_llm = (
        not resume.skills
        or resume.location == "Unknown"
        or getattr(resume, "category", "Unknown") in [None, "Unknown", "General"]
        or resume.name.startswith(("DESIGNER_", "SALES_", "ACCOUNTANT_"))
    )

    llm_data = {}

    if need_llm:
        try:
            llm_data = extract_resume_information(text)
        except Exception as e:
            print(f"⚠️  LLM fail hua {resume.file_name}: {e}")
            failed += 1
            # is resume ko is baar skip karo, agli dafa dobara try hoga
            continue

    # ----------------------------
    # UPDATE NAME
    # ----------------------------

    if llm_data.get("name"):
        resume.name = llm_data["name"]

    # ----------------------------
    # UPDATE EDUCATION
    # ----------------------------

    if resume.education in [None, "", "Unknown"]:
        resume.education = education

    # ----------------------------
    # UPDATE EXPERIENCE
    # ----------------------------

    if resume.experience in [None, 0, 0.0]:
        resume.experience = experience

    # ----------------------------
    # UPDATE SKILLS
    # ----------------------------

    if not resume.skills and llm_data.get("skills"):
        resume.skills = ", ".join(llm_data["skills"])

    # ----------------------------
    # UPDATE LOCATION
    # ----------------------------

    if resume.location == "Unknown":
        resume.location = llm_data.get("location", "Unknown")

    # ----------------------------
    # UPDATE CATEGORY
    # ----------------------------

    if hasattr(resume, "category"):

        current = getattr(resume, "category", "Unknown")

        if current in [None, "", "Unknown", "General"]:
            setattr(
                resume,
                "category",
                llm_data.get("category", "General")
            )

    updated += 1

    # ----------------------------
    # NAYA: har 20 resumes ke baad commit karo,
    # taaki agar beech me crash ho, pehle wala kaam save rahe
    # ----------------------------

    if updated % 20 == 0:
        db.commit()
        print(f"   💾 Progress saved ({updated} updated so far)")

# Final commit — jo bacha hua tha
db.commit()
db.close()

print(f"\n========== Summary ==========")
print(f"Updated: {updated}")
print(f"Failed (rate limit / error): {failed}")