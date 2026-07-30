# ==========================================
# services.py
# Business Logic Layer
# ==========================================
# every API in app.py calls a function from this file.
# db.add(obj) → naya record banane ke liye taiyar karo
# db.commit() → actually save karo database me (permanent) resume id generate hota han
# db.refresh(obj) → database se wapas latest data lo (jaise auto-generated id)
# db.close() → connection band karo

# Aur query karne ke liye:
# .filter(...).first() → ek specific row dhundo
# .filter(...).all() → saari matching rows dhundo
# .count() → sirf ginti do

import os
import re

from app.database import (
    SessionLocal,
    Resume,
    Job,
    Session,
    Conversation
)

from app.utils import (
    extract_text_from_pdf,
    clean_text,
    extract_experience,
    extract_skills,
    extract_education,
    extract_location,
   
)

from app.rag import (
    add_resume,
    semantic_search
)

from app.llm import (
    generate_candidate_summary,
    generate_interview_questions,
    improve_job_description,
    explain_match,
    explain_no_match,
    rewrite_query_for_search,
    extract_result_count_with_llm
    
)

from app.config import UPLOAD_FOLDER

# Run Match mein match/no-match explanation ke liye threshold.
# apply_filter() mein bhi yahi 0.45 use hota hai — dono jagah consistent
# rakhne ke liye same value.
RUN_MATCH_SIMILARITY_THRESHOLD = 0.45


# ==========================================
# Database Session
# ==========================================

def get_db():
    return SessionLocal()


# ==========================================
# Dynamic Result Count Helper
# ==========================================
# User query se number nikalta hai (e.g. "give me 10 resumes" -> 10)
# Agar number nahi mila to default 5 return karta hai.
# max_limit se zyada kabhi nahi jaane deta (safety cap).

MAX_RESULT_LIMIT = 50

def get_requested_count(query: str, default: int = 5):

    if not query:
        return default


    # First try regex
    match = re.search(r'\b\d+\b', query)

    if match:
        count = int(match.group())

        return min(
            max(count,1),
            MAX_RESULT_LIMIT
        )


    # If number not found use LLM

    count = extract_result_count_with_llm(query)


    return min(
        max(count,1),
        MAX_RESULT_LIMIT
    )


# ==========================================
# Upload Resume  (FIXED — category ab add_resume() call me bhi jaa raha hai)
# ==========================================

def upload_resume(file):

    # Save uploaded PDF
    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # Extract Resume Text
    resume_text = extract_text_from_pdf(file_path)

    # Clean Resume Text
    resume_text = clean_text(resume_text)

    # Extract Information
    experience = extract_experience(resume_text)

    skills = extract_skills(resume_text)

    education = extract_education(resume_text)

    location = extract_location(resume_text)

    # category = suggest_category(resume_text)   # LLM-based category (single resume, isliye chalega)

    # Database Connection
    db = get_db()

    # Create Resume Object
    resume = Resume(
        name=file.filename.replace(".pdf", ""),
        education=education,
        experience=experience,
        skills=",".join(skills),
        location=location,
        resume_text=resume_text,
        file_name=file.filename
    )

    # Save into SQLite
    db.add(resume)
    db.commit()
    db.refresh(resume)

    # Save into ChromaDB
    add_resume(
        candidate_id=resume.id,
        name=resume.name,
        resume_text=resume_text,
        experience=experience,
        skills=skills,
        education=education,
        location=location,
        # category=category      # ← ye missing tha, add kiya
    )

    db.close()

    return {
        "id": resume.id,
        "message": "Resume uploaded successfully."
    }


# ==========================================
# Create Job
# ==========================================

def create_job(job_data):

    db = get_db()

    job = Job(
        title=job_data.title,
        description=job_data.description,
        required_skills=",".join(job_data.required_skills),
        experience=job_data.experience,
        education=job_data.education,
        location=job_data.location
    )

    db.add(job)
    db.commit()
    db.refresh(job)
    db.close()

    return {
        "id": job.id,
        "message": "Job created successfully."
    }

# ==========================================
# Upload Job Description
# ==========================================

