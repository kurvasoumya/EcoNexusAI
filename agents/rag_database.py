from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

from knowledge_loader import load_knowledge


# Load knowledge files
knowledge = load_knowledge()

documents = []

for filename, content in knowledge.items():
    documents.append(
        Document(
            page_content=content,
            metadata={"source": filename}
        )
    )


# Split documents into smaller chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = text_splitter.split_documents(documents)


# Create embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)


# Location for Chroma database
db_path = Path(__file__).resolve().parent.parent / "chroma_db"


# Create vector database
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=str(db_path)
)


print("RAG database created successfully!")
print("Knowledge files:", len(knowledge))
print("Document chunks:", len(chunks))
print("Database location:", db_path)