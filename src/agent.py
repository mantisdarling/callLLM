"""Run a bounded Gemini tool calling loop."""

import json
import os

from google import genai
from google.genai import types
from rich.console import Console
from rich.panel import Panel

from src.config import get_gemini_api_key
from src.tools import GEMINI_TOOLS, TOOL_REGISTRY

DEFAULT_MODEL = "gemini-3.6-flash"
MODEL_NAME = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
MAX_ITERATIONS = 5

console = Console()


def run_agentic_loop(
    user_query: str,
    client: genai.Client | None = None,
    max_iterations: int = MAX_ITERATIONS,
) -> str:
    """Ask Gemini to use tools until it returns a final text answer."""
    if max_iterations < 1:
        raise ValueError("max_iterations must be at least 1")

    if client is None:
        client = genai.Client(api_key=get_gemini_api_key())

    console.print(Panel(user_query, title="User Query", border_style="cyan"))

    contents: list[types.Content] = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_query)],
        )
    ]
    generation_config = types.GenerateContentConfig(
        tools=GEMINI_TOOLS,
        temperature=0.0,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True
        ),
    )

    for _ in range(max_iterations):
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=generation_config,
        )

        if not response.candidates or response.candidates[0].content is None:
            raise RuntimeError("Gemini returned an empty or blocked response")

        candidate_content = response.candidates[0].content
        contents.append(candidate_content)
        function_calls = [
            part.function_call
            for part in candidate_content.parts or []
            if part.function_call is not None
        ]

        if not function_calls:
            final_answer = response.text or ""
            if not final_answer.strip():
                raise RuntimeError("Gemini returned no text or function call")
            console.print(
                Panel(
                    final_answer,
                    title="Final Grounded Response",
                    border_style="green",
                )
            )
            return final_answer

        raw_response = response.model_dump_json(indent=2, exclude_none=True)
        console.print(
            Panel(raw_response, title="Raw Gemini Response", border_style="yellow")
        )

        response_parts: list[types.Part] = []
        for call in function_calls:
            if not call.name:
                raise RuntimeError("Gemini returned a function call without a name")

            function_name = call.name
            function_arguments = dict(call.args or {})
            tool_callable = TOOL_REGISTRY.get(function_name)

            if tool_callable is None:
                tool_output = {
                    "status": "error",
                    "message": "Unknown tool",
                }
            else:
                try:
                    tool_output = tool_callable(**function_arguments)
                except Exception:  # noqa: BLE001
                    tool_output = {
                        "status": "error",
                        "message": "Tool execution failed",
                    }

            console.print(
                Panel(
                    json.dumps(tool_output, indent=2),
                    title="Local Python Execution Output",
                    border_style="magenta",
                )
            )
            response_parts.append(
                types.Part.from_function_response(
                    name=function_name,
                    response=tool_output,
                )
            )

        contents.append(types.Content(role="user", parts=response_parts))

    exhaustion_message = (
        "Execution stopped after reaching the iteration limit without a final answer"
    )
    console.print(
        Panel(
            exhaustion_message,
            title="Execution Limit Reached",
            border_style="red",
        )
    )
    return exhaustion_message
