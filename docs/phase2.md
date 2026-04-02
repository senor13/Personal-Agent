# Phase 2 — Memory
## Adding Short Term and Long Term Memory to the Agent

---

## What Was Built

Memory system for the agent. The agent can now remember things about the user across sessions. Built in two parts — Phase 2a (manual memory) is complete. Phase 2b (auto extraction) is next.

---

## Phase 2a — Manual Memory

### What it does
- User explicitly tells the agent what to remember at the end of each session
- Memory is saved to `memory/long_term.json`
- At the start of each session, memory is loaded and injected into the system prompt
- The agent uses this context naturally without being told where it came from

### Files Created / Modified

```
ai/
└── memory.py              # New — read and write memory files

memory/
└── long_term.json         # New — persistent memory storage

scripts/
└── run_terminal.py        # Updated — loads memory, saves memory after session

ai/
└── prompts.py             # Updated — prompt() now accepts memory parameter
```

---

## How Memory Works

### The flow

```
Session starts
→ read_memory() loads long_term.json
→ returns plain text string of all memory entries
→ prompt(memory) injects it into system prompt
→ agent starts conversation already knowing the context

Session ends
→ user asked if they want to save anything
→ if yes → add_memory(category, content) appends to long_term.json
→ next session picks it up
```

### Memory file structure

Each entry in `long_term.json` is a self-contained document:

```json
[
    {
        "id": "mem_001",
        "category": "about the user",
        "content": "user's email address is sagrika1323@gmail.com",
        "created_at": "2026-03-24T10:00:00Z"
    }
]
```

Why this structure:
- Each entry is independent — can be read, deleted, or updated without affecting others
- `category` enables filtering later (load only relevant categories)
- `content` is what gets injected into the prompt — and later embedded for RAG
- `created_at` helps with debugging and ordering

### How memory gets injected into the prompt

`prompts.py` accepts memory as a parameter:

```python
def prompt(memory=""):
    system_prompt = """..."""
    return system_prompt + f"\n\nWhat you know about the user:\n{memory}"
```

`run_terminal.py` connects them:

```python
memory = read_memory()
conversation_history.append({"role": "system", "content": prompt(memory)})
```

Memory becomes part of the system prompt — the LLM reads it as background context before the conversation starts.

---

## Key Concepts

### Memory vs conversation priority
If memory says one thing and the user says something different in the conversation, the LLM trusts the conversation. Recent explicit input overrides background context.

- Memory = baseline defaults
- Conversation = ground truth

### Memory wording is prompt engineering
The same fact written differently produces different agent behavior:

| Wording | Agent behavior |
|---|---|
| `"user's email is X"` | Weak — easy to override if user provides different email |
| `"Always use this email for calendar: X"` | Stronger — agent resists override |

Experiment with this to build intuition about how context affects LLM reasoning.

### Memory is loaded once at session start
`read_memory()` is called once when `run_terminal.py` starts. Changes to the JSON file mid-session are not picked up until the next run. Memory is a session-start snapshot.

---

## `ai/memory.py` — Full Reference

### `add_memory(category, content)`
- Takes a category string and content string
- Loads existing `memory/long_term.json` (or starts fresh if it doesn't exist)
- Appends new entry with auto-generated id and timestamp
- Saves back to file
- No return value

### `read_memory()`
- Reads `memory/long_term.json`
- Builds a plain string from all `content` fields
- Returns the string for injection into the system prompt
- Returns `""` if file doesn't exist

---

## What Was Learned

### Experiment run
Added `"user's email address is sagrika1323@gmail.com"` to memory. Asked agent to book a meeting without providing email.

**Result:** Agent booked without asking for email. Confirmed it had the email when challenged. Recalled it correctly when asked directly.

**Insight:** Memory injection works. The agent absorbs it as natural context — it doesn't announce the source, it just knows.

---

## Common Mistakes Made

### Iterating over a JSON string instead of a Python list
Called `json.dumps(data)` then tried to iterate — which iterates over characters.
`json.load()` already returns a Python object. Iterate directly over it.

### File path inconsistency
Checked existence with one path, read/wrote with another. Always use the same path string in all three places.

### `is not ""` for string comparison
Wrong in Python. Use `if content:` to check for non-empty string.

### `break` outside a loop
`break` only works inside loops. Use `return ""` when a function has nothing to return.

---

## Phase 2b — Auto Memory Extraction ✅ Complete

Instead of the user manually deciding what to save, the agent automatically extracts facts worth remembering after each session using a second LLM call.

### How it works

Two triggers:
- `/remember` — user explicitly triggers extraction mid-session
- `/stop` — automatically triggers extraction when stopping the agent

Both call `extract_memory(conversation_history)` in `ai/memory.py`.

### `extract_memory(conversation_history)`

1. Filters out system messages from `conversation_history` (to avoid re-saving old memory that was injected into the system prompt)
2. Appends an extraction prompt asking the LLM to return a JSON list of facts
3. Makes a second LLM call — same model, completely different purpose
4. Parses the JSON response
5. Calls `add_memory(category, content)` for each fact

```python
for_memory = [item for item in conversation_history if item["role"] != "system"]
message = for_memory + [{"role": "user", "content": prompt}]
response = call_llm(messages=message, tools=None)
facts = json.loads(response.content)
for mem in facts:
    add_memory(mem["category"], mem["content"])
```

### Extraction prompt design

Key instructions in the prompt:
- Only extract clear, specific facts worth remembering long term
- Ignore small talk and questions
- Return only raw JSON, no markdown, no code fences
- Example format uses obviously fake values so LLM doesn't save the example itself

### Problems encountered and fixed

**LLM wrapping response in markdown fences** — `json.loads()` crashed on ` ```json\n[]\n``` `. Fixed by adding "Return only raw JSON, no markdown, no code fences" to the prompt.

**Old memories being re-saved** — system prompt contains previous memories, which were in `conversation_history`, so LLM extracted them again. Fixed by filtering out `role == "system"` messages before passing to `extract_memory`.

**Example fact being saved** — extraction prompt included a realistic example (`"User's name is Sagrika"`) which the LLM saved as a real fact. Fixed by using obviously fake placeholder values in the example.

### Key insight

This is a second LLM call with a completely different job. The ReAct loop LLM call reasons and acts. The extraction LLM call reads and summarizes. Same model, same `call_llm` wrapper — just a different prompt and purpose. This pattern (multiple LLM calls with different roles in one pipeline) is common in production AI systems.

---

## What's NOT in Phase 2

- No RAG — all memory loaded in full every session (RAG comes in Phase 6)
- No memory deletion via agent — edit the JSON file manually
- No scratchpad — short term task notes come in Phase 4
- No tool call log — comes later

---

## Phase 3 Preview — MCP Tools

Next phase replaces mock tools with real MCP servers. Google Calendar first, then Spotify.

The agent loop in `agent.py` does not change. The only thing that changes is where tool execution happens — instead of calling `mock_tools.py` functions, the `tool_map` routes calls through the MCP client.

This is why building the loop correctly in Phase 1 mattered — Phase 3 is just swapping the tool execution layer.
