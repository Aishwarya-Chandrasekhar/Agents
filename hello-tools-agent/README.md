# hello-tools-agent

Tiny, inspectable agent loop (plan → tool → observe → answer) with two tools:
- `calculator(expr)`: safe, math-only eval (Python `math`)
- `web_search(query, k)`: web search using the [`ddgs`](https://pypi.org/project/ddgs/) library 
  (a maintained DuckDuckGo wrapper). Falls back to HTML scrape / Wikipedia if needed.

![demo](hello_tools_agent.gif)

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python agent.py chat "sqrt(144) + 5"
python agent.py chat "Who is the CEO of Apple?"
