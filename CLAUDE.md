# Personal AI Assistant — CLAUDE.md

## What This Project Is

A personal Telegram AI assistant built to **learn AI engineering**, not to ship a product.
The learning goals are: how agents think, how memory affects reasoning, how prompts shape behavior, how tool descriptions influence decisions, and how the ReAct loop produces coherent multi-step behavior.

The software engineering side is kept deliberately simple so it does not get in the way.

---

## Primary Goal Reminder

> The assistant is the vehicle. The learning is the outcome.

When making decisions about complexity, always ask: does this help understand the AI part better? If not, keep it simple.

---

## Tech Stack

| Component | Choice | Reason |
|---|---|---|
| LLM | OpenAI GPT-4o mini | Fast, cheap, good tool-use support |
| Telegram | `python-telegram-bot` (polling first) | Simple to start, no infra needed |
| Backend | `FastAPI` | Minimal, async, only added in Phase 6 |
| MCP | Custom `MCPClient` class (no SDK) | Learn tool calling at a low level |
| Memory | Files (JSON / Markdown) | Simple, inspectable, RAG-ready structure |
| Agent framework | None — built from scratch | The whole point is to understand how it works |

**Do not use LangChain, LangGraph, or any agent framework.** Build the loop, memory, and tool calling manually.

LLM provider abstraction: keep LLM calls behind a thin wrapper so switching to Claude or Gemini later only requires changing that wrapper, nothing else.

---

## Project Structure

```
Personal-Agent/
├── CLAUDE.md
├── idea.md
│
├── ai/                          ← ALL AI logic lives here (main focus)
│   ├── agent.py                 # ReAct loop — the core of the project
│   ├── llm.py                   # Thin LLM wrapper (swap models here only)
│   ├── prompts.py               # System prompt and ReAct formatting
│   ├── memory.py                # Load/save all memory types
│   ├── guard.py                 # Prompt injection stripping
│   ├── tools_log.py             # Timestamped tool call logger
│   └── metrics.py               # Latency, token, and cost tracking per turn
│
├── mcp/
│   └── client.py                # Custom MCP client (connect, list tools, execute)
│
├── bot/
│   ├── telegram_bot.py          # Telegram handler, message formatting, buttons
│   └── confirmation.py          # YES/NO confirmation flow for write actions
│
├── server/
│   └── main.py                  # FastAPI webhook (Phase 6 only)
│
├── memory/
│   ├── preferences.md           # Explicit user preferences (always loaded in full)
│   ├── long_term.json           # Cross-session learned context — RAG-ready structure
│   ├── scratchpad.json          # Current task working notes (short-term, cleared on done)
│   └── tool_calls.log           # Audit log of every tool call
│
├── rag/                         # Added in Phase 6 — do not create before then
│   ├── embedder.py              # Embed long_term.json entries using OpenAI embeddings
│   ├── retriever.py             # Query vector store, return top-K relevant memories
│   └── vector_store/            # ChromaDB or FAISS local index (gitignored)
│
├── evals/
│   ├── cases/                   # Fixed test cases (JSON) with input + expected outcome
│   ├── run_evals.py             # Run all eval cases, score results, write report
│   └── results/                 # Eval run outputs (gitignored)
│
├── logs/
│   └── metrics.jsonl            # One JSON object per turn — latency, tokens, cost, steps
│
├── scripts/
│   └── run_terminal.py          # Phase 1 — run agent from terminal, no Telegram
│
├── .env
├── .env.example
└── docs/
    └── architecture.md          # Written last — full walkthrough with design decisions
```

---

## Development Phases

Build in order. Do not move to the next phase until the current one is working and understood.

### Phase 1 — ReAct Loop in Terminal
Run from a plain Python script. No Telegram, no FastAPI, no MCP.
- Hardcode a test task (e.g. "create a meditation playlist")
- Implement the agent loop: call LLM → parse response → handle tool calls → feed result back → repeat
- Print THINK / ACT / OBSERVE to the terminal
- Use mock tool functions that return fake data
- **Learning goal:** understand the agent loop and ReAct output format

