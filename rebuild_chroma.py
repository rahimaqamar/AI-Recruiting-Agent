from app.database import SessionLocal, Resume
from app.rag import add_resume


db = SessionLocal()

resumes = db.query(Resume).limit(1000).all()

print("Total resumes:", len(resumes))


for resume in resumes:

    if not resume.resume_text:
        print("Skipping:", resume.id)
        continue

    add_resume(
        candidate_id=resume.id,
        name=resume.name,
        resume_text=resume.resume_text,
        experience=resume.experience,
        skills=resume.skills.split(",") if resume.skills else [],
        education=resume.education,
        location=resume.location
    )

    print("Embedded:", resume.id)


db.close()

print("Finished")