"""Offline tests for the Gemini tool calling loop."""

import pytest
from google.genai import types

from src import agent


class FakeModels:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.requests = []

    def generate_content(self, *, model, contents, config):
        self.requests.append(
            {
                "model": model,
                "contents": list(contents),
                "config": config,
            }
        )
        return next(self.responses)


class FakeClient:
    def __init__(self, responses):
        self.models = FakeModels(responses)


def function_call_response(name, arguments):
    return types.GenerateContentResponse(
        candidates=[
            types.Candidate(
                content=types.Content(
                    role="model",
                    parts=[
                        types.Part.from_function_call(
                            name=name,
                            args=arguments,
                        )
                    ],
                ),
                finish_reason=types.FinishReason.STOP,
            )
        ]
    )


def text_response(text):
    return types.GenerateContentResponse(
        candidates=[
            types.Candidate(
                content=types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=text)],
                ),
                finish_reason=types.FinishReason.STOP,
            )
        ]
    )


def test_known_order_uses_tool_and_returns_final_answer(capsys):
    client = FakeClient(
        [
            function_call_response("lookup_order_status", {"order_id": "A123"}),
            text_response("Order A123 is in transit."),
        ]
    )

    answer = agent.run_agentic_loop(
        "What is the status of order A123?",
        client=client,
    )

    assert answer == "Order A123 is in transit."
    assert len(client.models.requests) == 2
    second_contents = client.models.requests[1]["contents"]
    assert [content.role for content in second_contents] == ["user", "model", "user"]
    tool_response = second_contents[-1].parts[0].function_response
    assert tool_response.name == "lookup_order_status"
    assert tool_response.response["shipping_status"] == "in_transit"
    output = capsys.readouterr().out
    assert "Raw Gemini Response" in output
    assert "function_call" in output


def test_unknown_order_returns_not_found_to_model():
    client = FakeClient(
        [
            function_call_response("lookup_order_status", {"order_id": "Z999"}),
            text_response("Order Z999 was not found."),
        ]
    )

    answer = agent.run_agentic_loop("Check order Z999", client=client)

    assert answer == "Order Z999 was not found."
    tool_content = client.models.requests[1]["contents"][-1]
    assert tool_content.role == "user"
    assert tool_content.parts[0].function_response.response["status"] == "not_found"


def test_unknown_tool_returns_safe_error():
    client = FakeClient(
        [
            function_call_response("unknown_tool", {}),
            text_response("That tool is unavailable."),
        ]
    )

    agent.run_agentic_loop("Use a tool", client=client)

    tool_content = client.models.requests[1]["contents"][-1]
    assert tool_content.parts[0].function_response.response == {
        "status": "error",
        "message": "Unknown tool",
    }


def test_tool_exception_does_not_leak_details(monkeypatch):
    def broken_tool():
        raise RuntimeError("private internal detail")

    monkeypatch.setattr(agent, "TOOL_REGISTRY", {"broken_tool": broken_tool})
    client = FakeClient(
        [
            function_call_response("broken_tool", {}),
            text_response("The tool failed."),
        ]
    )

    agent.run_agentic_loop("Run the tool", client=client)

    tool_content = client.models.requests[1]["contents"][-1]
    assert tool_content.parts[0].function_response.response == {
        "status": "error",
        "message": "Tool execution failed",
    }


def test_iteration_limit_stops_repeated_tool_calls():
    client = FakeClient(
        [
            function_call_response("lookup_order_status", {"order_id": "A123"}),
            function_call_response("lookup_order_status", {"order_id": "A123"}),
        ]
    )

    answer = agent.run_agentic_loop(
        "Check A123",
        client=client,
        max_iterations=2,
    )

    assert "iteration limit" in answer
    assert len(client.models.requests) == 2


@pytest.mark.parametrize(
    "response",
    [
        types.GenerateContentResponse(candidates=[]),
        types.GenerateContentResponse(
            candidates=[types.Candidate(content=None, finish_reason="SAFETY")]
        ),
        types.GenerateContentResponse(
            candidates=[
                types.Candidate(
                    content=types.Content(role="model", parts=[]),
                    finish_reason="STOP",
                )
            ]
        ),
    ],
)
def test_empty_or_blocked_response_raises_clear_error(response):
    client = FakeClient([response])

    with pytest.raises(RuntimeError, match="empty|blocked|no text"):
        agent.run_agentic_loop("Hello", client=client)


def test_invalid_iteration_limit_is_rejected():
    with pytest.raises(ValueError, match="at least 1"):
        agent.run_agentic_loop("Hello", client=FakeClient([]), max_iterations=0)


def test_multiple_function_calls_share_one_tool_response():
    response = types.GenerateContentResponse(
        candidates=[
            types.Candidate(
                content=types.Content(
                    role="model",
                    parts=[
                        types.Part.from_function_call(
                            name="lookup_order_status",
                            args={"order_id": "A123"},
                        ),
                        types.Part.from_function_call(
                            name="lookup_order_status",
                            args={"order_id": "ORD_8801"},
                        ),
                    ],
                ),
                finish_reason="STOP",
            )
        ]
    )
    client = FakeClient([response, text_response("Both orders were found.")])

    answer = agent.run_agentic_loop("Check A123 and ORD_8801", client=client)

    assert answer == "Both orders were found."
    tool_content = client.models.requests[1]["contents"][-1]
    assert tool_content.role == "user"
    assert len(tool_content.parts) == 2