### Phase 2 — Memory
Still terminal only. Add memory on top of Phase 1.
- Load preferences and long-term memory into the system prompt at session start
- Save new learned facts to long-term memory after the session
- Use task scratchpad during the loop, clear it when done
- Experiment: how does adding/removing memory change the agent's responses?
- **Learning goal:** understand how context and memory shape LLM reasoning

### Phase 3 — MCP Tool Connection
Replace mock tools with real MCP servers.
- Build the custom `MCPClient` in `mcp/client.py`
- Connect Google Calendar MCP server first
- Connect Spotify MCP server second
- Experiment: how does changing tool descriptions change which tools the agent picks?
- **Learning goal:** understand tool calling mechanics and tool description engineering

### Phase 4 — Telegram Bot
Wrap the working agent in a Telegram polling bot.
- Show THINK / ACT / OBSERVE as individual Telegram messages as they happen
- Add YES/NO inline buttons before any write action
- Add `/stop` emergency command to halt the agent
- User ID lock — reject all messages from non-allowed users before any LLM call
- **Learning goal:** understand how to surface agent reasoning in a real interface

### Phase 5 — Experiment and Expand
Agent is working end-to-end. Now experiment.
- **Tool description experiment** — reword a tool description (vague → specific), run the same task, observe if agent behavior changes. Key question: how much does wording control tool selection?
- **Few-shot prompting** — add one example ReAct trace to system prompt, measure if reasoning quality improves
- **Add new tools** — one at a time (news, research papers). Each new tool = new MCP server + description, zero changes to `agent.py`
- **Learning goal:** validate that prompts and tool descriptions are the control surface, not code

### Phase 6 — RAG
Two-part RAG implementation: memory retrieval + YouTube knowledge base.

#### Phase 6a — Memory RAG
Long-term memory has grown large enough that loading everything every time wastes context. Replace "load all" with "retrieve relevant."
- Embed all existing `long_term.json` entries using OpenAI `text-embedding-3-small`
- Store vectors locally using **ChromaDB** (file-based, no server) or **FAISS**
- Replace full memory load in `ai/memory.py` with `retrieve_relevant_memories(query, top_k=5)`
- Query = current user message. Retrieve only the top-K most semantically relevant entries
- Preferences file is still always loaded in full — it is small and always relevant
- **Learning goal:** understand how embedding quality, top-K value, and entry wording affect retrieval
- **Experiment:** run same task with full memory load vs. RAG — compare what agent knows and how it reasons

#### Phase 6b — YouTube RAG
Build a personal video knowledge base from channels you follow. See YouTube RAG section below for full design.
- **Learning goal:** chunking strategy, metadata filtering, source attribution, cross-source retrieval

Progression of memory strategies:

| Strategy | How it works | What you learn |
|---|---|---|
| Phase 2 | Load all memories into prompt | Baseline — context bloat at scale |
| Phase 6a | Semantic RAG (embeddings) | How does similarity retrieval change reasoning quality? |
| Phase 6b | YouTube transcripts + memory in one store | Does mixing sources improve or confuse retrieval? |

### Phase 7 — Observability and Metrics
Instrument the agent to measure what's actually happening per turn.
- Build `ai/metrics.py` — captures latency, token counts, cost per turn, tool call latency, steps to completion
- Write to `logs/metrics.jsonl` — one JSON object per agent turn
- Track: total latency, tokens per turn, cost per task, steps to completion, memory entries loaded
- **Learning goal:** understand the real cost and performance profile of your agent. Which step is slowest? Does more memory = better reasoning? How much does one calendar booking cost?

### Phase 8 — Evaluation Framework
Measure how well the agent performs, not just how fast.
- Build `evals/` with fixed test cases in JSON format
- `run_evals.py` runs all cases and scores results
- Dimensions: task success (boolean), tool selection accuracy, reasoning quality (LLM-as-judge), memory relevance
- Run evals before/after any significant prompt or tool description change
- **Learning goal:** understand the difference between "agent ran" and "agent did well." Use evals to validate that prompt changes actually improve behavior.

