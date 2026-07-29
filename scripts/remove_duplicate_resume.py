import hashlib
from app.database import SessionLocal, Resume


def generate_hash(text):
    """Create unique fingerprint of resume text"""
    return hashlib.md5(
        text.strip().encode("utf-8")
    ).hexdigest()


db = SessionLocal()

resumes = db.query(Resume).order_by(Resume.id).all()

seen = {}
duplicate_ids = []


for resume in resumes:

    if not resume.resume_text:
        continue

    resume_hash = generate_hash(resume.resume_text)

    if resume_hash in seen:
        # duplicate found
        duplicate_ids.append(resume.id)

    else:
        # keep first (oldest id)
        seen[resume_hash] = resume.id


print("Total resumes:", len(resumes))
print("Duplicates found:", len(duplicate_ids))


# Delete duplicates
for rid in duplicate_ids:
    db.query(Resume).filter(
        Resume.id == rid
    ).delete()


db.commit()

print("Deleted:", len(duplicate_ids))


remaining = db.query(Resume).count()
print("Remaining resumes:", remaining)


db.close()