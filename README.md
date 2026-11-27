# callLLM

A small Gemini project that demonstrates manual tool calling. The model asks Python to run a function, reads the function result, and then writes a final answer.

## What is a tool call?

A tool call happens when the model does not answer from memory alone. Instead, it returns a structured request such as `lookup_order_status(order_id="A123")`. Python runs the matching function and sends the result back to the model.

This project keeps that step visible by disabling the SDK's automatic function execution. You can see the raw model response, the local Python result, and the final answer.

## Features

- Uses the official Gemini SDK with `gemini-3.6-flash`.
- Defines `lookup_order_status(order_id: str) -> dict`.
- Includes six fake orders and five fake customers.
- Supports known orders, unknown orders, and chained customer and order lookups.
- Validates tool inputs before looking up records.
- Prints the raw Gemini response before executing a function call.
- Sends function results back in a `user` content turn, as required by the Gemini `generate_content` endpoint.
- Limits the loop to five model requests.
- Includes offline tests that do not need an API key.

## Requirements

- Python 3.10 or newer
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)

The tested package versions are recorded in `requirements.txt`.

## Setup

Run these commands from the project folder.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` and replace the placeholder with your real key.

```dotenv
GEMINI_API_KEY=your_api_key_here
```

The `.env` file is ignored by Git. Never commit it or paste the key into source code, screenshots, README files, or terminal output.

## Run the demo

```powershell
python -m src.main
```

The demo runs three queries:

1. Look up the known order `A123`.
2. Look up the unknown order `Z999`.
3. Look up a customer and then check all of their orders.

For each tool call, the output shows:

1. The raw Gemini response containing the function call.
2. The dictionary returned by the Python function.
3. The final natural language answer from Gemini.

The exact wording of the final answer can vary between runs.

## Run the tests

```powershell
python -m pytest -ra
```

The tests use fake Gemini responses. They cover tool execution, the `user` content role used for function responses, unknown tools, unknown orders, empty responses, exceptions, multiple function calls, and the iteration limit. No API key or network access is required.

## Project structure

```text
callLLM/
  .env.example
  .gitignore
  requirements.txt
  README.md
  src/
    __init__.py
    agent.py
    config.py
    database.py
    main.py
    tools.py
  tests/
    __init__.py
    test_agent.py
    test_tools.py
```

## Example output

This is an abbreviated illustration, not a recorded API response.

```text
Raw Gemini Response
{
  "candidates": [
    {
      "content": {
        "parts": [
          {
            "function_call": {
              "args": { "order_id": "A123" },
              "name": "lookup_order_status"
            }
          }
        ],
        "role": "model"
      }
    }
  ]
}

Local Python Execution Output
{
  "status": "success",
  "order_id": "A123",
  "shipping_status": "in_transit",
  "carrier": "BlueDart Express",
  "estimated_delivery": "November 25, 2026",
  "items": ["Mechanical Keyboard", "USB C Hub"]
}

Final Grounded Response
Order A123 is currently in transit with BlueDart Express.
```

## Submission evidence

Use screenshots from your own real run. Do not show the API key.

1. Raw Gemini function call for `A123` (`01-live-tool-call.png`).
2. Python function result and final grounded answer for `A123` (`02-local-tool-result.png`).
3. Safe handling of the unknown order `Z999` (`03-unknown-order.png`).
4. Passing automated test suite (`04-chaining-and-tests.png`).

The assignment also requires a GitHub repository, a LinkedIn post with a short demo video or screenshots, and the dashboard submission. Those external steps are not completed by running this project locally.
