# Daily Tracker — 2026-03-25 — Phase 3: MCP Client & Google Calendar Integration

---

## Quick Summary
- Built custom MCP client from scratch in `mcp/client.py`
- Connected to Google Calendar MCP server via stdio
- Agent now books, updates and deletes real calendar events
- Memory correctly influencing agent behavior (no meetings before certain time)
- Phase 3 complete — real external service working end to end

---

## Files Created / Modified Today

| File | Status | What changed |
|---|---|---|
| `mcp/client.py` | New | Custom MCP client — connect, fetch tools, execute tools, disconnect |
| `ai/agent.py` | Updated | Removed mock tools, added process parameter, uses MCP client |
| `scripts/run_terminal.py` | Updated | Added connect/disconnect server, passes process to run_agent |
| `credentials/gcp-oauth.keys.json` | New | Google OAuth credentials (never commit this) |

---

## What You Built Today

### `mcp/client.py`
Four functions:

**`connect_server()`**
- Spawns the Google Calendar MCP server as a subprocess using `subprocess.Popen`
- Passes `GOOGLE_OAUTH_CREDENTIALS` env var so the server can authenticate with Google
- Uses `{**os.environ, "GOOGLE_OAUTH_CREDENTIALS": "..."}` — copies all existing env vars and adds the new one
- Returns the process object for other functions to use

**`fetch_tools(process)`**
- Sends `tools/list` JSON-RPC request to the server via stdin
- Reads response from stdout
- Converts MCP tool format to OpenAI tool format (`inputSchema` → `parameters`, wrapped in `type: function`)
- Returns list of tools ready to pass to OpenAI

**`execute_tools(process, tool_name, arguments)`**
- Sends `tools/call` JSON-RPC request with tool name and arguments
- Reads and returns the result
- Arguments come in as a parsed dict from `agent.py`

**`disconnect_server(process)`**
- Closes stdin pipe
- Waits for process to terminate cleanly

### `ai/agent.py`
- Removed mock tools import and hardcoded tool schemas
- Added `process` parameter to `run_agent(messages, process)`
- Tools fetched dynamically via `fetch_tools(process)` at start of each session
- Tool execution via `execute_tools(process, tool_name, arguments)`
- `arguments` parsed with `json.loads()` before passing to execute

### `scripts/run_terminal.py`
- Imports `connect_server` and `disconnect_server` from `mcp/client`
- Connects before conversation loop, disconnects after
- Passes `process` to `run_agent`

---

## Key Concepts Learned Today

### MCP architecture
```
run_terminal.py → agent.py → llm.py
                     ↓
               mcp/client.py → MCP server process → Google Calendar API
```
MCP client does NOT talk to the LLM. It only talks to the server. `agent.py` is the coordinator.

### stdio transport
The MCP server runs as a local subprocess. Your Python code spawns it with `subprocess.Popen`. Communication happens via stdin (write requests) and stdout (read responses). No HTTP, no ports — just two processes on your machine talking through pipes.

### JSON-RPC protocol
Every message follows this format:
- Request: `{"jsonrpc": "2.0", "id": timestamp, "method": "tools/list", "params": {}}`
- Response: `{"jsonrpc": "2.0", "id": timestamp, "result": {...}}`

`id` links responses to requests. Always `"2.0"` for version.

### Why MCP
Not about schema format. About standardization — every service uses the same `tools/list` and `tools/call` protocol. Adding Spotify or Gmail = just connect a new server. Agent automatically knows the new tools. Zero changes to agent logic.

### Tool schema conversion
MCP format uses `inputSchema`. OpenAI expects `parameters` wrapped in `{"type": "function", "function": {...}}`. One-time conversion in `fetch_tools`. Write once, forget it.

### flush() is critical
`write()` puts message in buffer. `flush()` actually sends it. Without `flush()` — deadlock. Client waits for response that never comes because server never got the request.

### env vars in subprocess
```python
env={**os.environ, "MY_VAR": "value"}
```
Must include `**os.environ` — without it subprocess has no PATH and can't find `npx`.

---

## Key Questions Asked & What You Learned

**Q: I thought MCP handles credentials — why do I still need Google OAuth?**
MCP doesn't bypass authentication. It's just a communication protocol between your client and the server. The MCP server still needs valid credentials to talk to Google's API on your behalf. MCP = the pipe. OAuth = the key to the door.

