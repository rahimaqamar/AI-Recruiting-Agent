from app.rag import vector_store

print("=" * 50)
print("Testing ChromaDB")
print("=" * 50)

print("Total vectors:", vector_store._collection.count())

queries = [
    "FastAPI",
    "Docker",
    "Python",
    "Business Developer"
]

for query in queries:
    print("\n" + "=" * 50)
    print("Query:", query)

    docs = vector_store.similarity_search_with_score(query, k=5)

    print("Retrieved:", len(docs))

    for i, (doc, score) in enumerate(docs, 1):
        print(f"\nResult {i}")
        print("Score:", score)
        print("Metadata:", doc.metadata)
        print("Content:", doc.page_content[:200])