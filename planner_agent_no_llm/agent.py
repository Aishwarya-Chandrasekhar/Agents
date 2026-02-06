import warnings
warnings.filterwarnings("ignore")
from planner import plan
from tools.calculator import calculate
from tools.retriever import RetrieverTool
from tools.web import fetch_text

retriever = RetrieverTool(docs_folder="../sample_docs")

def run(question: str) -> str:
    p = plan(question)

    # PLAN
    print(f"\n🧠 PLAN: use `{p.tool}`")
    print(f"💡 Reason: {p.reason}")

    # ACT
    if p.tool == "calculator":
        result = calculate(question)
        observation = result

    elif p.tool == "retriever":
        chunks = retriever.query(question, k=3)
        observation = "📚 Retrieved:\n" + "\n".join([f"• {c}" for c in chunks])

    elif p.tool == "web":
        # For demo: user includes URL in question or we use a default known page
        # Simple heuristic: if question contains 'http', treat it as URL
        url = None
        for token in question.split():
            if token.startswith("http"):
                url = token
                break
        if not url:
            return "🌐 For web tool demo, include a URL in your question (e.g. 'Summarize https://example.com')."

        page_text = fetch_text(url)
        observation = "🌐 Page text (truncated):\n" + page_text

    else:
        observation = "❌ No tool available."

    # OBSERVE
    print("👀 OBSERVE: got tool output\n")
    return observation

if __name__ == "__main__":
    print("🤖 Day 3: Planner Agent (No LLM)")
    print("Type 'exit' to quit.\n")

    while True:
        q = input("🧑 Question: ")
        if q.lower().strip() == "exit":
            break

        answer = run(q)
        print(answer)
        print("\n" + "-" * 50)
