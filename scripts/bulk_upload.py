# # ==========================================
# # bulk_upload.py
# # Upload All PDF Resumes
# # ==========================================

# import os

# from database import SessionLocal, Resume
# from utils import (
#     extract_text_from_pdf,
#     clean_text,
#     extract_experience,
#     extract_skills,
#     extract_education
# )
# from rag import add_resume
# from config import DATASET_FOLDER


# def upload_all_resumes():

#     # Create database session
#     db = SessionLocal()

#     # Count uploaded resumes
#     uploaded = 0

#     # Read all files from folder
#     for filename in os.listdir(DATASET_FOLDER):

#         # Only process PDF files
#         if not filename.endswith(".pdf"):
#             continue

#         file_path = os.path.join(
#             DATASET_FOLDER,
#             filename
#         )

#         print(f"Processing: {filename}")

#         try:

#             # -----------------------------
#             # Extract Resume Text
#             # -----------------------------
#             resume_text = extract_text_from_pdf(
#                 file_path
#             )

#             resume_text = clean_text(
#                 resume_text
#             )

#             # -----------------------------
#             # Extract Information
#             # -----------------------------
#             experience = extract_experience(
#                 resume_text
#             )

#             skills = extract_skills(
#                 resume_text
#             )

#             education = extract_education(
#                 resume_text
#             )

#             # -----------------------------
#             # Candidate Name
#             # -----------------------------
#             candidate_name = filename.replace(
#                 ".pdf",
#                 ""
#             )

#             # -----------------------------
#             # Store in SQLite
#             # -----------------------------
#             resume = Resume(

#                 name=candidate_name,

#                 education=education,

#                 experience=experience,

#                 skills=",".join(skills),

#                 location="Unknown",

#                 category="Unknown",

#                 resume_text=resume_text,

#                 file_name=filename

#             )

#             db.add(resume)

#             db.commit()

#             db.refresh(resume)

#             # -----------------------------
#             # Store in ChromaDB
#             # -----------------------------
#             add_resume(

#                 candidate_id=resume.id,

#                 name=resume.name,

#                 resume_text=resume_text,

#                 experience=experience,

#                 skills=skills,

#                 education=education,

#                 location="Unknown",

#                 category="Unknown"

#             )

#             uploaded += 1

#             print(f"Uploaded: {filename}")

#         except Exception as e:

#             print(f"Error: {filename}")

#             print(e)

#     db.close()

#     print("-" * 50)

#     print(f"Total Uploaded: {uploaded}")

#     print("Bulk Upload Completed")


# # ==========================================
# # Run Script
# # ==========================================

# if __name__ == "__main__":

#     upload_all_resumes()