import re

ALLOWED = re.compile(r"^[\d\s\.\+\-\*\/\(\)]+$")

def calculate(expr: str) -> str:
    expr = expr.strip()
    if not ALLOWED.match(expr):
        return "❌ Sorry — that doesn't look like safe math."

    try:
        # Evaluate in a restricted environment
        result = eval(expr, {"__builtins__": {}}, {})
        return f"✅ {expr} = {result}"
    except Exception as e:
        return f"❌ Math error: {e}"
