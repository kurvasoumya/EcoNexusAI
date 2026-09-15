from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


class RAGAgent:

    def __init__(self):
        self.name = "RAG Knowledge Agent"

        db_path = Path(__file__).resolve().parent.parent / "chroma_db"

        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )

        self.vectorstore = Chroma(
            persist_directory=str(db_path),
            embedding_function=self.embeddings
        )

    def search(self, query, k=3):
        results = self.vectorstore.similarity_search(
            query,
            k=k
        )

        knowledge = []

        for result in results:
            knowledge.append({
                "source": result.metadata.get("source"),
                "content": result.page_content
            })

        return knowledge


rag_agent = RAGAgent()