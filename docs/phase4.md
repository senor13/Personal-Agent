# Phase 4 — Telegram Bot

---

## What Was Built

Wrapped the working terminal agent in a Telegram polling bot. The agent now runs as a persistent bot you can message from your phone.

---

## Files Created / Modified

| File | What changed |
|---|---|
| `AI/telegram/telegram_bot.py` | Telegram handler, user ID lock, command handlers, main() |
| `AI/telegram/run_bot.py` | Module-level setup, process_message(), stop_flag |
| `AI/agent.py` | Added stop_flag parameter to run_agent() |

---

## How It Works

```
User sends Telegram message
→ handle_message() checks user ID
→ if unauthorized → reply "Unauthorized." and stop
→ if authorized → call run_bot.process_message()
→ run_agent() runs ReAct loop
→ reply with response
```

### User ID Lock
`ALLOWED_USER_ID` in `.env`. Check happens before any LLM call — unauthorized users never reach the agent.

### Module-level Setup
`run_bot.py` runs setup code once at import time:
```python
process1, process2 = connect_server()   # connect MCP servers once
conversation_history = []               # initialize per-session history
stop_flag = [False]                     # mutable flag for /stop
memory = read_memory()
conversation_history.append({"role": "system", "content": prompt(memory)})
```

### Conversation History
Global list in `run_bot.py`. Persists across messages within a session. Reset only when bot restarts.

---

## Commands

### `/stop`
- Sets `stop_flag[0] = True`
- Triggers `extract_memory` to save anything worth keeping
- Replies "Stopping."
- Agent loop checks flag at top of each iteration — exits with `None` if set

### `/remember`
- Triggers `extract_memory(conversation_history)`
- LLM extracts facts worth saving from current session
- Saves to `long_term.json`
- Replies "Memories saved."

---

## Key Concepts Learned

### Polling vs Webhook
Polling: bot asks Telegram "any new messages?" every few seconds. Simple, no infrastructure needed. Good for development.
Webhook: Telegram pushes messages to your server when they arrive. Requires a public URL and server. Production approach (Phase 10).

### async/await
Telegram handlers must be `async def`. `await` pauses execution until the async call completes without blocking the event loop. Python runs other tasks while waiting.

### Mutable list as flag
Plain boolean can't be passed by reference. `stop_flag = [False]` is a list — passed by reference so `stop_flag[0] = True` in the handler is seen by the agent loop.

### `conversation_history[:] = updated_history`
Updates the list in-place. Plain `=` inside an async function makes Python treat it as a local variable → `UnboundLocalError`. `[:]` avoids the assignment entirely.

### Module-level code runs at import time
Every line outside a function runs when the file is imported. `connect_server()` at module level = connects once at startup. Disconnect/cleanup code at module level would run immediately — wrong place for shutdown logic.

---

## Common Mistakes Made

### `from telegram import update` (lowercase)
Type hint used `Update` (capital) — crash on import. Always capital `U`.

### `if __name__` indented inside `main()`
Python thought it was inside the function. Must be at column 0.

### `disconnect_server` at module level
Ran immediately at import, killed MCP connections before bot started. Removed entirely — OS handles cleanup on process exit.

### `conversation_history = updated_history` inside async function
Python treats as local variable → `UnboundLocalError`. Fix: `conversation_history[:] = updated_history`.
