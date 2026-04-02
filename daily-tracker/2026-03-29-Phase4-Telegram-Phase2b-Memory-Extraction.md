# Daily Tracker — 2026-03-29 — Phase 4 Complete + Phase 2b Auto Memory Extraction

---

## Quick Summary
- Completed Phase 4 — Telegram bot fully working end to end
- Added `/stop` command with mid-loop interrupt
- Completed Phase 2b — auto memory extraction via `/remember` and `/stop`
- Fixed multiple bugs in memory extraction pipeline

---

## What Was Built Today

### Phase 4 — Telegram Bot ✅ Complete

**`bot/telegram_bot.py`**
- User ID lock — rejects all non-allowed users before any LLM call
- `handle_message` — routes text messages to `run_bot.process_message`
- `stop_command` — sets `stop_flag[0] = True`, triggers memory extraction, replies "Stopping."
- `remember_command` — triggers `extract_memory`, replies "Memories saved."
- `main()` — builds app, registers handlers, starts polling

**`bot/run_bot.py`**
- Module-level setup: connects MCP servers, loads memory, initializes conversation history
- `stop_flag = [False]` — mutable list passed to `run_agent` so handler can signal stop mid-loop
- `process_message(message)` — resets stop flag, appends message, calls `run_agent`, updates history in place with `[:]`

**`ai/agent.py`**
- Added `stop_flag=None` parameter to `run_agent`
- Checks `stop_flag[0]` at top of while loop — returns `None, message` if set

### Phase 2b — Auto Memory Extraction ✅ Complete

**`ai/memory.py` — `extract_memory(conversation_history)`**
- Filters system messages using list comprehension: `[item for item in conversation_history if item["role"] != "system"]`
- Makes second LLM call with extraction prompt
- Parses JSON response
- Calls `add_memory` for each extracted fact

---

## Key Concepts Learned Today

### Why `conversation_history[:] = updated_history` not `=`
Assignment inside an async function makes Python treat the variable as local — `UnboundLocalError` on the line above. `[:]` updates the list in-place, no assignment, no scope issue.

### Why module-level code in `run_bot.py` runs at import time
Every line at module level executes when Python imports the file. `connect_server()` at module level = connects once at startup. Putting `disconnect_server()` at module level = disconnects immediately after import, before the bot starts.

### `/stop` uses a mutable list as a flag
Plain boolean can't be passed by reference in Python. A list `[False]` can — `stop_flag[0] = True` in the handler updates the same object the agent loop is checking.

### Two LLM calls, two jobs
ReAct loop call: reasons, selects tools, acts. Extraction call: reads conversation, summarizes facts. Same model, same wrapper, completely different prompts and purposes. This pattern is common in production AI pipelines.

### List comprehension for filtering
```python
[item for item in some_list if condition]
```
Creates a new filtered list without mutating the original.

---

## Bugs Fixed Today

### `conversation_history = updated_history` — UnboundLocalError
Python sees assignment inside function → treats as local → reference before assignment error.
**Fix:** `conversation_history[:] = updated_history`

### `rocess1` typo
Missing `p` in variable name. **Fix:** `process1`

### `from telegram import update` (lowercase)
Type hint used `Update` (capital) but import was lowercase — crash on import.
**Fix:** `from telegram import Update`

### `if __name__` indented inside `main()`
**Fix:** Move to column 0.

### `disconnect_server` at module level in `run_bot.py`
Ran at import time, immediately killing the MCP connections.
**Fix:** Removed entirely — OS cleans up subprocesses when process exits.

### LLM wrapping JSON in markdown fences
`json.loads()` crashed on ` ```json\n[]\n``` `.
**Fix:** Added "Return only raw JSON, no markdown, no code fences" to extraction prompt.

### Old memories being re-saved
System prompt contains previous memories → `extract_memory` saw them as new facts.
**Fix:** Filter `role == "system"` messages before passing to `extract_memory`.

### Extraction prompt example being saved as real fact
Example used `"User's name is Sagrika"` — LLM saved it.
**Fix:** Use obviously fake placeholder values in example.

---

## Key Questions Asked & What You Learned

**Q: Does bot auto-update when I change files?**
No — Python loads files once at startup. Always restart the process after code changes.

**Q: Will `disconnect_server` be needed when bot is killed?**
No — when the Python process exits, all subprocess pipes close. MCP servers exit on their own.

**Q: What's the difference between `json.dump` and `json.dumps`?**
`json.dump` writes to a file object. `json.dumps` returns a string. Use `dumps` when you need a string (e.g. for `reply_text`).

**Q: Should `save_memory` be a tool the agent can call?**
Yes — useful when users say "remember this going forward." Complements `/remember` which extracts from the full conversation. Tool description controls when the agent calls it — write it specifically: "only call when user explicitly asks to remember something long term."

---

## Project Status

**Phase 1 — Complete**
**Phase 2a — Complete**
**Phase 2b — Complete**
**Phase 3 — Complete**
**Phase 4 — Complete**
**Phase 5 — Starting next**

---

## Tomorrow — Resume Here

Phase 5 — Tool description experiment:
- Pick a Google Calendar tool
- Run a task, note which tool the agent picks
- Reword the tool description (vague → specific or vice versa)
- Run the same task again
- Did the agent's tool selection change?

Question to answer: **how much does tool description wording control agent behavior?**
