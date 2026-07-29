import sqlite3

conn = sqlite3.connect("talentmatch.db")   # Replace with your database filename if different
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE jobs ADD COLUMN category TEXT")
    conn.commit()
    print("Category column added successfully!")
except Exception as e:
    print("Error:", e)

conn.close()