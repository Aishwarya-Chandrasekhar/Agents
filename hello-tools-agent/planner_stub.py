import warnings
warnings.filterwarnings(
    "ignore",
    category=RuntimeWarning,
    module="duckduckgo_search"
)

import re
from typing import Dict, Any


MATH_HINTS = r"(sqrt|log|sin|cos|tan|\d+\s*[\+\-\*\/]\s*\d+)"
SEARCH_HINTS = r"(who|what|when|where|why|how|latest|news|CEO|meaning|define|price|weather)"

def decide_next_step(goal: str, transcript: str) -> Dict[str, Any]:
    """
    Decide the agent's next action.

    Returns ONE of:
      {"tool": "<tool_name>", "args": {...}}
      {"final": "<final_answer>"}

    This is intentionally rule-based (no LLM)
    so we can clearly see how an agent loop works.
    """

    q = goal.strip()

    # If math-looking query → calculator
    if re.search(MATH_HINTS, q, re.I):
        q_fixed = q.replace("^", "**").replace("√", "sqrt")
        return {
            "tool": "calculator",
            "args": {"expr": q_fixed}
        }

    # If knowledge-looking query → web search
    if re.search(SEARCH_HINTS, q, re.I):
        return {
            "tool": "web_search",
            "args": {"query": q, "k": 5}
        }

    # Otherwise → no tools needed
    return {
        "final": f"I don't need tools for that. Here's my answer: {q}"
    }


def reflect(goal: str, observation: Dict[str, Any]) -> str:
    """
    Convert a raw tool observation into
    a user-facing answer.
    """

    if observation.get("type") == "number":
        return f"The answer is {observation['value']}."

    if observation.get("type") == "search_results":
        results = observation.get("results", [])
        if not results:
            return "I searched the web but couldn't find anything useful."

        top = results[0]
        return (
            f"Top result: {top.get('title','(no title)')}\n\n"
            f"{top.get('snippet','')}\n\n"
            f"Source: {top.get('url','')}"
        )

    return "I have completed the task."
