# callLLM: Deterministic Tool Calling Agent Architecture

A production grade implementation of schema constrained tool calling and bounded agentic execution built with the official Google Gemini Python SDK (`google_genai`) targeting `gemini-2.5-flash`.

Repository: https://github.com/mantisdarling/callLLM

## Core Architectural Thesis

Modern agentic systems require predictable, verifiable, and secure execution boundaries. High level agent frameworks frequently obscure model reasoning and state transitions behind opaque abstractions. In contrast, this repository demonstrates a manual, deterministic ReAct execution loop where every reasoning trace, tool invocation schema, local function dispatch, and model assimilation step remains inspectable and testable.

The architecture synthesizes two foundational applied AI research paradigms:
* **ReAct Paradigm (Yao et al., 2023):** Interleaving reasoning traces with domain actions, enabling dynamic multi step plans while grounding decisions in external data.
* **Toolformer Mechanism (Schick et al., 2023):** Teaching language models when and how to invoke explicit API signatures via strict parameter typing, deterministic schema decoding, and structured dictionary ingestion.

## System Lifecycle Flow

The execution cycle enforces bounded iterations with zero automatic client side tool execution:

```
[ User Query ]
       │
       ▼
[ Gemini 2.5 Flash Engine ] (Model: gemini-2.5-flash, temperature: 0.0)
       │
       ▼ (Emits structured function call request)
[ Schema Validation Layer ] (Pydantic models sanitize input arguments)
       │
       ▼ (Dispatches to registered callable)
[ Immutable Backend Store ] (MappingProxyType and frozen dataclasses)
       │
       ▼ (Returns structured Python dictionary payload)
[ Function Response Assimilation ] (Types.Part.from_function_response)
       │
       ▼
[ Grounded Terminal Synthesis ] (Synthesizes factual natural language answer)
```

## Repository Scaffold

```
callLLM/
  .env.example
  .gitignore
  requirements.txt
  README.md
  src/
    __init__.py
    config.py
    database.py
    tools.py
    agent.py
    main.py
  tests/
    __init__.py
    test_tools.py
```

## Architectural Invariants and Security

1. **State Immutability at Runtime:** All customer and order entities are stored within `types.MappingProxyType` instances holding frozen dataclass objects. Neither model hallucinations nor malfunctioning tools can mutate backend state during runtime execution.
2. **Deterministic Tool Dispatch:** Tool execution delegates through a read only registry mapping validated function identifiers to pure Python functions. Unregistered tool calls trigger deterministic error payloads rather than arbitrary code execution.
3. **Pydantic Input Sanitization:** Function arguments undergo boundary validation, casing normalization, and regex validation prior to executing database lookups.
4. **Secret Protection Invariants:** Environment validation in `src/config.py` enforces present, non empty, and non placeholder credentials while ensuring tokens never appear in exception messages, logs, or execution traces.
5. **Bounded Execution Loop:** The ReAct loop enforces a strict iteration threshold (`max_iterations=5`), preventing runaway recursive API consumption.

## Environment Configuration

Clone the repository and prepare the Python environment:

```powershell
git clone https://github.com/mantisdarling/callLLM.git
cd callLLM
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install google_genai python_dotenv pydantic rich pytest
```

Copy the environment template and insert your valid Google Gemini API key:

```powershell
cp .env.example .env
```

Set your secret key inside `.env`:

```
GEMINI_API_KEY=your_actual_api_key_here
```

## Running the Automated Benchmark Suite

Execute the three verification scenarios sequentially:

```powershell
python src/main.py
```

The demonstration suite executes three test scenarios:
1. **Single Tool Lookup:** Queries order status for known identifier `A123`.
2. **Edge Case Handling:** Queries missing order identifier `Z999`, verifying honest abstention without hallucination.
3. **Multi Tool Chaining:** Resolves account profile for `rohan.sharma@example.com`, parses associated order references, and sequentially queries fulfillment status for all linked shipments.

## Sample Terminal Output

```
┌────────────────────────────── System Benchmark Suite ──────────────────────────────┐
│ Starting Deterministic Tool Calling Demonstration Suite                            │
│ Testing Gemini 2.5 Flash with ReAct Bounded Execution Loop                         │
└────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────── Benchmark Case 1 of 3 ──────────────────────────────┐
│ Scenario 1: Single Tool Lookup for Known Order                                     │
│ Query: What is the current shipping status of order A123?                          │
└────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────── User Query ────────────────────────────────────┐
│ What is the current shipping status of order A123?                                 │
└────────────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────── Raw Model Tool Call Step ─────────────────────────────┐
│ {                                                                                  │
│   "function": "lookup_order_status",                                               │
│   "arguments": {                                                                   │
│     "order_id": "A123"                                                             │
│   }                                                                                │
│ }                                                                                  │
└────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────── Local Python Execution Output ──────────────────────────┐
│ {                                                                                  │
│   "status": "success",                                                             │
│   "order_id": "A123",                                                              │
│   "shipping_status": "in_transit",                                                 │
│   "carrier": "BlueDart Express",                                                   │
│   "estimated_delivery": "November 25, 2026",                                       │
│   "items": [                                                                       │
│     "Mechanical Keyboard",                                                         │
│     "USB C Hub"                                                                    │
│   ]                                                                                │
│ }                                                                                  │
└────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────── Final Grounded Response ─────────────────────────────┐
│ Order A123 is currently in transit with BlueDart Express.                          │
│ Estimated delivery is November 25, 2026. The shipment contains:                    │
│ * Mechanical Keyboard                                                              │
│ * USB C Hub                                                                        │
└────────────────────────────────────────────────────────────────────────────────────┘
```

## Offline Unit Test Suite

Execute the comprehensive offline test suite verifying schema validation, input normalization, immutability guarantees, and dispatch protection without requiring active network connectivity or API credentials:

```powershell
pytest
```

All 11 unit test assertions validate deterministically offline.
