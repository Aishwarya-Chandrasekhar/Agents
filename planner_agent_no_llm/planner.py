import re
from dataclasses import dataclass
from typing import Literal

ToolName = Literal["calculator", "retriever", "web"]

@dataclass
class Plan:
    tool: ToolName
    reason: str

MATH_PATTERN = re.compile(r"^[\d\s\.\+\-\*\/\(\)]+$")

def plan(question: str) -> Plan:
    q = question.strip().lower()

    # Rule 1: If it looks like math → calculator
    if MATH_PATTERN.match(q) and any(op in q for op in ["+", "-", "*", "/", "(", ")"]):
        return Plan(tool="calculator", reason="Question looks like a math expression.")

    # Rule 2: If it contains 'latest', 'today', 'news', 'current' → web
    if any(word in q for word in ["latest", "today", "current", "news", "this week"]):
        return Plan(tool="web", reason="Question asks for recent/up-to-date info.")

    # Rule 3: Otherwise → search local docs (retriever)
    return Plan(tool="retriever", reason="Best answered from local knowledge base.")
