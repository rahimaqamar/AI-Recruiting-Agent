# # ==========================================
# # bulk_upload_resumes.py
# # Local folder se saari resumes ek saath upload karta hai
# # ==========================================

# import os

# from app.database import SessionLocal, Resume

# from app.utils import (
#     extract_text_from_pdf,
#     clean_text,
#     extract_experience,
#     extract_skills,
#     extract_education,
#     extract_location,
#     extract_category
# )

# from app.rag import add_resume

# # ==========================================
# # Config — apna resumes wala folder path yahan do
# # ==========================================

# RESUME_FOLDER = "data/resumes"


# def bulk_upload():

#     db = SessionLocal()

#     pdf_files = [
#         f for f in os.listdir(RESUME_FOLDER)
#         if f.lower().endswith(".pdf")
#     ]

#     print(f"Total PDFs mile: {len(pdf_files)}")

#     success_count = 0
#     failed_files = []

#     for filename in pdf_files:

#         file_path = os.path.join(RESUME_FOLDER, filename)

#         try:
#             resume_text = extract_text_from_pdf(file_path)
#             resume_text = clean_text(resume_text)

#             if not resume_text or len(resume_text.strip()) < 20:
#                 print(f"⚠️  Skip kiya (khaali/scanned text): {filename}")
#                 failed_files.append(filename)
#                 continue

#             experience = extract_experience(resume_text)
#             skills = extract_skills(resume_text)
#             education = extract_education(resume_text)
#             location = extract_location(resume_text)
#             category = extract_category(resume_text)

#             resume = Resume(
#                 name=filename.replace(".pdf", ""),
#                 education=education,
#                 experience=experience,
#                 skills=",".join(skills),
#                 location=location,
#                 category=category,
#                 resume_text=resume_text,
#                 file_name=filename
#             )

#             db.add(resume)
#             db.commit()
#             db.refresh(resume)

#             add_resume(
#                 candidate_id=resume.id,
#                 name=resume.name,
#                 resume_text=resume_text,
#                 experience=experience,
#                 skills=skills,
#                 education=education,
#                 location=location,
#                 category=category
#             )

#             success_count += 1
#             print(f"✅ Saved: {filename} | skills: {skills} | exp: {experience} | edu: {education}")

#         except Exception as e:
#             db.rollback()
#             print(f"❌ Fail hua {filename}: {e}")
#             failed_files.append(filename)

#     db.close()

#     print("\n========== Summary ==========")
#     print(f"Total processed: {len(pdf_files)}")
#     print(f"Successfully saved: {success_count}")
#     print(f"Failed/Skipped: {len(failed_files)}")
#     if failed_files:
#         print("Failed files:", failed_files)


# if __name__ == "__main__":
#     bulk_upload()