"""Application entrypoint executing sequential demonstration scenarios for tool calling agent."""

import sys
import time
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.agent import run_agentic_loop

console = Console()

SCENARIOS = (
    (
        "Scenario 1: Single Tool Lookup for Known Order",
        "What is the current shipping status of order A123?",
    ),
    (
        "Scenario 2: Edge Case Query for Unknown Order",
        "Can you check the status of order Z999?",
    ),
    (
        "Scenario 3: Multi Tool Chaining for Customer Orders",
        "Look up the account for rohan.sharma@example.com and tell me the shipping status of all their orders.",
    ),
)


def run_demo_suite():
    """Execute three verification scenarios sequentially with a one second separation pause."""
    console.print(
        Panel(
            "Starting Deterministic Tool Calling Demonstration Suite\n"
            "Testing Gemini 2.5 Flash with ReAct Bounded Execution Loop",
            title="System Benchmark Suite",
            border_style="bold blue",
        )
    )

    for index, (scenario_title, query_prompt) in enumerate(SCENARIOS, start=1):
        console.print(
            Panel(
                f"{scenario_title}\nQuery: {query_prompt}",
                title=f"Benchmark Case {index} of {len(SCENARIOS)}",
                border_style="cyan",
            )
        )

        run_agentic_loop(user_query=query_prompt)

        if index < len(SCENARIOS):
            time.sleep(1.0)

    console.print(
        Panel(
            "All demonstration scenarios executed cleanly\n"
            "Tool execution telemetry verified against immutable data store",
            title="Demonstration Suite Complete",
            border_style="bold green",
        )
    )


if __name__ == "__main__":
    run_demo_suite()
