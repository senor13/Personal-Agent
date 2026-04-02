# Daily Tracker — 2026-03-23 — Project Planning & Phase 1 Implementation (Agent Loop)

## Quick Summary
- Planned the full project in `CLAUDE.md` — architecture, phases, memory, RAG, evals, observability
- Started Phase 1 implementation — built 4 out of 5 files
- Only `scripts/run_terminal.py` remaining to complete Phase 1
- Session ended early — resume tomorrow with run_terminal.py then test the full loop

---

## Files Created Today

| File | Status | What it does |
|---|---|---|
| `CLAUDE.md` | Done | Full project blueprint — architecture, phases, experiments map |
| `CLAUDE.docx` | Done | Word version of CLAUDE.md for offline reference |
| `ai/llm.py` | Done | Thin OpenAI wrapper — takes messages + tools, returns response message |
| `ai/prompts.py` | Done | System prompt with ReAct format and example |
| `ai/mock_tools.py` | Done | Fake calendar functions — `fetch_calendar`, `book_slot` |
| `ai/agent.py` | Done | ReAct loop — calls LLM, handles tool calls, feeds results back |
| `scripts/run_terminal.py` | **TODO** | Entry point — takes user input, calls run_agent, prints response |

---

## What You Built and Why

### `ai/llm.py`
Single function `call_llm(messages, tools)` that calls OpenAI and returns `response.choices[0].message`.
Returns the full message object — not just `.content` — because when the LLM wants to call a tool, `.content` is `None` and the tool call info lives in `.tool_calls`.

### `ai/prompts.py`
System prompt as a plain string for now. Will become a function in Phase 2 when memory needs to be injected dynamically.
Key elements: ReAct instruction, concrete example showing THINK → ACT → OBSERVE → RESPONSE, "don't assume, ask the user."

### `ai/mock_tools.py`
Two functions with hardcoded fake responses:
- `fetch_calendar(user_email)` → returns `['9:30', '10:30', '17:30']`
- `book_slot(my_calendar, slot)` → returns `"Booking done"`

Mock tools exist so Phase 1 can focus purely on the agent loop without debugging MCP connections at the same time.

### `ai/agent.py`
The ReAct loop. Key flow:
1. Build message list: system prompt + user query
2. Call LLM
3. If `response.tool_calls` → get tool name, look up in `tool_map`, execute with `**json.loads(arguments)`, append assistant message + tool result to history, loop again
4. If no tool calls → return response (final answer)

Important details learned:
- Tool results use `role: "tool"` with a `tool_call_id` linking back to the assistant message
- The assistant message must be appended to history BEFORE the tool result
- `**json.loads(arguments)` unpacks the JSON string into keyword arguments for the function
- `tool_map` is a dict mapping tool name strings to actual Python functions — this is how you go from `"fetch_calendar"` (string) to `fetch_calendar()` (callable)

---

## Key Concepts Learned Today

### The agent loop
Just a `while True` loop. LLM is stateless — you maintain the message list and send it in full every iteration. "Memory" at this level is just the message list growing with each turn.

### Two types of LLM responses
1. `tool_calls` is not None → LLM wants to call a tool
2. `content` is not None → LLM has a final answer

### Tool calling mechanics
OpenAI doesn't execute tools. It returns a structured object saying "I want to call X with these args." Your code executes it and feeds the result back. This is true in all frameworks — LangChain, LangGraph etc. all do the same thing under the hood.

### Tool schema
Each tool needs `type: "function"` wrapper + `function: { name, description, parameters }`. The description is critical — it's how the LLM decides which tool to call. Bad descriptions = wrong tool choices.

### Message roles
- `system` — instructions to the LLM
- `user` — your input
- `assistant` — LLM response (text or tool call request)
- `tool` — result of a tool execution

---

## Key Questions Asked & What You Learned

**Q: Why use mock tools in Phase 1 instead of real ones?**
To isolate the variable you're learning. Phase 1 is only about the agent loop. If you're also debugging MCP connections at the same time, you won't know which thing is broken. Mock tools let you control the environment completely and focus on whether the agent reasons correctly.

**Q: Why return the full message object from `call_llm` instead of just `.content`?**
Because when the LLM wants to call a tool, `.content` is `None`. The tool call information lives in `.tool_calls`. If you only return `.content` you'll never be able to detect tool calls.

**Q: What are the four message roles and what does each mean?**
- `system` — instructions to the LLM (the prompt)
- `user` — your input
- `assistant` — LLM response (text or tool call request)
- `tool` — result of a tool execution

**Q: Why does `tool_map` exist? Why not just call the tool directly?**
Because when the LLM says "call fetch_calendar", it gives you a string — not a callable function. `tool_map` is a dict that maps the string `"fetch_calendar"` to the actual Python function `fetch_calendar`. You look up the string, get the function, call it.

**Q: Why does `llm.py` need to be its own file?**
Single responsibility. If you want to switch from GPT-4o mini to Claude, you change one file and nothing else breaks. If the LLM call was mixed into `agent.py`, you'd have to hunt for it.

**Q: What does `print()` return?**
`None`. This is why `return print("Booking done")` is wrong — the agent loop needs a return value to feed back to the LLM. Always `return` the value, don't just print it.

**Q: What is `**json.loads(arguments)`?**
`json.loads()` converts a JSON string like `'{"user_email": "test@gmail.com"}'` to a Python dict `{"user_email": "test@gmail.com"}`. The `**` unpacks that dict into keyword arguments so `fetch_calendar(**{"user_email": "x"})` becomes `fetch_calendar(user_email="x")`.

---

## Feedback and Things to Remember

- **Be intentional with f-strings** — only use `f"""` if you're actually interpolating variables
- **Single responsibility** — `llm.py` only makes the API call, nothing else. Don't mix concerns.
- **Return values matter** — `print()` returns `None`. If a function's output needs to be used by the agent, it must `return` something.
- **Python is case sensitive** — `fetch_Calendar` vs `fetch_calendar` will break imports silently
- **Don't change two things at once** — when debugging the agent loop, change one variable at a time and observe the effect
- **`tools` in `agent.py` is the schema list** — it is not the same as your mock functions. `tool_map` is the bridge between the two.

---

## Tomorrow — Resume Here

1. Write `scripts/run_terminal.py` — ask for input, call `run_agent(query)`, print `response.content`
2. Create a `.env` file with `OPENAI_API_KEY`
3. Run the full loop and test with: *"Can you book a 30 min meeting with John tomorrow at 9:30am?"*
4. Observe the THINK / ACT / OBSERVE output in terminal
5. If something breaks — check which layer it's in (LLM call? tool execution? message history?)

---

## Project Status

**Phase 1 — ~90% done**
One file remaining. Once `run_terminal.py` is written and tested, Phase 1 is complete.

**Phase 2 next** — memory. Short term conversation history + long term preferences loaded into system prompt.
