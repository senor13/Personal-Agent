# Daily Tracker — 2026-04-02 — Custom Tools Complete, Metrics, Evals, GitHub Push

---

## Quick Summary
- Completed `youtube_search` with view count filtering and sort
- Built eval framework end to end — test cases, runner, LLM-as-judge, results saved to JSON
- Built metrics tracking — latency, tokens, cost per turn saved to `logs/metrics.jsonl`
- Pushed project to GitHub: https://github.com/senor13/Personal-Agent
- Updated CLAUDE.md with phases 7-10

---

## What Was Built Today

### `youtube_search` — Completed
- Two API calls when view filtering needed: `search.list` + `videos.list`
- `sort_by_views` parameter — sorts results by view count descending
- `min_view_count` filter — skips videos below threshold using `continue`
- `function_map` pattern with `**arguments` unpacking for clean routing
- try/except around custom tool calls so failures don't break the agent loop

### Eval Framework — `evals/run_evals.py` ✅ Complete
- Loads test cases from `evals/test_cases.json`
- Runs agent fresh for each test case
- Extracts tool sequence from conversation history using `isinstance(item, dict)` check
- Compares actual vs expected tool sequence
- LLM-as-judge using GPT-4o (more capable than the agent being evaluated)
- Saves results to `evals/results.json` with run id, tool eval, response eval, timestamp

### Test Cases — `evals/test_cases.json`
Three cases covering:
- `eval_001` — save memory (save Amit's email)
- `eval_002` — update memory (update user email)
- `eval_003` — YouTube search + save memory (find vizuara videos + save preference)

### Metrics — `ai/metrics.py` pattern in `run_bot.py` ✅ Complete
- Turn timer started in `process_message` before `run_agent`
- Token counts accumulated per LLM call inside agent loop: `response.usage.prompt_tokens` + `response.usage.completion_tokens`
- Tool call latency measured with `time.time()` around each tool execution
- Cost calculated: `(input_tokens * 0.00000015) + (output_tokens * 0.0000006)`
- Written to `logs/metrics.jsonl` in append mode — one JSON object per line per turn

Sample metrics entry:
```json
{"run_id": "2026-04-02T18:38:27", "total_latency": 8.5, "tool_latency": 0, "input_token_count": 7211, "output_token_count": 479, "cost_usd": 0.00137}
```

**Observation:** Input tokens consistently ~7165 even for simple messages — system prompt + full memory load is expensive. This is exactly what RAG will fix in Phase 6.

---

## Key Concepts Learned Today

### JSONL vs JSON for logs
JSONL = one JSON object per line. Append with `"a"` mode, no need to read/parse/rewrite the whole file. Perfect for logs where you just add entries.

### `continue` in loops
Skips the current iteration without breaking the loop. Used to filter videos below `min_view_count` threshold.

### Object vs dict in conversation history
System/user/tool messages = dicts (created with `{}`). Assistant messages = OpenAI objects (appended directly from API response). Use `isinstance(item, dict)` to distinguish them when iterating.

### LLM-as-judge pattern
Use a more capable model (GPT-4o) to evaluate a less capable model (GPT-4o mini). Pass expected outcome + actual response, ask for 1-5 score. Separate from the agent's own LLM calls — different purpose, different prompt.

### Agent non-determinism
Same eval input can produce different tool sequences across runs. This is normal for LLMs. Need to run each test case multiple times and measure pass rate, not just single pass/fail.

### try/except for tool failures
Without it: tool crashes → `tool_output` undefined → tool response not appended → next LLM call fails with 400 error. With it: error becomes the tool output, loop continues cleanly.

---

## Key Observations from Metrics

- Input tokens ~7k per turn — memory + system prompt is large
- Simple turns (no tools) cost ~$0.001
- Tool turns cost more due to multiple LLM calls
- Phase 6 RAG goal: reduce input tokens by only loading relevant memory chunks

---

## GitHub
- Repo: https://github.com/senor13/Personal-Agent
- CLAUDE.md excluded from tracking (`git rm --cached`)
- PDFs, credentials, memory data, eval results all gitignored
- README to be written after Phase 6 with full learning journey

---

## Project Status

**Phase 1 — Complete**
**Phase 2a — Complete**
**Phase 2b — Complete**
**Phase 3 — Complete**
**Phase 4 — Complete**
**Phase 5 — In Progress** (custom tools done, tool description experiments pending)
**Phase 6 — Starting next (RAG)**
**Phase 7 — Not started (Metrics — partially implemented)**
**Phase 8 — In Progress (Eval framework done)**

---

## Tomorrow — Resume Here

Phase 6 RAG:
1. Pick one PDF (AI Engineering by O'Reilly)
2. Extract text from PDF
3. Chunk into ~500 token pieces
4. Embed with `text-embedding-3-small`
5. Store in ChromaDB
6. Build retrieval tool the agent can call
7. Test: "summarize the section on orchestration frameworks"
