import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import ollama

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "lectures"

def get_chroma_collection():
    client = chromadb.PersistentClient(
        path=CHROMA_PATH,
        settings=Settings(allow_reset=False)
    )
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

def add_documents(
    documents: List[str],
    embeddings: List[List[float]],
    metadatas: List[Dict],
    ids: List[str]
):
    collection = get_chroma_collection()
    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )

def search_documents(
    query: str,
    subject: Optional[str] = None,
    n_results: int = 5
):
    collection = get_chroma_collection()
    where = {"subject": subject} if subject else None

    resp = ollama.embeddings(model="nomic-embed-text", prompt=query)
    query_embedding = resp["embedding"]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where
    )
    return results

def count_documents() -> int:
    collection = get_chroma_collection()
    return collection.count()

if __name__ == "__main__":
    print(f"Документів у базі: {count_documents()}")
