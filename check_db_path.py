# check_db_path.py
import os
from app.config import DATABASE_URL

print("DATABASE_URL:", DATABASE_URL)
print("Current working directory:", os.getcwd())

# Agar sqlite:///./recruitment.db jaisa format hai:
if DATABASE_URL.startswith("sqlite:///"):
    relative_path = DATABASE_URL.replace("sqlite:///", "")
    absolute_path = os.path.abspath(relative_path)
    print("Actual absolute path:", absolute_path)
    print("File exists?", os.path.exists(absolute_path))