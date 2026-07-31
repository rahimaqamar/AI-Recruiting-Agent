# ==========================================
# rag.py
# Retrieval-Augmented Generation (RAG)
# ==========================================

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.config import (
    CHROMA_DB_DIR,
    EMBEDDING_MODEL,
    TOP_K_RESULTS
)
# ------------------------------------------
# Load Embedding Model
# ------------------------------------------

embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)

# ------------------------------------------
# Connect ChromaDB
# ------------------------------------------
# FIX: pehle collection_metadata specify nahi tha, isliye Chroma default
# L2 (Euclidean) distance use kar raha tha. Resume jaisi lambi, similar-
# structure wali text ke liye L2 distance role/domain ka farak achhe se
# pakad nahi paata — har resume (chahe kisi bhi field ka ho) ek jaisi
# narrow distance range me aa jaata tha, isliye similarity_score bhi
# sabka lagbhag same (0.75) aa raha tha, chahe query "backend developer"
# ho aur candidate "Automobile Mechanic" ho.
# Fix: cosine similarity space explicitly set kiya — text/semantic search
# ke liye ye standard aur zyada accurate metric hai.
#
# IMPORTANT: ye setting sirf NAYE collection pe apply hoti hai. Agar
# CHROMA_DB_DIR folder mein pehle se (L2-based) data stored hai, to use
# delete karke saare resumes dobara upload/embed karne honge — warna
# purana data galat metric ke saath hi reh jayega. Neeche 'clear_chroma_db.py'
# script diya hai isi ke liye.

vector_store = Chroma(
    persist_directory=CHROMA_DB_DIR,
    embedding_function=embeddings,
    collection_metadata={"hnsw:space": "cosine"}
)

# ------------------------------------------
# Add Resume to ChromaDB
# ------------------------------------------
#  Ye function services.py ke upload_resume() se call hota hai —
#  usi jagah se ye saari values (resume ki structured info) aa rahi hain.
#
# FIX: duplicate-check add kiya. Pehle har call pe naya document add ho
# jaata tha, chahe wahi candidate_id already ChromaDB me maujood ho
# (jaise bulk_upload_resumes.py accidentally dobara chal jaye) — isliye
# search results me same candidate (e.g. "AUTOMOBILE_1331") do baar
# dikhta tha. Ab add karne se pehle check karte hain.

def add_resume(
    candidate_id,
    name,
    resume_text,
    experience,
    skills,
    education,
    location,
  
):
    # Duplicate check — agar ye candidate_id already ChromaDB me hai
    # to dobara add mat karo.
    existing = vector_store.get(
        where={"candidate_id": candidate_id}
    )

    if existing and existing.get("ids"):
        return

# Resume ka text lo → ek standard Document format me pack karo (text + metadata) → ChromaDB me daal do, 
# jo usse automatically embedding me convert karke
# "meaning-searchable" bana deta hai.
    document = Document(
        page_content=resume_text,
        metadata={
            "candidate_id": candidate_id,
            "name": name,
            "experience": experience,
            "skills": ",".join(skills),
            "education": education,
            "location": location,
            
        }
    )

    vector_store.add_documents([document])

# ------------------------------------------
# Check Filters
# ------------------------------------------
# IMPORTANT BUG FIX: pehle is function ke end mein koi explicit
# `return True` nahi tha (category filter ke saath comment ho gaya tha).
# Jab bhi koi filter False return nahi karta (matlab candidate pass ho
# raha hai), function chup-chaap `None` return kar deta tha — aur
# semantic_search() mein `if not passes_filters(...)` check hone ki
# wajah se `not None` -> True ban jaata tha, isliye HAR candidate skip
# ho jaata tha aur results hamesha [] aata tha (chahe filters={} hi ho).
# Fix: function ke end mein explicit `return True` add kiya.

def passes_filters(metadata, filters):

    if filters is None:
        return True


    # Experience Filter
    min_experience_years = (
        filters.get("min_experience_years")
        if isinstance(filters, dict)
        else filters.min_experience_years
    )

    if (
        min_experience_years is not None
        and metadata["experience"] < min_experience_years
    ):
        return False


    # Skills Filter
    required_skills = (
        filters.get("required_skills")
        if isinstance(filters, dict)
        else filters.required_skills
    )

    if required_skills:

        candidate_skills = (
            metadata["skills"]
            .lower()
            .split(",")
        )

        for skill in required_skills:

            if skill.lower() not in candidate_skills:
                return False


    # Education Filter
    education_level = (
        filters.get("education_level")
        if isinstance(filters, dict)
        else filters.education_level
    )

    if (
        education_level
        and metadata["education"].lower()
        != education_level.lower()
    ):
        return False


    # Location Filter
    location = (
        filters.get("location")
        if isinstance(filters, dict)
        else filters.location
    )

    if (
        location
        and metadata["location"].lower()
        != location.lower()
    ):
        return False


    # Category Filter
    # category = (
    #     filters.get("category")
    #     if isinstance(filters, dict)
    #     else filters.category
    # )

    # if (
    #     category
    #     and metadata["category"].lower()
    #     != category.lower()
    # ):
    #     return False

    # Saare filters pass ho gaye (ya koi filter set hi nahi tha)
    # -> candidate ko results mein rehne do.
    return True


# ------------------------------------------
# Semantic Search
# ------------------------------------------

def semantic_search(query, filters=None, top_k=None):

    if filters is None:
        filters = {}

    if top_k is None:
        top_k = TOP_K_RESULTS

    # Detect role from query
    # roles = [
    #     "chef",
    #     "accountant",
    #     "developer",
    #     "designer",
    #     "manager"
    # ]

    # if query:
    #     query_lower = query.lower()

    #     for role in roles:
    #         if role in query_lower:
    #             filters["category"] = role
    #             break

    # Search ChromaDB
    if query:
        docs = vector_store.similarity_search_with_score(
            query,
            k=top_k
        )
    else:
        docs = vector_store.similarity_search(
            "resume",
            k=top_k
        )
        docs = [(doc, 0) for doc in docs]

    results = []

    for doc, score in docs:

        metadata = doc.metadata

        if not passes_filters(metadata, filters):
            continue

        # NOTE: ab collection cosine space use kar raha hai, isliye
        # similarity_search_with_score() seedha cosine DISTANCE return
        # karta hai (range roughly 0 to 2, kam = behtar match).
        # similarity = 1 - distance se sahi 0-to-1 similarity milti hai
        # (1 = perfect match, 0 = koi relation nahi).
        similarity = round(
            1 - score,
            2
        )

        results.append({
            "candidate_id": metadata["candidate_id"],
            "name": metadata["name"],
            "similarity_score": similarity,
            "resume_text": doc.page_content,
            "metadata": metadata
        })

    return results