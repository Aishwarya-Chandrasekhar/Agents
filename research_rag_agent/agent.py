import warnings
warnings.filterwarnings("ignore")

from embed import embed_text
from ingest import load_documents
from search import build_index, search



docs = load_documents()
doc_embeddings = embed_text(docs)
index = build_index(doc_embeddings)

def ask_agent(question):
    q_embed = embed_text([question])
    results = search(q_embed, index, docs)
    return results

if __name__ == "__main__":
    print("📚 Research RAG Agent (No LLM)")
    print("Type 'exit' to quit\n")

    while True:
        q = input("🧑 Question: ")
        if q.lower() == "exit":
            break

        answers = ask_agent(q)
        print("\n🤖 Agent found:")
        for a in answers:
            print("•", a)
        print("\n" + "-" * 40)
