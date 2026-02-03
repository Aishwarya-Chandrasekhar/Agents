import warnings
warnings.filterwarnings("ignore")


import gradio as gr
from agent import ask_agent


def answer(question):
    results = ask_agent(question)
    return "\n".join(results)

demo = gr.Interface(
    fn=answer,
    inputs=gr.Textbox(label="Ask a research question"),
    outputs=gr.Textbox(label="Retrieved answer"),
    title="📚 Research RAG Agent",
    description="Answers questions using document retrieval (no LLM)"
)

demo.launch()
