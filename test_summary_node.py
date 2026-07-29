from app.services import get_db, Resume
from app.agent.tools import candidate_summary_tool

db = get_db()
resumes = db.query(Resume).limit(3).all()
db.close()

for r in resumes:
    print(f"Testing candidate_id={r.id}...")
    result = candidate_summary_tool(r.id)
    print(f"Done: {result}")