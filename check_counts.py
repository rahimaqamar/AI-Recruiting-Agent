from app.database import SessionLocal, Resume, Job

db = SessionLocal()

resume_count = db.query(Resume).count()
job_count = db.query(Job).count()

print(f"Total Resumes: {resume_count}")
print(f"Total Jobs: {job_count}")

db.close()