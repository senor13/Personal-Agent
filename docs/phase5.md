# Phase 5 — Experiment and Expand

---

## What Was Built

Added three custom tools to the agent. Custom tools are local Python functions exposed to the LLM via schemas — same pattern as MCP tools but no external server needed.

---

## Files Created / Modified

| File | What changed |
|---|---|
| `AI/tools.py` | New — save_memory, update_memory, youtube_search |
| `AI/agent.py` | Added function_map, custom tool routing, try/except, stop_flag, metrics |
| `AI/memory.py` | Updated read_memory() to include id in output, added extract_memory() |
| `AI/llm.py` | Added call_llm_advanced() using GPT-4o |

---

## Custom Tools

### `save_memory(category, content)`
Called when user explicitly asks agent to remember something going forward. Thin wrapper around `add_memory`.

Schema description: "only call when user explicitly asks to remember something long term" — this wording prevents the agent from saving memory on every message.

### `update_memory(id, new_content)`
Updates an existing memory entry by id. LLM knows the id because `read_memory()` now includes it in the system prompt:
```
mem_001: Amit's email is amit.iitkgp18@gmail.com
mem_002: I prefer morning meetings
```

### `youtube_search(query, channel_id, published_after, min_view_count, max_results, sort_by_views)`
Wraps YouTube Data API v3. Two API calls when view filtering needed:
1. `search.list` — relevance-ranked results
2. `videos.list` — view count statistics

`sort_by_views=True` triggers second call and sorts descending. `min_view_count` filters out videos below threshold using `continue`.

---

## function_map Pattern

```python
function_map = {
    "save_memory": save_memory,
    "update_memory": update_memory,
    "youtube_search": youtube_search
}
# routing:
tool_output = function_map[tool_name](**arguments)
```

`**arguments` unpacks the dict into keyword arguments — works for any function regardless of parameter count. Adding a new custom tool = add to function_map, zero other changes.

---

## Metrics Instrumentation

Token counts and tool latency collected inside `run_agent()`:
- `response.usage.prompt_tokens` and `response.usage.completion_tokens` after each LLM call
- `time.time()` around each tool execution for tool latency

Returned from `run_agent()` as extra values. Written to `logs/metrics.jsonl` in `run_bot.py`.

Cost formula:
```python
cost_usd = (input_tokens * 0.00000015) + (output_tokens * 0.0000006)
```

**Key observation:** Input tokens ~7k per simple turn — full memory load is expensive. Phase 6 RAG will reduce this significantly.

---

## Key Concepts Learned

### Tool description as control surface
The schema description is what tells the LLM when to call the tool. "Only call when user explicitly asks" prevents over-calling. Vague descriptions = wrong tool picked. Specific descriptions = precise behavior. This is prompt engineering applied to tools.

### Custom tools vs MCP tools
MCP tools come from external servers. Custom tools are local Python functions. The LLM can't tell the difference — it sees the same schema format. Routing in `agent.py` handles which path to take.

### try/except for tool failures
Without it: tool crashes → tool_output undefined → tool response not appended → next LLM call fails with 400 error. With it: error becomes the tool output string, loop continues cleanly.

### YouTube API — two call pattern
`search.list` returns relevance-ranked results with no view counts. `videos.list` returns statistics. To filter/sort by views: search first, get stats second, then filter/sort. Only make second call when needed.

### JSONL for logs
Append with `"a"` mode — no need to read/parse/rewrite the whole file. One JSON object per line. Ideal for high-frequency log writes.

---

## Experiments Pending (Phase 5 continued)

- Reword a tool description — does wording change which tool the agent picks?
- Few-shot prompting — add example ReAct trace to system prompt
- Add new MCP server — verify zero changes to agent.py needed

---

## Common Mistakes Made

### `tool_name(arguments)` — calling a string
`tool_name` is a string, not callable. Fix: `function_map[tool_name](**arguments)`.

### Missing try/except around custom tools
Tool crash → tool_output undefined → OpenAI 400 error on next call. Always wrap custom tool calls.

### YouTube API channel name vs channel ID
LLM passes channel name, API expects channel ID (`UCxxxxxx`). Include channel name in query instead — YouTube search handles it.