### Phase 9 — Guardrails
Harden the agent against misuse and failures.
- Max tool calls per turn (10) — stop loop and alert if exceeded
- MCP call timeout (30s) — don't hang forever on a broken server
- Prompt injection guard (`ai/guard.py`) — strip instruction-like patterns from external content before passing to LLM
- Sensitive data redaction in logs — strip phone numbers, email addresses from `metrics.jsonl`
- Rate limiting on Telegram handler
- **Learning goal:** understand failure modes of production agents and how guardrails prevent them

### Phase 10 — Production
Only after all learning is done.
- Switch Telegram from polling to webhook
- Add FastAPI server (`server/main.py`)
- Deploy to a VPS (DigitalOcean or similar) — bot runs 24/7
- Final architecture review and `docs/architecture.md`

---

## ReAct Loop Format (MANDATORY)

Every agent response must follow this structure. Every step must be shown on Telegram (or terminal in early phases) as it happens — not batched at the end.

```
THINK: [reasoning about what to do next and why]

ACT: tool_name(param1=value1, param2=value2)
OBSERVE: [what the result means, what to do next]

ACT: next_tool(...)
OBSERVE: [updated understanding]

→ [final human-readable response to the user]
```

No silent tool calls. No skipping steps. Every cycle must be visible.

---

## Confirmation Gate (MANDATORY for write actions)

Before any tool that **creates, modifies, deletes, sends, books, or posts**, the agent must:
1. State what it is about to do
2. Show YES / NO inline buttons
3. Wait for user response
4. Only proceed on YES — on NO, stop and explain

Write actions: `create_playlist`, `add_tracks`, `book_meeting`, `send_message`, `delete_event`, `post_*`, anything that changes state in the real world.

---

## Memory Design

Four memory types:

| File | Type | Content | Cleared when |
|---|---|---|---|
| `memory/preferences.md` | Long-term | Explicit rules the user stated (e.g. "never before 7am") | Never |
| `memory/long_term.json` | Long-term | Things learned about the user over time | Manually |
| `memory/scratchpad.json` | Short-term | Working notes for the current task only | Task completes |
| `memory/tool_calls.log` | Audit | Every tool call with timestamp, params, result, confirmed/cancelled | Never |

### Long-term memory structure (RAG-ready from day one)

Write entries as **self-contained, specific, embeddable documents.** Each entry must make sense on its own without surrounding context — this is what makes retrieval work well later.

```json
{
  "id": "mem_001",
  "category": "people",
  "content": "John is my research collaborator at UCL working on NLP",
  "tags": ["john", "people", "ucl", "research"],
  "created_at": "2026-03-23T10:00:00Z",
  "last_accessed": "2026-03-23T10:00:00Z"
}
```

**Categories** (use exactly these — consistent categories make keyword filtering and RAG equally easy):
- `people` — who someone is and their relationship to you
- `schedule` — recurring patterns, availability constraints, preferences around time
- `preferences` — tastes, styles, things you like or dislike (music, meeting length, etc.)
- `context` — ongoing projects, goals, things the agent has learned about your life

**Rules for writing good memory entries:**
- Be specific, not vague. `"John is my research collaborator at UCL working on NLP"` embeds far better than `"John - important"`.
- One fact per entry. Don't combine multiple unrelated facts.
- Include names, places, and topics — these become natural retrieval anchors.
- Use `tags` to mirror the key nouns in `content` — helpful for keyword-based retrieval in early phases.

**Why this structure matters:**
- Phase 2: Load all entries — works fine when memory is small.
- Phase 6 (RAG): Each `content` field becomes the text to embed. Each entry is a retrieval document. Migration = embed all entries + replace `load_all` with `retrieve_relevant`. No restructuring needed.

At session start:
- Always load `preferences.md` in full (small, always relevant)
- Phase 2–5: Load all `long_term.json` entries
- Phase 6+: Embed the current user message and retrieve top-K entries by cosine similarity

---

