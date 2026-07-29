from app.config import CHROMA_DB_DIR
from app.rag import vector_store

print("CHROMA_DB_DIR:", CHROMA_DB_DIR)
print("Vector count:", vector_store._collection.count())