def upload_job(file):

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    job_description = extract_text_from_pdf(file_path)
    job_description = clean_text(job_description)

    skills = extract_skills(job_description)
    experience = extract_experience(job_description)
    education = extract_education(job_description)
    location = extract_location(job_description)

    db = get_db()

    job = Job(
        title=file.filename.replace(".pdf", ""),
        description=job_description,
        required_skills=",".join(skills),
        experience=experience,
        education=education,
        location=location
    )

    db.add(job)
    db.commit()
    db.refresh(job)
    db.close()

    return {
        "id": job.id,
        "message": "Job uploaded successfully"
    }

# ==========================================
# Search Candidates
# ==========================================

def search_candidates(search_request, skip_explanation=False, top_k=None):

    if top_k is None:
        top_k = get_requested_count(search_request.query)

    candidates = semantic_search(
        query=search_request.query,
        filters=search_request.filters,
        top_k=top_k
    )

    results = []

    db = get_db()

    try:
        for candidate in candidates:

            explanation = "" if skip_explanation else explain_match(
                search_request.query,
                candidate["resume_text"]
            )

            # Fetch resume from database
            resume = db.query(Resume).filter(
                Resume.id == candidate["candidate_id"]
            ).first()

            skills = []
            experience = 0
            education = ""
            location = ""

            if resume:
                if resume.skills:
                    skills = [
                        s.strip()
                        for s in resume.skills.split(",")
                        if s.strip()
                    ]

                experience = resume.experience
                education = resume.education
                location = resume.location

            results.append({
                "candidate_id": candidate["candidate_id"],
                "name": candidate["name"],
                "similarity_score": candidate["similarity_score"],
                "meets_filters": True,
                "why_matched": explanation,
                "skills": skills,
                "experience": experience,
                "education": education,
                "location": location
            })

    finally:
        db.close()

    return {
        "query": search_request.query,
        "filters_applied":
            search_request.filters.model_dump()
            if search_request.filters
            else {},
        "results": results
    }
# ==========================================
# Candidate Summary
# ==========================================

def candidate_summary(
    candidate_id,
    search_query=""
):

    db = get_db()

    resume = db.query(Resume).filter(
        Resume.id == candidate_id
    ).first()

    db.close()

    if resume is None:
        return None

    summary = generate_candidate_summary(
        resume.resume_text,
        search_query
    )

    return {
        "candidate_id": candidate_id,
        "summary": summary
    }


# ==========================================
# Interview Questions
# ==========================================

def interview_questions(
    job_id,
    candidate_id
):

    db = get_db()

    resume = db.query(Resume).filter(
        Resume.id == candidate_id
    ).first()

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    db.close()

    if resume is None or job is None:
        return None

    questions = generate_interview_questions(
        resume.resume_text,
        job.description
    )

    return {
        "candidate_id": candidate_id,
        "job_id": job_id,
        "questions": questions
    }


# ==========================================
# Improve Job Description
# ==========================================

def improve_job(job_id):

    db = get_db()

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    total_candidates = db.query(Resume).count()

    db.close()

    if job is None:
        return None

    statistics = f"Total resumes available: {total_candidates}"

    review = improve_job_description(
        job.description,
        statistics
    )

    return {
        "job_id": job_id,
        "review": review
    }


# ==========================================
# Save Conversation
# ==========================================

def save_chat(
    session_id,
    role,
    message
):
    db = get_db()
    try:
        session_exists = db.query(Session).filter(Session.id == session_id).first()

        if not session_exists:
            new_session = Session(id=session_id)
            db.add(new_session)
            db.commit()

        chat = Conversation(
            session_id=session_id,
            role=role,
            message=message
        )
        db.add(chat)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


# ==========================================
# Get Conversation History
# ==========================================

def get_chat_history(session_id):

    db = get_db()

    chats = db.query(Conversation).filter(
        Conversation.session_id == session_id
    ).all()

    db.close()

    history = []

    for chat in chats:
        history.append({
            "role": chat.role,
            "message": chat.message
        })

    return history


# ==========================================
# Create New Session
# ==========================================

