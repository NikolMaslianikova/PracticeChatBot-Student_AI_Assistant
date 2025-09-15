import os
import re
import uuid
from pathlib import Path
from typing import List
from tqdm import tqdm
from pypdf import PdfReader
import ollama
from transformers import AutoTokenizer
from create_chromadb import add_documents

DATA_DIR = Path("data/lectures")
EMBED_MODEL = "nomic-embed-text"
TOKENIZER_NAME = os.getenv("TOKENIZER_NAME", "xlm-roberta-base")

CHUNK_TOKENS = int(os.getenv("CHUNK_TOKENS", "500"))
OVERLAP_TOKENS = int(os.getenv("OVERLAP_TOKENS", "200"))

_tokenizer = None
def get_tokenizer():
    global _tokenizer
    if _tokenizer is None:
        _tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_NAME)
    return _tokenizer

def read_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    texts = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        texts.append(page_text)
    text = "\n".join(texts)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()
    return text

def chunk_text_by_tokens(
    text: str,
    max_tokens: int = CHUNK_TOKENS,
    overlap: int = OVERLAP_TOKENS
) -> List[str]:
    if not text:
        return []

    tokenizer = get_tokenizer()

    token_ids = tokenizer.encode(text, add_special_tokens=False)

    if len(token_ids) == 0:
        return []

    chunks = []
    step = max_tokens - overlap
    if step <= 0:
        raise ValueError("overlap має бути меншим за max_tokens")

    for start in range(0, len(token_ids), step):
        end = min(start + max_tokens, len(token_ids))
        chunk_ids = token_ids[start:end]
        chunk_text = tokenizer.decode(chunk_ids, skip_special_tokens=True).strip()
        if chunk_text and len(chunk_text) > 0:
            chunks.append(chunk_text)

        if end == len(token_ids):
            break

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

        chunks = chunk_text_by_tokens(text, max_tokens=CHUNK_TOKENS, overlap=OVERLAP_TOKENS)

        if not chunks:
            print("Не вдалося сформувати чанки.")
            continue

        embeds = embed_texts(chunks)

        ids = [str(uuid.uuid4()) for _ in chunks]
        metadatas = [{
            "subject": subject,
            "file": pdf.name,
            "chunk_index": i,
            "tokenizer": TOKENIZER_NAME,
            "chunk_tokens": CHUNK_TOKENS,
            "overlap_tokens": OVERLAP_TOKENS,
        } for i in range(len(chunks))]

        add_documents(
            documents=chunks,
            embeddings=embeds,
            metadatas=metadatas,
            ids=ids
        )

        print(f"Додано {len(chunks)} чанків\n")

    print("Усі лекції проіндексовані")

if __name__ == "__main__":
    index_lectures()