## Prompt Injection Guard

Before any external content (calendar event titles, Spotify track names, search results, email subjects) is passed to the LLM, strip instruction-like patterns.

Patterns to strip (case-insensitive): `ignore previous`, `system:`, `<instructions>`, `forget`, `act as`, `you are now`, `disregard`, `new task:`

Implemented in `ai/guard.py`. Called on all external content before it enters any prompt.

---

## Safety Guardrails

- **User lock:** `ALLOWED_USER_ID` in `.env`. Reject at the handler level — no LLM call made for other users.
- **Emergency stop:** `/stop` Telegram command immediately halts the current agent loop.
- **Max tool calls per turn:** 10. If exceeded, stop and tell the user something went wrong.
- **MCP call timeout:** 30 seconds per tool call.
- **Confirmation before writes:** See Confirmation Gate above.
- **No secrets in code:** All API keys via `.env`. Validate at startup and fail fast.
- **Prompt injection guard:** See above.

Future guardrails (Phase 6):
- Max token budget per turn
- Sensitive data redaction in logs (phone numbers, email addresses)
- Rate limiting on the Telegram handler

---

## MCP Client Design

`mcp/client.py` must implement from scratch:
1. Connect to an MCP server (stdio or HTTP transport)
2. Call `tools/list` to fetch available tools dynamically
3. Execute tool calls by routing `tool_name + args` to the correct server
4. Return structured results to the agent loop

Adding a new MCP server should require zero changes to `ai/agent.py`. The client handles routing transparently.

---

## LLM Wrapper Design

`ai/llm.py` is a thin wrapper around the OpenAI client. It must:
- Accept messages, tools, and system prompt as inputs
- Return the raw LLM response
- Be the only place in the codebase that imports `openai`

Switching to Claude or Gemini = rewrite only this file.

---

## Coding Guidelines

- `ai/` is the priority. Write clear docstrings explaining **what** and **why**, not just what.
- Keep `ai/agent.py` under 300 lines. Extract helpers if it grows.
- ReAct formatting is the agent's responsibility — not the bot layer's.
- The bot layer only sends strings. No business logic in `telegram_bot.py`.
- No global mutable state. Pass context explicitly.
- All external calls (LLM, MCP, Telegram) must be async.
- No hardcoded values — use `.env` or constants.

---

## Environment Variables

```bash
# .env.example
OPENAI_API_KEY=
TELEGRAM_BOT_TOKEN=
ALLOWED_USER_ID=          # Your Telegram numeric user ID
GOOGLE_CALENDAR_MCP_PATH= # Path or URL to Google Calendar MCP server
SPOTIFY_MCP_PATH=         # Path or URL to Spotify MCP server
WEBHOOK_URL=              # Only needed in Phase 6
```

---

## Documentation

`docs/architecture.md` is written **last**, after all phases are working. It must cover:
1. What the project does end-to-end
2. Why each technology was chosen and what alternatives were considered
3. How the ReAct loop works in this specific codebase
4. How memory is structured, why entries are written the way they are, and how RAG migration works
5. How tool descriptions affect agent behavior (with examples from experiments)
6. How to add a new MCP server / capability

---

## Observability — Latency and Cost Tracking

Every LLM call already returns token counts in the API response. Capture them. Every tool call has a wall-clock duration. Measure it. Write it all to `logs/metrics.jsonl` — one JSON object per agent turn.

### What to measure per turn

```json
{
  "turn_id": "uuid",
  "timestamp": "2026-03-23T10:00:00Z",
  "user_message": "create a 30 min meditation playlist",
  "task_success": true,
  "total_latency_ms": 4200,
  "react_steps": 4,
  "llm_calls": [
    {
      "step": 1,
      "latency_ms": 980,
      "input_tokens": 412,
      "output_tokens": 87,
      "cost_usd": 0.000114
    }
  ],
  "tool_calls": [
    {
      "tool": "search_tracks",
      "latency_ms": 320,
      "success": true
    }
  ],
  "total_input_tokens": 1240,
  "total_output_tokens": 310,
  "total_cost_usd": 0.000372,
  "memory_entries_loaded": 6
}
```

