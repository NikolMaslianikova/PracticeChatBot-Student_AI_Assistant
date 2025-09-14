from create_chromadb import search_documents
from user_data import user_subject

def build_rag_prompt(user_id: int, user_text: str) -> str:
    subj = user_subject.get(user_id)
    results = search_documents(user_text, subject=subj, n_results=3)

    if results and results["documents"]:
        docs = [doc for doc in results["documents"][0]]
        context = "\n---\n".join(docs)
    else:
        context = "Нічого не знайшов у базі."

    rag_prompt = f"""
Ти — навчальний помічник для студентів. 
Ось знайдений контекст з лекцій (може містити помилки чи неповні фрагменти):

{context}

Тепер відповідай на запитання студента: 
{user_text}
"""
    return rag_prompt