def create_session():
    db = get_db()
    session = Session()
    db.add(session)
    db.commit()
    db.refresh(session)
    db.close()
    return session.id


from app.schemas import SearchRequest

# ==========================================
# Automatic Job Processing
# ==========================================

def process_job(job_data):

    job_result = create_job(job_data)
    job_id = job_result["id"]

    search_request = SearchRequest(
        query=job_data.description,
        filters=None
    )

    search_result = search_candidates(search_request)

    results = sorted(
        search_result["results"],
        key=lambda x: x["similarity_score"],
        reverse=True
    )

    # NOTE: har candidate ke liye 2 LLM calls hoti hain (summary + interview
    # questions). Isliye "results" ko unlimited chhodna risky hai — bahut
    # zyada candidates maangne par ye slow ho jayega ya rate-limit hit karega.
    # Isliye ek safe upper cap (10) rakha hai, chahe query me zyada number ho.
    PROCESS_JOB_LIMIT = 10
    limited_results = results[:PROCESS_JOB_LIMIT]

    final_candidates = []

    for candidate in limited_results:

        candidate_id = candidate["candidate_id"]

        summary = candidate_summary(
            candidate_id,
            job_data.description
        )

        interview = interview_questions(
            job_id,
            candidate_id
        )

        final_candidates.append({
            "candidate_id": candidate["candidate_id"],
            "name": candidate["name"],
            "similarity_score": candidate["similarity_score"],
            "why_matched": candidate["why_matched"],
            "summary": summary["summary"] if summary else "",
            "interview_questions": interview["questions"] if interview else []
        })

    review = improve_job(job_id)

    return {
        "job_id": job_id,
        "improved_job_description": review["review"] if review else "",
        "total_candidates": len(final_candidates),
        "candidates": final_candidates
    }


# ==========================================
# Run Match  (FIXED — category ab har jagah sahi se ja raha hai)
# ==========================================
# BUG FIX (score 0.00 issue): pehle top_k = max(len(candidates), 1) tha.
# Agar sirf 1 resume upload hua to top_k=1, aur ChromaDB (jisme purane
# saare resumes bhi stored hain) sirf EK sabse relevant document poore
# collection me se return karta tha — jo zaroori nahi ki abhi wala
# candidate ho. Isliye score_map me candidate ka apna ID hi nahi milta
# tha, aur score hamesha default 0.0 aa jaata tha.
# Fix: top_k ko ek bada fixed number (100) diya, taaki search results
# me har candidate (chahe database me aur bhi purane resumes ho) cover
# ho jaye aur uska sahi similarity score mile.

