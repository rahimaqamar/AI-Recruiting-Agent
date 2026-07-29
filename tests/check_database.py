import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

from database import SessionLocal, Resume


db = SessionLocal()

try:
    resume = db.query(Resume).first()

    if resume:

        print("Category: ACCOUNTANT")

        print("Experience:", resume.experience, "years")

        print("Skills:")
        print(resume.skills)

        print("----------------")

        print("Resume Text:")
        print(resume.resume_text[:1000])

    else:
        print("No resume found")

finally:
    db.close()