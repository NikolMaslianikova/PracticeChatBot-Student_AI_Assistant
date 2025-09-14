import os
import uuid
from pathlib import Path
from typing import List
from tqdm import tqdm
from pypdf import PdfReader
import ollama
from create_chromadb import add_documents

DATA_DIR = Path("data/lectures")
EMBED_MODEL = "nomic-embed-text"

def read_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 200) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def embed_texts(texts: List[str], model: str = EMBED_MODEL) -> List[List[float]]:
    embeddings = []
    for t in tqdm(texts, desc="Створюю ембеддинги"):
        resp = ollama.embeddings(model=model, prompt=t)
        embeddings.append(resp["embedding"])
    return embeddings

def index_lectures():
    pdf_files = list(DATA_DIR.glob("**/*.pdf"))

    if not pdf_files:
        print("Файли лекцій не знайдені")
        return

    for pdf in pdf_files:
        subject = pdf.parent.name
        print(f"Індексую: [{subject}] {pdf.name}")

        text = read_pdf_text(pdf)
        if not text.strip():
            print("Порожній PDF.")
            continue

        chunks = chunk_text(text)
        embeds = embed_texts(chunks)

        ids = [str(uuid.uuid4()) for _ in chunks]
        metadatas = [{
            "subject": subject,
            "file": pdf.name,
            "chunk_index": i
        } for i in range(len(chunks))]

        add_documents(
            documents=chunks,
            embeddings=embeds,
            metadatas=metadatas,
            ids=ids
        )

        print(f"Додано {len(chunks)} чанків\n")

    print("Усі лекції проіндексовані!")

if __name__ == "__main__":
    index_lectures()
