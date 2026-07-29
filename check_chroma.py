from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from app.config import CHROMA_DB_DIR, EMBEDDING_MODEL

embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)

vector_store = Chroma(
    persist_directory=CHROMA_DB_DIR,
    embedding_function=embeddings
)

collection = vector_store._collection

print("Total resumes:", collection.count())