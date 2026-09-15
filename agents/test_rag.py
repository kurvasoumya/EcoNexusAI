from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings


# Find Chroma database
db_path = Path(__file__).resolve().parent.parent / "chroma_db"


# Load embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)


# Load existing vector database
vectorstore = Chroma(
    persist_directory=str(db_path),
    embedding_function=embeddings
)


# Test query
query = "How should plastic waste be recycled?"


results = vectorstore.similarity_search(query, k=3)


print("\nRAG SEARCH RESULTS")
print("=" * 50)

for i, result in enumerate(results, start=1):
    print(f"\nResult {i}")
    print("Source:", result.metadata.get("source"))
    print("Content:", result.page_content)