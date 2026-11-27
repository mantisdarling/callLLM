"""Run three demonstration queries against the tool calling agent."""

from rich.console import Console
from rich.panel import Panel

from src.agent import run_agentic_loop

console = Console()

SCENARIOS = (
    (
        "Scenario 1: Known order lookup",
        "What is the current shipping status of order A123?",
    ),
    (
        "Scenario 2: Unknown order lookup",
        "Can you check the status of order Z999?",
    ),
    (
        "Scenario 3: Customer and order lookups",
        (
            "Look up the account for rohan.sharma@example.com and tell me the "
            "shipping status of all their orders."
        ),
    ),
)


def run_demo_suite() -> None:
    console.print(
        Panel(
            "Gemini 3.6 Flash tool calling demonstration",
            title="callLLM Demo",
            border_style="bold blue",
        )
    )

    for index, (title, query) in enumerate(SCENARIOS, start=1):
        console.print(
            Panel(
                f"{title}\nQuery: {query}",
                title=f"Scenario {index} of {len(SCENARIOS)}",
                border_style="cyan",
            )
        )
        run_agentic_loop(query)

    console.print(
        Panel(
            "Review the output above for each tool call and final answer.",
            title="Demonstration Finished",
            border_style="green",
        )
    )


if __name__ == "__main__":
    run_demo_suite()