### Where to implement this

`ai/metrics.py` wraps the agent turn and collects all of this:
- Start a turn timer when the user message arrives
- After each LLM call: read `usage.prompt_tokens` and `usage.completion_tokens` from the OpenAI response
- After each tool call: record latency and success/failure
- On turn end: write the full record to `logs/metrics.jsonl`

### GPT-4o mini pricing (as of 2026)

| Token type | Price |
|---|---|
| Input | $0.15 / 1M tokens |
| Output | $0.60 / 1M tokens |

`cost_usd = (input_tokens * 0.00000015) + (output_tokens * 0.0000006)`

Store the formula as a constant in `ai/metrics.py` — update it if you switch models.

### Things to watch in the metrics

- **Total latency per turn** — is the agent slow? Which step takes the longest?
- **Tokens per turn** — is the system prompt or memory too large?
- **Steps to completion** — is the agent taking more tool calls than needed? (sign of poor tool descriptions or prompt)
- **Cost per task** — how much does booking one meeting cost? creating a playlist?
- **Memory entries loaded** — does loading more context correlate with better or worse task success?

---

## Agent Evaluation

Measuring tokens and latency tells you *how* the agent ran. Evaluation tells you *how well* it did. These are different.

### Dimensions to evaluate

| Dimension | Question | How to measure |
|---|---|---|
| Task success | Did the task actually complete? | Boolean — check tool call log for the final write action |
| Efficiency | How many steps and tokens did it take? | From metrics log — compare across prompt versions |
| Tool selection | Did it pick the right tools in the right order? | Compare actual tool sequence vs. expected sequence in eval case |
| Reasoning quality | Was the THINK step coherent and accurate? | LLM-as-judge (see below) |
| Memory relevance | Did it recall the right context? | Check which memories were loaded vs. which were relevant |

### Eval case format

Store fixed test cases in `evals/cases/` as JSON:

```json
{
  "id": "eval_001",
  "description": "Book a 30-minute meeting with John next Tuesday",
  "user_message": "Book 30 mins with John next Tuesday morning",
  "expected_tool_sequence": ["check_availability", "create_event"],
  "expected_outcome": "calendar event created with Google Meet link",
  "expected_memories_used": ["john_is_collaborator", "no_meetings_before_7am"]
}
```

Start with 5–10 eval cases covering your two current tasks. Run them after any significant change to the prompt, memory structure, or tool descriptions.

### LLM-as-judge for reasoning quality

For each THINK step, make a separate LLM call asking:

```
Given the user's message and the agent's reasoning step below,
rate the quality of the reasoning on a scale of 1–5.
Consider: is it accurate? is it relevant? does it correctly identify what to do next?

User message: {user_message}
Agent THINK step: {think_text}

Score (1-5) and one sentence explanation:
```

Use GPT-4o (not mini) as the judge — you want the judge to be more capable than the agent being evaluated. Log scores to the eval results.

### When to run evals

- After any change to `ai/prompts.py` (system prompt)
- After changing tool descriptions
- After any change to memory loading logic
- When adding a new MCP server
- Before and after switching LLM models

### What evals tell you as experiments

This is the real value for learning:

| Change | Run evals before and after | What you learn |
|---|---|---|
| Reword a tool description | Did tool selection accuracy change? | How tool descriptions control agent decisions |
| Add more memory context | Did task success improve? Did token cost go up? | Memory vs. context trade-off |
| Switch to full load → RAG | Did reasoning quality stay the same with fewer tokens? | RAG retrieval quality |
| Change system prompt structure | Did THINK step quality scores change? | Prompt structure and reasoning |

---

## Learning Experiments Map

