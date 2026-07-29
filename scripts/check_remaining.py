from database import SessionLocal, Resume
from sqlalchemy import or_

db = SessionLocal()

remaining = db.query(Resume).filter(
    or_(
        Resume.name == None,
        Resume.name == "",

        Resume.education == None,
        Resume.education == "",
        Resume.education == "Unknown",

        Resume.experience == None,
        Resume.experience == 0,

        Resume.skills == None,
        Resume.skills == "",

        Resume.location == None,
        Resume.location == "",
        Resume.location == "Unknown"
    )
).all()

print("=" * 80)
print(f"Remaining incomplete resumes: {len(remaining)}")
print("=" * 80)

for resume in remaining:
    print(f"\nResume ID: {resume.id}")
    print(f"File Name : {resume.file_name}")
    print(f"Name      : {resume.name}")
    print(f"Education : {resume.education}")
    print(f"Experience: {resume.experience}")
    print(f"Skills    : {resume.skills}")
    print(f"Location  : {resume.location}")

db.close()