def run_match(job_file, resume_files):

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    job_path = os.path.join(
        UPLOAD_FOLDER,
        job_file.filename
    )

    with open(job_path, "wb") as f:
        f.write(job_file.file.read())

    job_description = clean_text(
        extract_text_from_pdf(job_path)
    )

    db = get_db()

    try:
        # =========================================
        # Extract Job Information (Job table me category column nahi hai, isliye yahan nahi chahiye)
        # =========================================
        job_skills = extract_skills(job_description)
        job_experience = extract_experience(job_description)
        job_education = extract_education(job_description)
        job_location = extract_location(job_description)

        job = Job(
            title=job_file.filename.replace(".pdf", ""),
            description=job_description,
            required_skills=",".join(job_skills),
            experience=job_experience,
            education=job_education,
            location=job_location
        )

        db.add(job)
        db.commit()
        db.refresh(job)

        job_id = job.id

        candidates = []

        # -------------------------------
        # Process Resumes
        # -------------------------------
        for resume_file in resume_files:

            resume_path = os.path.join(
                UPLOAD_FOLDER,
                resume_file.filename
            )

            with open(resume_path, "wb") as f:
                f.write(resume_file.file.read())

            resume_text = clean_text(
                extract_text_from_pdf(resume_path)
            )

            skills = extract_skills(resume_text)
            experience = extract_experience(resume_text)
            education = extract_education(resume_text)
            location = extract_location(resume_text)
            # category = extract_category(resume_text)
            #  yahan suggest_category() (LLM) nahi use kiya —
            # kyunki batch me kai resumes ek saath process hote hain,
            # har ek ke liye LLM call karna bahut slow hoga.
            # extract_category() (keyword-based, utils.py) fast hai, isliye yahan uchit hai.

            resume = Resume(
                name=resume_file.filename.replace(".pdf", ""),
                education=education,
                experience=experience,
                skills=",".join(skills),
                location=location,
                resume_text=resume_text,
                file_name=resume_file.filename
            )

            db.add(resume)
            db.commit()
            db.refresh(resume)

            add_resume(
                candidate_id=resume.id,
                name=resume.name,
                resume_text=resume_text,
                experience=experience,
                skills=skills,
                education=education,
                location=location
                       
            )

            candidates.append({
                "id": resume.id,
                "name": resume.name,
                "score": 0.0,
                "snippet": resume_text[:120] + "..",
                "skills": skills
            })

        # -------------------------------
        # Calculate Similarity Scores
        # -------------------------------
        # FIXED: top_k ab fixed 100 hai (pehle max(len(candidates), 1) tha).
        # ChromaDB me sirf ABHI ke candidates hi nahi, purane resumes bhi
        # stored rehte hain. Chhota top_k dene se sirf poore-collection-me-se
        # sabse relevant ek/do result milte the — jo abhi upload kiye gaye
        # candidates se match hi nahi karte the, isliye score hamesha 0.0
        # aa raha tha. Ab top_k=100 rakhne se zyada results aayenge aur
        # har naye candidate ka apna sahi similarity score milega.
        search_results = semantic_search(
            query=job_description,
            filters=None,
            top_k=100
        )

        score_map = {
            r["candidate_id"]: r["similarity_score"]
            for r in search_results
        }

        for candidate in candidates:
            candidate["score"] = round(
                score_map.get(candidate["id"], 0.0),
                2
            )

        candidates.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        # Yahan sirf display ke liye top 5 slice kiya ja raha hai
        # (dashboard summary view). Agar poore batch ka result chahiye
        # to iss line ko hata sakti ho ya limit badha sakti ho.
        candidates = candidates[:5]

        # -------------------------------
        # Why Matched / Why Not Matched
        # -------------------------------
        # Score threshold ke upar -> "why matched" explanation.
        # Score threshold ke neeche (0.0 sahit) -> "why NOT matched".
        # resume_text candidate dict mein store nahi tha, isliye DB se
        # dobara laate hain (ID se lookup).
            # -------------------------------
        # Why Matched / Why Not Matched
        # -------------------------------
        # Score threshold ke upar -> "why matched"
        # Score threshold ke neeche -> "why NOT matched"
        for candidate in candidates:

            resume_obj = db.query(Resume).filter(
                Resume.id == candidate["id"]
            ).first()

            resume_text = resume_obj.resume_text if resume_obj else ""

            score = candidate["score"]

            if score >= RUN_MATCH_SIMILARITY_THRESHOLD:

                candidate["match_status"] = "Matched"

                candidate["why_matched"] = explain_match(
                    job_description,
                    resume_text
                )

                candidate["why_not_matched"] = ""

                candidate["explanation"] = candidate["why_matched"]

            else:

                candidate["match_status"] = "Not Matched"

                candidate["why_matched"] = ""

                candidate["why_not_matched"] = explain_no_match(
                    job_description,
                    resume_text
                )

                candidate["explanation"] = candidate["why_not_matched"]

        return {
            "job_id": job_id,
            "candidates": candidates
        }

    except Exception as e:
        db.rollback()
        raise e

    finally:
        db.close()


