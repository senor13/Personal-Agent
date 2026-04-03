# Phase 8 — Evaluation Framework

---

## What Was Built

A structured eval framework to measure how well the agent performs — not just how fast or cheap, but whether it does the right thing.

---

## Files Created

| File | What it does |
|---|---|
| `evals/test_cases.json` | Fixed test cases with input, expected tool sequence, expected outcome |
| `evals/run_evals.py` | Runs agent on each test case, scores results, saves to results.json |
| `evals/results.json` | Eval run history — tool eval, LLM judge score, timestamp |

---

## Test Case Format

```json
{
    "id": "eval_001",
    "description": "remember the email id for amit",
    "input": "remember that amit's email id is amitiitkgp18@gmail.com",
    "expected_tool_sequence": ["save_memory"],
    "expected_outcome": "saved amit's email id"
}
```

---

## Eval Runner Flow

1. Load test cases from `evals/test_cases.json`
2. Connect MCP servers once (outside the loop)
3. For each test case:
   - Run agent fresh with the input
   - Extract tool sequence from conversation history
   - Compare actual vs expected tool sequence → pass/fail
   - LLM-as-judge scores actual response vs expected outcome (1-5)
   - Save result to `evals/results.json`

---

## Tool Sequence Extraction

```python
tools_called = []
for item in conversation_history:
    if not isinstance(item, dict) and item.role == "assistant" and item.tool_calls:
        for tool in item.tool_calls:
            tools_called.append(tool.function.name)
```

`isinstance(item, dict)` check needed because conversation history contains both dicts (user/system/tool messages) and OpenAI message objects (assistant messages).

---

## LLM-as-Judge

```python
def judge_response(actual_response, expected_outcome):
    # Uses GPT-4o (more capable than the GPT-4o mini agent being evaluated)
    # Returns score 1-5
```

Judge sees both responses in one message and scores how well actual matches expected.

---

## Key Concepts Learned

### Evals measure quality, metrics measure performance
Metrics: latency, cost, tokens — how it ran. Evals: task success, tool selection, reasoning quality — how well it did. Both needed, different purposes.

### Agent non-determinism
Same input can produce different tool sequences across runs. LLMs are probabilistic. Run each test case multiple times and measure pass rate, not just single run pass/fail.

### LLM-as-judge pattern
Use a more capable model as judge. Pass expected + actual, ask for score. Automates qualitative measurement that would otherwise require manual review.

### When to run evals
- After any system prompt change
- After rewording a tool description
- After adding a new tool
- Before and after switching models
- Before and after RAG implementation

---

## Limitations

- Single run per test case — need multiple runs for reliable pass rate
- `update_memory` test case non-deterministic — depends on LLM correctly reading memory id from system prompt
- Tool sequence comparison is exact match — doesn't handle equivalent sequences
