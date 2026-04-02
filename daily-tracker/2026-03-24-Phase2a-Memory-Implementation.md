# Daily Tracker — 2026-03-24 — Phase 2a Memory Implementation & Phase 3 Prep

---

## Quick Summary
- Completed Phase 1 fully — ReAct loop working end to end
- Built and tested Phase 2a — manual long term memory working
- Agent reads memory at session start and uses it without being asked
- Phase 2b (auto memory extraction) — decided to park for later
- Started discussing Phase 3 — MCP concepts, good mental model established
- Phase 3 implementation starts next session

---

## Files Created / Modified Today

| File | Status | What changed |
|---|---|---|
| `scripts/run_terminal.py` | Updated | Cleaned up loop, added memory loading and saving |
| `ai/memory.py` | New | `add_memory` and `read_memory` functions |
| `ai/prompts.py` | Updated | `prompt()` now accepts `memory` parameter and injects it |
| `memory/long_term.json` | New | Memory storage file — manually seeded for testing |
| `docs/phase1.md` | New | Full phase 1 documentation |
| `docs/phase2.md` | New | Full phase 2 documentation including Phase 2b plan |

---

## What You Built Today

### `ai/memory.py`
Two functions:

**`add_memory(category, content)`**
- Checks if `memory/long_term.json` exists
- If yes — loads existing entries, appends new one, saves back
- If no — creates empty list, appends, saves
- Each entry has: `id`, `category`, `content`, `created_at`
- No return value needed — it's a write operation

**`read_memory()`**
- Reads `memory/long_term.json`
- Iterates over entries and builds a plain string of all `content` fields
- Returns that string to be injected into the system prompt
- Returns `""` if file doesn't exist

### `ai/prompts.py`
`prompt(memory="")` now accepts memory as a parameter and appends it to the system prompt under "What you know about the user."

### `scripts/run_terminal.py`
- Loads memory once at session start via `read_memory()`
- Passes it to `prompt(memory)` when building system message
- After conversation ends, asks user if they want to save anything to memory
- If yes, asks for category and calls `add_memory(category, content)`

---

## Key Concepts Learned Today

### Memory injection
Memory is injected into the system prompt as plain text. The LLM reads it as context before the conversation starts. It uses the information naturally without announcing where it came from.

### Memory vs conversation priority
If memory says one thing and the user says something different in conversation, the LLM trusts the conversation. Recent explicit input overrides background context. Memory sets a baseline — conversation overrides it.

### Memory wording matters
`"user's email is X"` is a weak assertion — easy to override.
`"Always use this email for calendar: X"` is a stronger instruction.
The same fact written differently produces different agent behavior.

### When memory is loaded matters
`read_memory()` is called once at session start. Changes to the JSON file mid-session are not picked up until the next run.

---

## Key Questions Asked & What You Learned

**Q: Can RAG be used with memory later?**
Yes — and the memory structure is already designed for it. Each entry in `long_term.json` is a self-contained document with `id`, `category`, `content`, `created_at`. When memory grows large, you embed each `content` field and retrieve only relevant entries instead of loading everything. Migration = replace `load_all` with `embed + retrieve`. No restructuring needed.

**Q: Where should conversation history live — inside `run_agent` or `run_terminal`?**
In `run_terminal.py`. It owns the conversation — it's the one talking to the user. `run_agent` should just process one turn given the current history and return the updated list. One source of truth.

**Q: Should `system_prompt` be a variable or a function?**
A function when you need to inject dynamic content like memory. A plain variable works when it's static. Phase 1 = variable. Phase 2 = function that accepts `memory=""` parameter.

**Q: What is `json.dumps` vs `json.loads`?**
- `json.dumps(data)` — Python object → JSON string. Use when sending data somewhere (file, API, pipe).
- `json.loads(string)` — JSON string → Python object. Use when receiving data from somewhere.
`json.load(file)` already gives you a Python object — don't call `json.dumps` on it just to iterate.

**Q: Why does iterating over `json.dumps(data)` give characters?**
Because `json.dumps` converts your list to a string. Iterating over a string gives you characters one by one — `[`, `{`, `"`, `i`... not the entries you want. Always iterate over the Python list directly.

**Q: If memory says one thing and user says another, which wins?**
The conversation wins. Recent explicit input overrides background context. Memory is a baseline — not a hard constraint. This is also why memory wording matters — `"Always use this email"` is stronger than `"user's email is X"`.

**Q: Why does memory wording affect agent behavior?**
The LLM reads memory as text in the system prompt. How you phrase something changes how the LLM weights it against other context. `"user's email is X"` is a soft fact. `"Always use this email for calendar: X"` is an instruction. Instructions carry more weight than facts.

**Q: What does `if content:` check vs `if content is not ""`?**
`if content:` checks if the string is non-empty — the Pythonic way. `is not ""` checks object identity, not value equality. It can behave unexpectedly and is wrong for string comparison. Always use `if content:` for empty string checks.

---

## MCP — Mental Model Established (Phase 3 Prep)

**What you understood correctly:**
- MCP has a client and server
- Server exposes tools (e.g. Google Calendar functions)
- Client is the mediator between LLM and server
- Client fetches tool list, executes calls, passes results back to LLM

**Key correction — transport:**
MCP supports two transports:
- **stdio** — server runs as local process, client talks via stdin/stdout. Most common for local servers.
- **HTTP/SSE** — server runs remotely, client talks via HTTP.

For Google Calendar, you'll use a local MCP server running on your machine using **stdio** transport.

**Key insight:**
The client calls `tools/list` on the server first — this is how it discovers tools dynamically. No hardcoding. Connect a new server and the agent automatically knows its tools.

**Open question for tomorrow:**
Right now tool schemas are hardcoded in `agent.py`. In Phase 3 they should come from the MCP client dynamically via `tools/list`. This changes how `agent.py` gets its tool list.

---

## Experiment Results

**Test:** Added email to memory. Asked agent to book without providing email.
**Result:** Agent booked without asking. Recalled email correctly when asked directly.
**Insight:** Memory injection works. Agent absorbs it as natural context.

---

## What's Parked for Later

- **Phase 2b** — auto memory extraction after session. LLM reads conversation and extracts facts worth saving. Interesting experiment but not blocking Phase 3.

---

## Tomorrow — Resume Here

1. Phase 3 — MCP tool connection
   - Build custom `mcp/client.py` from scratch
   - Connect to Google Calendar MCP server (stdio transport)
   - Call `tools/list` to fetch tools dynamically
   - Replace hardcoded tool schemas in `agent.py` with dynamic ones from MCP client
   - Replace `mock_tools.py` execution with MCP client execution
   - Test end to end — real calendar booking

---

## Project Status

**Phase 1 — Complete**
**Phase 2a — Complete**
**Phase 2b — Parked**
**Phase 3 — Starting tomorrow**
