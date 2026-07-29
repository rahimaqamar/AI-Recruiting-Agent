# ==========================================
# config.py
# Project Configuration
# ==========================================

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# -------------------------------
# API Keys
# -------------------------------

# Groq API Key (stored in .env)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# -------------------------------
# Database
# -------------------------------

# SQLite database file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'recruitment.db')}"

# -------------------------------
# ChromaDB
# -------------------------------

# Folder where ChromaDB stores vectors
CHROMA_DB_DIR = "chroma_db"

# Embedding model
EMBEDDING_MODEL = "intfloat/e5-small-v2"

# ---- Upload Folder -----------
# -------------------------------

# Uploaded resumes are stored here
UPLOAD_FOLDER = "uploads"

# Dataset folder
DATASET_FOLDER = "data/resumes"

# -------------------------------
# LLM Model
# -------------------------------

LLM_MODEL = "llama-3.3-70b-versatile"

# -------------------------------
# Search Configuration
# -------------------------------

# Number of resumes returned
TOP_K_RESULTS = 5

# -------------------------------
# Create Required Folders
# -------------------------------

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CHROMA_DB_DIR, exist_ok=True)
os.makedirs(DATASET_FOLDER, exist_ok=True)