| Concept | Phase | Experiment | Question to answer |
|---|---|---|---|
| ReAct loop | 1 | Run same task with and without THINK steps in prompt | Does explicit reasoning improve tool selection? |
| Tool descriptions | 3 | Reword a tool description from vague to specific | How much does wording change which tool the agent picks? |
| Few-shot prompting | 3 | Add 1 example ReAct trace to system prompt | Does a worked example improve reasoning quality score? |
| Context window — sliding window | 2 | Keep only last 5 messages vs. full history | Does the agent lose important context? Where does it break? |
| Context window — summarization | 2 | Compress old turns into a rolling summary | Does summary quality affect task success vs. raw history? |
| Memory — full load | 2 | Load all long_term.json entries every turn | Baseline. What is the token cost? Does it all get used? |
| Memory — keyword filter | 2 | Filter entries by category before loading | Does reducing context hurt or help reasoning? |
| Memory — RAG | 6 | Embed entries, retrieve top-5 by similarity | Same task success with fewer tokens? |
| Embedding model | 6 | text-embedding-3-small vs 3-large | Does retrieval quality improve enough to justify 5x cost? |
| Retrieval strategy | 6 | top-K vs similarity threshold vs hybrid | Which surfaces the most relevant memories? |
| Model routing | 5 | Mini for tool selection, 4o for final answer | Does quality improve? What is the cost delta? |
| Prompt caching | 5 | Static system prompt with OpenAI prefix caching | How many tokens saved per turn on average? |
| Chunking | 5 | Fixed-size vs sentence-boundary chunks for paper summarizer | Does chunk boundary affect summary coherence? |
| LLM-as-judge | 2+ | Score THINK step quality after every prompt change | Does prompt change X actually improve reasoning? |
| Cost per task | 1+ | Track cost across all phases | How does cost change as the agent gets more capable? |
| YouTube RAG | 5 | Fetch transcripts from preferred channels, chunk + embed, retrieve on query | Can the agent answer "what did channel X say about topic Y?" from your personal video library? |
| YouTube channel curation | 5 | Define rules for which channels to follow, auto-fetch new video transcripts | Does rule-based channel selection produce a useful personal knowledge base? |
| Cross-source RAG | 6 | Combine YouTube transcripts + long_term memory + research papers in one vector store | Does mixing sources improve or confuse retrieval? How do you separate source types? |

---

## YouTube RAG — Detailed Design (Phase 5)

A personal video knowledge base built from channels you follow.

### How it works
1. **Channel list** — maintain a list of preferred YouTube channels in `memory/youtube_channels.json`
2. **Transcript ingestion** — periodically fetch new video transcripts via YouTube MCP server
3. **Chunking** — split transcripts into overlapping chunks (sentence-boundary, ~500 tokens)
4. **Embedding** — embed each chunk using `text-embedding-3-small`
5. **Storage** — store in ChromaDB with metadata: `video_id`, `channel`, `title`, `published_at`, `chunk_index`
6. **Retrieval** — when user asks about a topic, embed the query and retrieve top-K chunks
7. **Answer** — agent cites which video/channel the answer came from

### What you'll learn
- How chunking strategy affects retrieval quality
- How metadata filtering (filter by channel, filter by date) combines with semantic search
- How to attribute answers to sources
- Cost of embedding a large corpus vs. benefit of retrieval

### Rules for channel curation
Define in `memory/youtube_channels.json`:
```json
[
  {"channel_id": "UC...", "name": "3Blue1Brown", "topics": ["math", "AI"]},
  {"channel_id": "UC...", "name": "Andrej Karpathy", "topics": ["AI", "LLM"]}
]
```
New videos from these channels get auto-ingested when you run a sync command.

---

## What NOT to Do

- Do not use LangChain, LangGraph, or any agent framework
- Do not use the MCP SDK's built-in agent runner
- Do not add a database or Redis — files only for memory (ChromaDB/FAISS are file-based and allowed in Phase 6)
- Do not create the `rag/` folder before Phase 6 — build it only when memory is actually large enough to need it
- Do not add a frontend — Telegram is the UI
- Do not build Phase 6 infrastructure before Phase 5 is complete and understood
- Do not over-engineer the FastAPI layer — one webhook endpoint is enough
- Do not skip the terminal phase — Phase 1 is where the learning happens
