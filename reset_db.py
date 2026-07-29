from app.database import SessionLocal, Resume

db = SessionLocal()
count = db.query(Resume).count()
db.query(Resume).delete()
db.commit()
db.close()
print(f"Cleared {count} resume(s) from SQLite.")