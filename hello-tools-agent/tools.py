from __future__ import annotations
from typing import List, Dict, Any
from pydantic import BaseModel, Field
import math, os
from itertools import islice
import httpx
from bs4 import BeautifulSoup

# --- Primary search backend: ddgs ---
from ddgs import DDGS  # pip install ddgs

class SearchArgs(BaseModel):
    query: str = Field(..., description="Web search query string")
    k: int = Field(5, ge=1, le=10, description="Number of results")

class CalcArgs(BaseModel):
    expr: str = Field(..., description="Pythonic arithmetic expression, e.g. 'sqrt(144) + 5'")

def _normalize(r: Dict[str, Any]) -> Dict[str, str]:
    return {
        "title": r.get("title") or r.get("text") or "",
        "url": r.get("href") or r.get("url") or "",
        "snippet": r.get("body") or r.get("desc") or r.get("snippet") or "",
    }

def _search_via_ddgs(query: str, k: int) -> List[Dict[str, str]]:
    try:
        out: List[Dict[str, str]] = []
        headers = {"User-Agent": "Mozilla/5.0"}
        with DDGS(headers=headers) as ddg:
            for r in islice(ddg.text(query), k):
                out.append(_normalize(r) if isinstance(r, dict) else {"title": str(r), "url": "", "snippet": ""})
        return out
    except Exception:
        return []

def _search_via_duckduckgo_html(query: str, k: int) -> List[Dict[str, str]]:
    try:
        q = query.replace(" ", "+")
        url = f"https://duckduckgo.com/html/?q={q}"
        headers = {"User-Agent": "Mozilla/5.0"}
        with httpx.Client(timeout=15) as client:
            html = client.get(url, headers=headers).text
        soup = BeautifulSoup(html, "html.parser")
        items = soup.select(".result__body")[:k]
        out: List[Dict[str, str]] = []
        for it in items:
            a = it.select_one(".result__a")
            if not a: continue
            title = a.get_text(" ", strip=True)
            href = a.get("href", "")
            snippet_el = it.select_one(".result__snippet")
            snippet = snippet_el.get_text(" ", strip=True) if snippet_el else ""
            out.append({"title": title, "url": href, "snippet": snippet})
        return out
    except Exception:
        return []

def _search_via_wikipedia(query: str, k: int) -> List[Dict[str, str]]:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        search_url = "https://en.wikipedia.org/w/rest.php/v1/search/title"
        with httpx.Client(timeout=15, headers=headers) as client:
            r = client.get(search_url, params={"q": query, "limit": str(k)})
            r.raise_for_status()
            pages = r.json().get("pages", [])[:k]
            out: List[Dict[str, str]] = []
            for p in pages:
                title = p.get("title", "")
                url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
                s = client.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}")
                snippet = s.json().get("extract", "") if s.status_code == 200 else ""
                out.append({"title": title, "url": url, "snippet": snippet})
            return out
    except Exception:
        return []

def _search_demo_canned(query: str, k: int) -> List[Dict[str, str]]:
    q = query.lower().strip()
    out: List[Dict[str, str]] = []
    def add(t,u,s): out.append({"title": t, "url": u, "snippet": s})
    if "ceo of apple" in q:
        add("Tim Cook - Wikipedia", "https://en.wikipedia.org/wiki/Tim_Cook",
            "Timothy Donald Cook is the chief executive officer (CEO) of Apple Inc.")
    if "latest iphone" in q:
        add("iPhone 15 Pro — Apple", "https://www.apple.com/iphone-15-pro/",
            "Apple’s 2023 flagship with A17 Pro, titanium design, USB-C.")
    if "langgraph" in q:
        add("LangGraph — Build stateful LLM apps", "https://langchain-ai.github.io/langgraph/",
            "Library for agent/workflow graphs with controlled tool-calling loops.")
    return out[:k]

def web_search(args: SearchArgs) -> dict:
    # Try real backends
    for name, fn in (("ddgs", _search_via_ddgs),
                     ("ddg_html", _search_via_duckduckgo_html),
                     ("wikipedia", _search_via_wikipedia)):
        results = fn(args.query, args.k)
        if results:
            return {"type": "search_results", "results": results, "backend": name}

    # Demo fallback (always on OR require DEMO_MODE=1)
    if os.getenv("DEMO_MODE", "1") == "1":
        demo = _search_demo_canned(args.query, args.k)
        if demo:
            return {"type": "search_results", "results": demo, "backend": "demo"}
    return {"type": "search_results", "results": [], "error": "All backends empty"}

def calculator(args: CalcArgs) -> dict:
    safe_ns = {"__builtins__": {}}
    math_ns = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
    safe_ns.update(math_ns)
    val = eval(args.expr, safe_ns, {})
    return {"type": "number", "value": float(val)}

TOOLS = {
    "web_search": {"fn": web_search, "args_model": SearchArgs, "description": "Search the web"},
    "calculator": {"fn": calculator, "args_model": CalcArgs, "description": "Do math using Python math module"},
}
