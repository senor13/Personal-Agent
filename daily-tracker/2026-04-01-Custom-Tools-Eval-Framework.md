# Daily Tracker — 2026-04-01 — Custom Tools + Eval Framework Start

---

## Quick Summary
- Built three custom tools: `save_memory`, `update_memory`, `youtube_search`
- Added `function_map` pattern for routing custom tool calls in `agent.py`
- Updated `read_memory()` to include memory ids in system prompt
- Started eval framework — `evals/run_evals.py` partially built
- Updated CLAUDE.md with new phases (7-10)

---

## What Was Built Today

### Custom Tools — `ai/tools.py`

**`save_memory(category, content)`**
- Thin wrapper around `add_memory`
- Called when user explicitly asks agent to remember something going forward
- Schema in `agent.py` with description: "only call when user explicitly asks to remember something long term"

**`update_memory(id, new_content)`**
- Loads `long_term.json`, finds entry by id, replaces content, saves back
- LLM can identify the id because `read_memory()` now includes id in system prompt
- Schema in `agent.py`

**`youtube_search(query, channel_id, published_after, min_view_count, max_results, sort_by_views)`**
- Wraps YouTube Data API v3
- Two API calls when view filtering needed: `search.list` + `videos.list`
- `continue` pattern to skip videos below `min_view_count`
- Sorted by view count descending when `sort_by_views=True`
- Only makes second API call when `min_view_count` or `sort_by_views` is set

### `function_map` pattern in `agent.py`
```python
function_map = {"save_memory": save_memory, "update_memory": update_memory, "youtube_search": youtube_search}
# routing:
tool_output = function_map[tool_name](**arguments)
```
`**arguments` unpacks the dict into keyword arguments — works for any function regardless of parameter names.

### `read_memory()` updated
Now includes id in output:
```
mem_001: Amit's email is amit.iitkgp18@gmail.com
mem_002: I prefer morning meetings
```
LLM sees ids in system prompt → can pass correct id to `update_memory`.

### Eval Framework — `evals/run_evals.py` (in progress)
- Loads test cases from `evals/test_cases.json`
- Connects MCP servers once outside the loop
- Runs agent fresh for each test case
- Extracts tool sequence from conversation history
- Compares actual vs expected tool sequence
- LLM-as-judge for outcome quality — not yet implemented

---

## Key Concepts Learned Today

### `**kwargs` unpacking
```python
function_map[tool_name](**arguments)
```
Unpacks `{"category": "people", "content": "..."}` into `save_memory(category="people", content="...")`. Works for any function — routing code never needs to change when new tools are added.

### Custom tools vs MCP tools
MCP tools come from external servers via `fetch_tools()`. Custom tools are local Python functions. Both use the same schema format and same routing pattern — the LLM can't tell the difference.

### Tool description as control surface
The description is what tells the LLM when to call the tool. "Only call when user explicitly asks to remember" prevents the agent from saving memory on every message. Wording directly controls agent behavior.

### YouTube API — two call pattern
`search.list` returns relevance-ranked results, no view counts. `videos.list` returns statistics including view count. To filter/sort by views: search first, then get stats, then filter/sort.

### Object vs dict in conversation history
System/user/tool messages are dicts `{}`. Assistant messages are OpenAI message objects. Access dicts with `[]`, objects with `.`. Mix in history → use `isinstance(item, dict)` to check type before accessing.

### Eval design
- Test cases = fixed inputs + expected tool sequence + expected outcome
- Eval runner runs agent fresh on each input, captures what happened, compares to expected
- Conversation history is the output of running the agent, not the input to evals
- Tool sequence comparison = list equality check (automatic)
- Outcome quality = LLM-as-judge (scores 1-5)

---

## Key Questions Asked & What You Learned

**Q: Should `save_memory` be a tool or just `/remember`?**
Both. `/remember` extracts from full conversation at session end. `save_memory` tool handles explicit in-conversation "remember this" requests. Different use cases, both valid.

**Q: How does `update_memory` know which entry to update?**
LLM reads memory ids from system prompt, identifies which one to update, passes the id. No fuzzy matching needed — id lookup is reliable.

**Q: Is view count sorting a separate tool?**
No — a parameter on `youtube_search`. `sort_by_views=True` triggers second API call and sorts results. Keep related functionality in one tool.

**Q: Can eval conversation history be reused across runs?**
No — each eval run starts fresh. History is captured per run and compared against expected. Old conversation history from real usage is not useful for evals.

---

## Bugs Fixed Today

### `tool_output = tool_name(arguments)` — calling a string
`tool_name` is a string, not callable. Fix: `function_map[tool_name](**arguments)`.

### `search_list2` vs `search_list_2` — inconsistent naming
Typo caused NameError. Fixed by being consistent.

### `video_ids.append` outside loop
Indentation error — append was at same level as loop. Fixed by indenting inside `for`.

### Missing `:` after `if` in eval runner
Syntax error. Fixed.

---

## CLAUDE.md Updates

Added phases 7-10:
- **Phase 7** — Observability and Metrics (`ai/metrics.py`)
- **Phase 8** — Evaluation Framework (`evals/`)
- **Phase 9** — Guardrails
- **Phase 10** — Production (deploy, webhook)

---

## Project Status

**Phase 1 — Complete**
**Phase 2a — Complete**
**Phase 2b — Complete**
**Phase 3 — Complete**
**Phase 4 — Complete**
**Phase 5 — In Progress** (custom tools done, experiments next)
**Phase 6 — Not started**
**Phase 7 — Not started**
**Phase 8 — In Progress** (eval runner partially built)

---

## Tomorrow — Resume Here

1. **LLM-as-judge** — add to `run_evals.py` after tool sequence check
2. **Results output** — save scores to `evals/results/`
3. **Write test cases** — `evals/test_cases.json` with 5-10 cases
4. **Run evals end to end** — test the full pipeline
5. **Metrics** — `ai/metrics.py` for latency and cost
6. **Gmail tool** — if time allows