**Q: How does Google Calendar connect via a "local" MCP server if Google runs in the cloud?**
The local MCP server is a middleware process on your machine. It receives tool calls from your client (via stdio), translates them into Google Calendar API calls (via HTTPS), and returns results. Your agent talks to the local process — the local process talks to Google.

**Q: What is Node.js and why is it needed?**
Node.js is a JavaScript runtime — it runs JavaScript code outside the browser. The Google Calendar MCP server is written in JavaScript/TypeScript, so Node.js runs it. You don't write any JavaScript — you just need it installed to run the server, like a dependency.

**Q: What does "spawn" mean?**
Starting a new process from your Python code using `subprocess.Popen`. Equivalent to typing a command in the terminal, but done programmatically. Your Python code becomes the "terminal" that runs the MCP server.

**Q: What is JSON-RPC and how is it different from JSON?**
JSON is just a data format — a way to structure data as text. JSON-RPC is a protocol built on top of JSON — it adds rules about how two systems communicate. Every request must have `jsonrpc`, `id`, `method`, `params`. Every response must have `jsonrpc`, `id`, `result`. The `id` links responses to requests. JSON = the language. JSON-RPC = the conversation rules.

**Q: Why is `jsonrpc` always `"2.0"`?**
It's a fixed protocol version string, not something that changes between calls. Always `"2.0"` — it just tells both sides they're using the same version of the protocol.

**Q: What does `process.stdin.flush()` do and why is it critical?**
`write()` puts data in a buffer in memory. `flush()` forces it to actually send. Without `flush()` — deadlock. Your client waits for a response that never comes because the server never received the request.

**Q: Why `{**os.environ, "MY_VAR": "value"}` instead of just `{"MY_VAR": "value"}`?**
Without `os.environ`, the subprocess only gets that one variable and nothing else — no PATH, so it can't find `npx`, no HOME, nothing works. `**os.environ` copies all existing environment variables, then you add your new one on top.

**Q: What is the point of MCP if you have to convert schemas every time?**
MCP's value is standardization of tool discovery and execution, not schema format. Without MCP, every service has its own API and calling convention. With MCP, every service uses the same `tools/list` and `tools/call` protocol. The schema conversion is a one-time 5-line function. The payoff is: adding Spotify or Gmail = just connect a new server, zero agent code changes.

**Q: Can I mix MCP tools with custom tools?**
Yes — common pattern. Fetch MCP tools from the server, define your own custom tool schemas, merge both lists before passing to the LLM. The LLM sees one flat list and doesn't know which are MCP vs custom. `agent.py` routes tool calls to the right place — MCP client for MCP tools, local function for custom ones.

---

## What Went Wrong and Why

### `client.py` in wrong folder
Created `mcp/client.py` inside `Personal-Agent/AI/mcp/` instead of `Personal-Agent/mcp/`. Python couldn't find it.

**Fix:** `mv` to correct path.

**Lesson:** Always verify file paths with `find` when imports fail.

### Permission denied creating token directory
`~/.config` was owned by root so couldn't create subdirectory.

**Fix:** `sudo mkdir` + `sudo chown` to take ownership.

---

## Experiment Results

**Memory in action:** Agent knew not to schedule before a certain time — pulled from `long_term.json` correctly.

**Agent assumed email:** Used `amit@example.com` as dummy before being given real email. System prompt says "don't assume" but agent assumed contact details anyway.

**Follow up experiment:** How would you change the system prompt to prevent assuming contact details specifically? Try adding: "Never assume email addresses or contact details — always ask."

---

## Reflection — Answered Correctly

1. **MCP client job:** Connects to MCP server, fetches available tools, executes tool calls as requested by the agent
2. **Why return (response, message):** Message list is the conversation history — must be returned so run_terminal can pass full context to LLM on next turn
3. **Without flush():** Message sits in buffer, server never receives request, client waits forever — deadlock

---

## Tomorrow — Resume Here

Options for next session:
1. **Phase 2b** — auto memory extraction after session
2. **Add Spotify MCP server** — second tool integration
3. **Phase 4** — wrap in Telegram bot

Suggested: Add Spotify MCP server first (Phase 3 extension) — completes the two core use cases before moving to Telegram.

---

## Project Status

**Phase 1 — Complete**
**Phase 2a — Complete**
**Phase 2b — Parked**
**Phase 3 — Complete**
**Phase 4 — Not started**
