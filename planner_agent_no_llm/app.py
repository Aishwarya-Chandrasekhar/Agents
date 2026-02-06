# app.py
# Gradio UI for Part 3: Rule-based Planner Agent (No LLM)
#
# Run:
#   pip install gradio sentence-transformers faiss-cpu requests beautifulsoup4
#   python app.py
#
# Notes:
# - This UI wraps the same Plan → Act → Observe logic from agent.py
# - It displays the chosen tool + reason + the tool output
import warnings
warnings.filterwarnings("ignore")

import gradio as gr

from planner import plan
from tools.calculator import calculate
from tools.retriever import RetrieverTool
from tools.web import fetch_text

# Initialize once so the FAISS index + embeddings load a single time
retriever = RetrieverTool(docs_folder="../sample_docs")


def run_agent(question: str):
    question = (question or "").strip()
    if not question:
        return "—", "Please enter a question.", ""

    # PLAN
    p = plan(question)
    tool_name = p.tool
    reason = p.reason

    # ACT + OBSERVE
    if tool_name == "calculator":
        output = calculate(question)

    elif tool_name == "retriever":
        chunks = retriever.query(question, k=3)
        output = "📚 Retrieved top matches:\n" + "\n".join([f"• {c}" for c in chunks])

    elif tool_name == "web":
        # Heuristic: find the first URL token in the question
        url = next((t for t in question.split() if t.startswith("http")), None)
        if not url:
            output = (
                "🌐 Web tool selected.\n"
                "Please include a URL in your question, e.g.\n"
                "  Summarize https://en.wikipedia.org/wiki/Retrieval-augmented_generation"
            )
        else:
            page_text = fetch_text(url)
            output = "🌐 Page text (truncated):\n" + page_text
    else:
        output = "❌ Unknown tool selected."

    return tool_name, reason, output


with gr.Blocks() as demo:
    gr.Markdown("# 🤖 Part 3 — Planner Agent (No LLM)")
    gr.Markdown(
        "This agent chooses between **calculator**, **retriever**, and **web** using a deterministic rule-based planner.\n\n"
        "Try:\n"
        "- `45 * 19`\n"
        "- `What is RAG?`\n"
        "- `Summarize https://en.wikipedia.org/wiki/Retrieval-augmented_generation`"
    )

    with gr.Row():
        question = gr.Textbox(
            label="🧑 Question",
            placeholder="Ask a question…",
            lines=2,
        )

    with gr.Row():
        run_btn = gr.Button("Run Agent")
        clear_btn = gr.Button("Clear")

    with gr.Row():
        tool = gr.Textbox(label="🧠 Selected Tool", interactive=False)
        reason = gr.Textbox(label="💡 Planner Reason", interactive=False)

    output = gr.Textbox(label="👀 Tool Output", interactive=False, lines=14)

    run_btn.click(fn=run_agent, inputs=question, outputs=[tool, reason, output])
    question.submit(fn=run_agent, inputs=question, outputs=[tool, reason, output])

    clear_btn.click(
        fn=lambda: ("", "", "", ""),
        inputs=[],
        outputs=[question, tool, reason, output],
    )

demo.launch()
