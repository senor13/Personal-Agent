# Daily Tracker — 2026-03-25 (Part 2) — Spotify & YouTube MCP Attempts + Architecture Extension

---

## Quick Summary
- Attempted Spotify MCP — blocked by Premium requirement
- Attempted `CaullenOmdahl/youtube-music-mcp-server` — too complex, needs PostgreSQL + Redis
- Attempted `zubeid-youtube-mcp-server` — broken dependency (`@modelcontextprotocol/sdk` missing)
- Settled on `instructa/mcp-youtube-music` — simple, works, proves architecture
- Successfully ran TWO MCP servers simultaneously — Google Calendar + YouTube
- Added YouTube RAG idea to CLAUDE.md experiments map
- Accidentally exposed API keys — rotated all of them

---

## What Was Proven Today

Two MCP servers running simultaneously. Tools from both merged into one list. Agent correctly routed tool calls to the right server. Architecture is extensible — zero changes to `agent.py`.

---

## Files Modified Today

| File | What changed |
|---|---|
| `AI/mcp/client.py` | `connect_server()` now spawns two processes, returns `(process1, process2)`. Added `load_dotenv()`, `time`, `os` imports |
| `ai/agent.py` | `run_agent(query, process1, process2)` — fetches tools from both servers, merges, routes tool calls via tool name lookup |
| `.env` | Added `YOUTUBE_API_KEY`, `GOOGLE_OAUTH_CREDENTIALS`. Rotated OpenAI + YouTube keys after accidental exposure |
| `CLAUDE.md` | Added YouTube RAG experiment to experiments map + full design section |

---

## Key Architecture Change — Two MCP Servers

### `connect_server()` now returns two processes
```python
return process1, process2
```

### `run_agent()` fetches and merges tools from both
```python
tool1 = fetch_tools(process1)   # Google Calendar tools
tool2 = fetch_tools(process2)   # YouTube tools
tools = tool1 + tool2           # one flat list for LLM
```

### Tool routing via name lookup
```python
if tool_name in [tool["function"]["name"] for tool in tool1]:
    execute_tools(process1, tool_name, arguments)
else:
    execute_tools(process2, tool_name, arguments)
```

The LLM sees one flat list. It picks the tool. Your code figures out which server to call.

---

## Key Questions Asked & What You Learned

**Q: Why does `time.sleep(3)` help after spawning a subprocess?**
Some servers take a few seconds to start up before they're ready to receive requests. `process.wait()` won't work — it waits for the process to finish, which never happens for a running server. `sleep` gives it time to initialize.

**Q: Why can't I use `process.stderr.read(500)` to check for errors safely?**
`read(500)` blocks until it receives 500 bytes. If there's no error, it waits forever. Only use it for debugging, never in production code.

**Q: What is `npx` vs global install?**
`npx package-name` downloads and runs a package without installing it permanently. `npm install -g package-name` installs it globally so you can run it by name anytime. Use npx for one-off runs, global install when you need it available as a command.

**Q: Can I mix MCP tools with custom tools?**
Yes — fetch MCP tools, define your own schemas, merge both lists before passing to LLM. Agent routes to MCP client or local function depending on tool name.

**Q: YouTube RAG idea — how would it work?**
Follow preferred channels → auto-fetch transcripts → chunk + embed → store in ChromaDB with metadata (channel, video, date) → retrieve relevant chunks when user asks a question → agent answers with source attribution. Full design added to CLAUDE.md.

---

## What Went Wrong and Why

### Spotify blocked by Premium
Spotify Web API requires Premium for playlist creation. Free accounts can't use it.
**Lesson:** Check API tier requirements before starting setup.

### `CaullenOmdahl` YouTube Music server too complex
Needed PostgreSQL, Redis, Spotify credentials. A full web app, not a simple MCP server.
**Lesson:** Low star count + complex infrastructure = high risk for a learning project. Read the `.env.example` before committing to a server.

### `zubeid-youtube-mcp-server` broken dependency
`@modelcontextprotocol/sdk` not properly declared as a dependency. Package installs but crashes on startup.
**Lesson:** Community packages can have broken dependency trees. When a package fails with `MODULE_NOT_FOUND` after install, it's a packaging bug, not your code.

### API keys exposed in chat
Pasted `.env` contents and credentials into the conversation.
**Lesson:** Never paste `.env` contents or credentials anywhere. Rotate immediately if exposed. Store secrets only in `.env` and never commit it.

---

## Security Note
Rotated today:
- OpenAI API key
- YouTube Data API key
- Spotify credentials (deleted the app entirely)

Always rotate immediately when credentials are exposed anywhere — chat, logs, screenshots.

---

## Tomorrow — Resume Here

1. Do a verbal walkthrough of the full system (no code) — consolidate understanding
2. Phase 4 — Telegram bot
   - Wrap agent in `python-telegram-bot` polling bot
   - Show THINK/ACT/OBSERVE as individual Telegram messages
   - Add YES/NO confirmation buttons for write actions
   - Add `/stop` emergency command
   - User ID lock

---

## Project Status

**Phase 1 — Complete**
**Phase 2a — Complete**
**Phase 2b — Parked**
**Phase 3 — Complete (two MCP servers working)**
**Phase 4 — Starting tomorrow**
