"""Bounded ReAct execution engine orchestrating model reasoning and deterministic tool dispatch."""

import json
import os
from typing import List, Optional
from google import genai
from google.genai import types
from rich.console import Console
from rich.panel import Panel
from src.config import get_gemini_api_key
from src.tools import GEMINI_TOOLS, TOOL_REGISTRY

DEFAULT_MODEL = "gemini-2.5-flash"
MODEL_NAME = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
MAX_ITERATIONS = 5

console = Console()


def run_agentic_loop(
    user_query: str,
    client: Optional[genai.Client] = None,
    max_iterations: int = MAX_ITERATIONS,
):
    """Execute bounded ReAct execution loop with schema constrained decoding and tool dispatch.

    Iteratively requests model candidate tokens with disabled automatic tool execution,
    inspects structured tool calls, validates invocations against deterministic registry,
    executes Python callables over immutable state, and appends structured tool responses
    until the model synthesizes a final grounded answer or iteration limits are reached,
    mirroring the ReAct interleaved reasoning paradigm established by Yao et al. (2023).
    """
    if client is None:
        api_key = get_gemini_api_key()
        client = genai.Client(api_key=api_key)

    console.print(
        Panel(
            user_query,
            title="User Query",
            border_style="cyan",
        )
    )

    contents: List[types.Content] = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_query)],
        )
    ]

    generation_config = types.GenerateContentConfig(
        tools=GEMINI_TOOLS,
        temperature=0.0,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )

    iteration_counter = 0

    while iteration_counter < max_iterations:
        iteration_counter += 1

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=generation_config,
        )

        candidate_content = response.candidates[0].content
        contents.append(candidate_content)

        function_calls = response.function_calls

        if not function_calls:
            final_grounded_text = response.text or ""
            console.print(
                Panel(
                    final_grounded_text,
                    title="Final Grounded Response",
                    border_style="green",
                )
            )
            return final_grounded_text

        response_parts: List[types.Part] = []

        for call in function_calls:
            function_name = call.name
            function_arguments = dict(call.args) if call.args else {}

            call_payload = {
                "function": function_name,
                "arguments": function_arguments,
            }
            console.print(
                Panel(
                    json.dumps(call_payload, indent=2),
                    title="Raw Model Tool Call Step",
                    border_style="yellow",
                )
            )

            if function_name not in TOOL_REGISTRY:
                tool_output = {
                    "status": "error",
                    "message": f"Unregistered tool invocation requested: {function_name}",
                }
            else:
                try:
                    tool_callable = TOOL_REGISTRY[function_name]
                    tool_output = tool_callable(**function_arguments)
                except Exception as execution_error:
                    tool_output = {
                        "status": "error",
                        "message": f"Tool execution exception: {str(execution_error)}",
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

        contents.append(
            types.Content(
                role="user",
                parts=response_parts,
            )
        )

    exhaustion_message = "Bounded execution loop reached iteration limit without terminal answer"
    console.print(
        Panel(
            exhaustion_message,
            title="Execution Limit Exceeded",
            border_style="red",
        )
    )
    return exhaustion_message