# ==========================================
# Candidate Detail
# ==========================================
def get_candidate_detail(candidate_id, job_description):

    db = get_db()

    resume = db.query(Resume).filter(
        Resume.id == candidate_id
    ).first()

    if resume is None:
        db.close()
        return None

    # Summary
    summary = generate_candidate_summary(
        resume.resume_text,
        job_description
    )

    # Interview Questions
    questions = generate_interview_questions(
        resume.resume_text,
        job_description
    )

    # Skills
    job_skills = extract_skills(job_description)
    resume_skills = []

    if resume.skills:
        resume_skills = [
            s.strip()
            for s in resume.skills.split(",")
            if s.strip()
        ]

    missing = [
        skill
        for skill in job_skills
        if skill not in resume_skills
    ]

    # Get actual similarity score
    search_results = semantic_search(
        query=job_description,
        filters=None,
        top_k=100
    )

    score_map = {
        r["candidate_id"]: r["similarity_score"]
        for r in search_results
    }

    real_score = round(
        score_map.get(resume.id, 0.0),
        2
    )

    # Match / No Match explanation
    THRESHOLD = 0.45

    if real_score >= THRESHOLD:

        why_matched = explain_match(
            job_description,
            resume.resume_text
        )

        why_not_matched = ""

    else:

        why_matched = ""

        why_not_matched = explain_no_match(
            job_description,
            resume.resume_text
        )

    db.close()

    return {
        "candidate_id": resume.id,
        "candidate_name": resume.name,
        "match_score": real_score,
        "why_matched": why_matched,
        "why_not_matched": why_not_matched,
        "summary": summary,
        "skills": resume_skills,
        "missing_skills": missing,
        "experience": resume.experience,
        "education": resume.education,
        "location" : resume.location,
        "interview_questions": questions,
        "resume_file": resume.file_name
    }


# ==========================================
# Job Quality
# ==========================================
def get_job_quality(job_description):

    db = get_db()

    total = db.query(Resume).count()

    db.close()

    stats = f"Total resumes analysed: {total}"

    feedback = improve_job_description(
        job_description,
        stats
    )

    return {"feedback": feedback}

# ==========================================
# Apply Chat Filter  (why_not_matched add kiya weak matches ke liye)
# ==========================================
def apply_filter(query):

    try:
        if not query or not query.strip():
            return {"candidates": []}

        optimized_query = rewrite_query_for_search(query)
        

        requested_count = get_requested_count(query)

        search_request = SearchRequest(
            query=optimized_query,
            filters=None
        )

        result = search_candidates(
            search_request,
            skip_explanation=True,
            top_k=requested_count
        )

        if not result:
            return {"candidates": []}

        results = result.get("results", [])

        if not results:
            return {"candidates": []}

        MIN_SIMILARITY_THRESHOLD = 0.45
        top_score = results[0].get("similarity_score", 0) if results else 0
        weak_match_warning = top_score < MIN_SIMILARITY_THRESHOLD

        candidates = []
        db = get_db()

        try:
            for candidate in results[:requested_count]:
                resume = db.query(Resume).filter(
                    Resume.id == candidate["candidate_id"]
                ).first()

                if resume is None:
                    continue

                snippet = ""
                if resume.resume_text:
                    snippet = resume.resume_text[:150] + "..."

                skills = []
                if resume.skills:
                    skills = [
                        s.strip()
                        for s in resume.skills.split(",")
                        if s.strip()
                    ]

                why_not = ""
                candidate_score = candidate.get("similarity_score", 0)

                if candidate_score < MIN_SIMILARITY_THRESHOLD:
                    why_not = explain_no_match(query, resume.resume_text)

                candidates.append({
                    "id": candidate["candidate_id"],
                    "name": candidate["name"],
                    "score": round(candidate_score, 2),
                    "snippet": snippet,
                    "skills": skills,
                    "why_not_matched": why_not
                })

        finally:
            db.close()

        return {
            "candidates": candidates,
            "weak_match": weak_match_warning
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise Exception(f"Filter failed: {e}")



# ==========================================
# Get All Sessions
# ==========================================

def get_sessions():

    db = get_db()

    sessions = db.query(Session).all()

    db.close()

    results = []
    for session in sessions:
        results.append({
            "id": session.id,
            "name": f"Session {session.id}",
            "subtitle": "Resume matching session"
        })
    return results
# ==========================================
# Get All Jobs
# ==========================================

def get_all_jobs():

    db = get_db()

    jobs = db.query(Job).all()

    db.close()

    results = []

    for job in jobs:
        results.append({
            "id": job.id,
            "title": job.title,
            "description": job.description
        })

    return results
