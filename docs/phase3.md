# Phase 3 — MCP Tool Connection
## Custom MCP Client + Google Calendar Integration

---

## What Was Built

A custom MCP client from scratch that connects to the Google Calendar MCP server via stdio. The agent now books, updates, and deletes real calendar events through natural language.

Mock tools are gone. Real tools are fetched dynamically from the MCP server at session start.

---

## Files Created / Modified

```
mcp/
└── client.py          # New — custom MCP client

ai/
└── agent.py           # Updated — uses MCP client instead of mock tools

scripts/
└── run_terminal.py    # Updated — connects/disconnects MCP server

credentials/
└── gcp-oauth.keys.json  # Google OAuth credentials (never commit)
```

---

## Architecture

```
run_terminal.py
    ├── connect_server()         # spawns MCP server process
    ├── run_agent(messages, process)
    │       ├── fetch_tools(process)      # get tools from MCP server
    │       ├── call_llm(messages, tools) # LLM decides what to do
    │       └── execute_tools(process, tool_name, args)  # MCP server executes
    └── disconnect_server(process)
```

---

## How MCP Works in This Project

### Transport: stdio
The MCP server (`@cocal/google-calendar-mcp`) runs as a local Node.js subprocess. Your Python MCP client spawns it with `subprocess.Popen` and communicates through stdin/stdout pipes.

```
Python client  →  stdin pipe  →  Node.js MCP server  →  Google Calendar API
Python client  ←  stdout pipe ←  Node.js MCP server  ←  Google Calendar API
```

### Protocol: JSON-RPC 2.0
Every message is a JSON object:

**Request:**
```json
{
    "jsonrpc": "2.0",
    "id": 1234567890,
    "method": "tools/list",
    "params": {}
}
```

**Response:**
```json
{
    "jsonrpc": "2.0",
    "id": 1234567890,
    "result": { "tools": [...] }
}
```

### Tool discovery
On connection, client calls `tools/list` to fetch all available tools dynamically. No hardcoding. Connect a new MCP server and the agent automatically knows its tools.

### Tool execution
When LLM requests a tool call, client sends `tools/call` with the tool name and arguments. Server executes it and returns the result.

---

## `mcp/client.py` — Full Reference

### `connect_server()`
```python
subprocess.Popen(
    ["npx", "@cocal/google-calendar-mcp"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    env={**os.environ, "GOOGLE_OAUTH_CREDENTIALS": "/path/to/gcp-oauth.keys.json"}
)
```
Returns the process object. Must be passed to all other functions.

### `fetch_tools(process)`
1. Sends `tools/list` JSON-RPC request
2. Reads response from stdout
3. Converts MCP format → OpenAI format
4. Returns list of tool schemas ready for OpenAI

**MCP → OpenAI conversion:**
```python
# MCP format
{"name": "create-event", "description": "...", "inputSchema": {...}}

# OpenAI format
{"type": "function", "function": {"name": "...", "description": "...", "parameters": {...}}}
```
`inputSchema` becomes `parameters`. Wrapped in `type: function`.

### `execute_tools(process, tool_name, arguments)`
1. Sends `tools/call` JSON-RPC request
2. Reads and returns result
3. `arguments` must be a Python dict (not JSON string)

### `disconnect_server(process)`
Closes stdin, waits for process to terminate.

---

## Key Technical Details

### Why `flush()` is critical
`write()` puts data in buffer. `flush()` forces it out to the server. Without it — deadlock. Client waits forever for a response the server never received.

### Why `{**os.environ, ...}` for env vars
Without `os.environ`, subprocess has no PATH and can't find `npx`. Always copy existing env vars and add on top.

### Why `json.loads()` on arguments
OpenAI returns tool arguments as a JSON string: `'{"calendarId": "primary"}'`. Must parse to dict before passing to `execute_tools`.

### Why return `(response, message)` from `run_agent`
`run_terminal.py` owns conversation history. `run_agent` must return the updated message list so the next turn has full context.

---

## Google Calendar Setup

### Prerequisites
1. Google Cloud project with Calendar API enabled
2. OAuth 2.0 credentials (Desktop app type) downloaded as JSON
3. Email added as test user in OAuth consent screen
4. Auth flow completed: `npx @cocal/google-calendar-mcp auth`
5. Tokens stored at `~/.config/google-calendar-mcp/tokens.json`

### Available tools (12 total)
Key ones used: `list-events`, `create-event`, `update-event`, `delete-event`, `get-freebusy`, `get-current-time`

---

## What Was Learned

### MCP value proposition
Not about schema format. About standardization:
- Every service uses same `tools/list` + `tools/call` protocol
- Adding new capability = connect new MCP server, zero agent code changes
- Agent discovers tools dynamically — no hardcoding

### Memory + MCP working together
Memory entry "never schedule before X time" correctly influenced agent behavior when booking real calendar events. Context engineering and tool execution working together.

### Agent assumed contact details
Despite "don't assume" in system prompt, agent used dummy email before being given real one. Prompt engineering gap — needs more specific instruction like "never assume email addresses, always ask."

---

## Common Mistakes Made

### Wrong folder path
Created `client.py` in `Personal-Agent/AI/mcp/` instead of `Personal-Agent/mcp/`. Import failed silently until path was verified with `find`.

### Permission denied on token directory
`~/.config` owned by root. Fixed with `sudo mkdir` + `sudo chown`.

---

## Extending to New MCP Servers

Adding Spotify or any other MCP server requires:
1. Install and auth the new MCP server
2. Update `connect_server()` to spawn it (or spawn multiple servers)
3. Zero changes to `agent.py` or `run_terminal.py`

The agent automatically discovers and uses the new tools via `tools/list`.

---

## Future: Combining MCP Tools + Custom Tools

```python
tool_map = {
    "create-event": lambda args: execute_tools(process, "create-event", args),
    "my_custom_tool": my_custom_function,  # your own logic
}
```

LLM sees one flat tool list. Doesn't know or care which tools are MCP vs custom.

---

## Phase 4 Preview — Telegram Bot

Next phase wraps the working agent in a Telegram polling bot.
- THINK/ACT/OBSERVE shown as individual Telegram messages
- YES/NO inline buttons before write actions
- `/stop` emergency command
- User ID lock

The agent loop does not change. Telegram is just a new delivery layer on top.
