from pathlib import Path


class RAGAgent:
    def __init__(self):
        self.name = "RAG Knowledge Agent"

        self.knowledge_folder = (
            Path(__file__).resolve().parent.parent / "knowledge"
        )

        self.knowledge = self._load_knowledge()

    def _load_knowledge(self):
        knowledge = {}

        for file_path in self.knowledge_folder.glob("*.txt"):
            knowledge[file_path.name] = file_path.read_text(
                encoding="utf-8"
            )

        return knowledge

    def search(self, query, k=3):
        """
        Lightweight keyword-based knowledge retrieval.
        Returns the most relevant knowledge files without
        loading HuggingFace/PyTorch models.
        """

        query_words = set(query.lower().split())

        scored_results = []

        for filename, content in self.knowledge.items():
            text = content.lower()

            score = sum(
                1 for word in query_words
                if len(word) > 2 and word in text
            )

            if score > 0:
                scored_results.append(
                    {
                        "score": score,
                        "source": filename,
                        "content": content
                    }
                )

        scored_results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return [
            {
                "source": item["source"],
                "content": item["content"]
            }
            for item in scored_results[:k]
        ]


rag_agent = RAGAgent()