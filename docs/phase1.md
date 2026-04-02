# Phase 1 — ReAct Agent Loop
## Plain Python Terminal Agent (No Telegram, No MCP, No Memory)

---

## What Was Built

A working ReAct agent that runs in the terminal. You type a query, the agent thinks, calls tools if needed, observes the results, and gives a final response. No frameworks. Built from scratch.

**Task tested:** Book a calendar meeting — agent asks for email and time, calls mock tools, confirms booking.

---

## Files Created

```
ai/
├── agent.py          # The ReAct loop — heart of the project
├── llm.py            # Thin OpenAI wrapper
├── prompts.py        # System prompt with ReAct instructions
└── mock_tools.py     # Fake calendar functions

scripts/
└── run_terminal.py   # Entry point — takes user input, runs agent
```

---

## What Each File Does

### `ai/llm.py`
Single function `call_llm(messages, tools)`.
- Calls OpenAI GPT-4o mini
- Returns `response.choices[0].message` — the full message object
- Returns the full object (not just `.content`) because when the LLM wants to call a tool, `.content` is `None` and the tool info lives in `.tool_calls`
- Only place in the codebase that imports `openai` — swap models here only

### `ai/prompts.py`
Function `prompt()` that returns the system prompt string.
- Instructs the LLM to follow ReAct format: THINK → (tool call) → OBSERVE → RESPONSE
- Includes a concrete example — showing the LLM exactly what output format is expected
- Tells the LLM to call tools directly, not describe them in text
- Will become a function that accepts memory in Phase 2

### `ai/mock_tools.py`
Two fake functions that return hardcoded data:
- `fetch_calendar(user_email)` → returns `['9:30', '10:30', '17:30']`
- `book_slot(my_calendar, slot)` → returns `"Booking done"`

Why mock? To isolate the agent loop. In Phase 1 you're only learning how the loop works — not debugging MCP connections at the same time. Real tools come in Phase 3.

### `ai/agent.py`
The ReAct loop. Takes a message list, runs until the LLM gives a final text response.

**Flow:**
1. Call LLM with full message history + tool schemas
2. If `response.tool_calls` → get tool name → look up in `tool_map` → execute with `**json.loads(arguments)` → append assistant message + tool result to history → loop again
3. If no tool calls → return `(response, message)`

**Key details:**
- `tool_map` bridges tool name strings (`"fetch_calendar"`) to actual Python functions (`fetch_calendar`)
- `**json.loads(arguments)` unpacks the JSON string from OpenAI into keyword arguments for the function
- Assistant message must be appended as `message.append(response)` — not as a dict — because when tool_calls exist, `content` is `None` and OpenAI needs the full object with `tool_calls` field
- Returns both `response` and the updated `message` list so `run_terminal.py` can continue the conversation with correct history

### `scripts/run_terminal.py`
Entry point. Owns the conversation history.

**Flow:**
1. Add system prompt to history
2. Take user input → append to history
3. Call `run_agent(history)` → get response and updated history
4. Print response
5. Loop until user types "exit"

---

## How the Agent Loop Works (Plain English)

The LLM has no memory between API calls. Every time you call it, you send the full conversation from the beginning. The "memory" is just a Python list that grows with each turn.

When the LLM responds it can do one of two things:
1. **Ask for a tool** — returns a structured object with tool name and arguments. Your code executes the tool, adds the result to the list, and calls the LLM again.
2. **Give a final answer** — returns a text response. Loop ends.

This cycle — call LLM → execute tool → feed result back → repeat — is the agent loop. Everything else in the project is built around this.

---

## Message History Format

OpenAI requires messages in this exact format and order:

```python
[
    {"role": "system", "content": "...system prompt..."},
    {"role": "user", "content": "book a meeting with amit"},
    ChatCompletionMessage(role="assistant", tool_calls=[...]),   # full object, not dict
    {"role": "tool", "content": "['9:30']", "tool_call_id": "call_abc123"},
    ChatCompletionMessage(role="assistant", content="OBSERVE: slot available...RESPONSE: Done!")
]
```

**Rules:**
- Tool message must always follow an assistant message that has `tool_calls`
- `tool_call_id` links the result back to the specific tool call
- `content` in tool message must be a string — convert lists/dicts with `str()`

---

## Tool Schema Format

Each tool passed to OpenAI must follow this structure:

```python
{
    "type": "function",
    "function": {
        "name": "fetch_calendar",
        "description": "...",   # LLM reads this to decide when to call the tool
        "parameters": {
            "type": "object",
            "properties": {
                "user_email": {
                    "type": "string",
                    "description": "..."
                }
            },
            "required": ["user_email"]
        }
    }
}
```

The `description` field is critical — it is how the LLM decides which tool to call and when. Poor descriptions lead to wrong tool choices.

---

## What Went Wrong and Why

### Problem 1 — Agent describing tool calls instead of making them
The system prompt example showed `ACT: tool call()` as text. The LLM learned to write that in its response instead of actually triggering a tool call.

**Fix:** Remove fake ACT examples from the prompt. Add explicit instruction: "call tools directly, do not describe them in text."

**Lesson:** The LLM follows your prompt example literally. Show it exactly what you want — nothing more, nothing less.

### Problem 2 — Message history out of sync
`run_terminal.py` was maintaining its own history while `run_agent` was building a separate internal list. After tool calls, the two lists diverged and OpenAI got confused about message ordering.

**Fix:** `run_agent` returns both the response and the updated message list. `run_terminal.py` replaces its history with the returned list each turn.

**Lesson:** There should be one source of truth for conversation history. Decide who owns it and stick to it.

### Problem 3 — Appending assistant message as dict when tool calls exist
```python
message.append({"role": "assistant", "content": response.content})
```
When the LLM makes a tool call, `response.content` is `None`. OpenAI sees an assistant message with no `tool_calls` field, then sees a tool message, and throws an error.

**Fix:** `message.append(response)` — append the full object. OpenAI accepts it directly.

**Lesson:** When in doubt, pass the full object back. Don't manually reconstruct what OpenAI already gave you.

---

## Hardest Parts (Personal Notes)

1. **The agent loop + tool connection** — understanding that the LLM doesn't execute tools, your code does. The LLM just says "I want to call X." You execute X and feed the result back.

2. **Conversation history format** — every message must be in the right format, in the right order, with the right role. One wrong message type breaks the whole chain.

---

## What's NOT in Phase 1

- No memory — the agent forgets everything when you restart
- No real tools — mock functions return hardcoded data
- No Telegram — terminal only
- No confirmation before actions — agent books directly
- No logging or metrics

All of these come in later phases.

---

## Phase 2 Preview — Memory

Next phase adds two types of memory:
- **Short term** — conversation history within a session (already working, just not persisted)
- **Long term** — preferences and learned facts that survive across sessions, injected into the system prompt

The `prompt()` function in `prompts.py` will become `prompt(memory)` — accepting memory as input and injecting it into the system prompt. This is where you'll start to see how context affects the LLM's reasoning.
