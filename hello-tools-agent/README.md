# hello-tools-agent
A tiny agent loop that can:
       
* Decide whether to use a calculator tool or a web search tool
* Call that tool with structured arguments (validated with Pydantic)
* Observe the result and answer the user

![demo](hello_tools_agent.gif)

Tiny, inspectable agent loop (plan → tool → observe → answer) with two tools:
- `calculator(expr)`: safe, math-only eval (Python `math`)
- `web_search(query, k)`: web search using the [`ddgs`](https://pypi.org/project/ddgs/) library 
  (a maintained DuckDuckGo wrapper). Falls back to HTML scrape / Wikipedia if needed.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python agent.py chat "sqrt(144) + 5"
python agent.py chat "Who is the CEO of Apple?"
