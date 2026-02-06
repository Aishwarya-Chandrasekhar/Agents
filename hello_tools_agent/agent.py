from __future__ import annotations
import warnings
# Ignore general UserWarnings (e.g. urllib3 / SSL warnings)
warnings.filterwarnings("ignore", category=UserWarning)

# Ignore DuckDuckGo search RuntimeWarnings
warnings.filterwarnings(
    "ignore",
    category=RuntimeWarning,
    module="duckduckgo_search"
)

warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

import json
from typing import List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import typer

from tools import TOOLS
from planner_stub import decide_next_step, reflect


app = typer.Typer()
console = Console()


def run_agent(goal: str, max_steps: int = 3) -> str:
    """
    Core agent loop:
    - Decide what to do
    - Possibly use a tool
    - Observe result
    - Reflect
    - Repeat or finish
    """

    transcript: List[Dict[str, Any]] = []
    console.rule("[bold cyan]Hello Tools Agent")

    for step in range(1, max_steps + 1):
        console.print(
            Panel.fit(
                f"[bold]Step {step}[/bold]\nGoal: {goal}",
                style="cyan"
            )
        )

        decision = decide_next_step(goal, json.dumps(transcript))

        # If planner says we're done → finish
        if "final" in decision:
            answer = decision["final"]
            console.print(
                Panel(
                    Markdown(f"**Final Answer:**\n\n{answer}"),
                    style="green"
                )
            )
            return answer

        # Otherwise → call a tool
        tool_name = decision["tool"]
        tool = TOOLS.get(tool_name)

        if not tool:
            console.print(f"[red]Unknown tool: {tool_name}[/red]")
            return "Error: unknown tool."

        args_obj = tool["args_model"](**decision["args"])
        console.print(
            f"[yellow]Calling tool[/yellow]: {tool_name}\n"
            f"Args: {args_obj.model_dump()}"
        )

        observation = tool["fn"](args_obj)

        transcript.append({
            "tool": tool_name,
            "args": args_obj.model_dump(),
            "observation": observation
        })

        draft = reflect(goal, observation)
        console.print(
            Panel(
                Markdown(f"**Observation → Draft Answer:**\n\n{draft}"),
                style="magenta"
            )
        )

        return draft  # Day-1 agent intentionally stops after one tool

    return "No answer produced."


@app.command()
def chat(q: List[str] = typer.Argument(..., help="User question / goal")):
    if q and q[0].lower() == "chat":
        q = q[1:]
    query = " ".join(q)
    run_agent(query)


if __name__ == "__main__":
    app()
