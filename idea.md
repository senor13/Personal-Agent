
Personal AI Assistant — Project Brain Dump
What I am building
A personal AI assistant that I talk to via Telegram. I tell it what I want in plain language and it figures out what to do. To start with it can book calendar meetings and create Spotify playlists. Later I want to expand it to do much more — like summarising research papers, showing me news highlights, and finding new YouTube videos etc
The most important thing about this project is that I want to learn AI engineering. I am not trying to build a perfect product. I want to understand how agents think, how memory works, how to write good prompts, and how context affects the LLM's reasoning, learn when to use RAG, experiment with different models for embedding, indexing, similarity ranking etc. The software engineering side should be kept as simple as possible so it does not get in the way of the AI learning.

The core idea
I send a message to my assistant on Telegram. The assistant thinks about what I asked, decides what tools it needs, uses those tools, looks at the results, and keeps going until the task is done. Then it tells me what it did.
The assistant should show me its thinking as it works — not just give me a final answer. I want to see every THINK, ACT, and OBSERVE step directly in Telegram so I can understand what the agent is doing and why.

How the agent should think — ReAct approach
The agent must follow the ReAct pattern. This means before every action it reasons out loud, then it acts, then it observes the result. It repeats this cycle until the task is complete.
For example if I say "create a 30 minute meditation playlist on Spotify with calm instrumental music" — the agent should first think about what it needs to do, then search for tracks, then observe what it found, then create the playlist, then add the tracks, then tell me it is done. Every step should be visible to me on Telegram.

The AI part — this is the main focus
The AI folder is the heart of the project. Everything important lives here. The rest of the project is just simple plumbing to support it.
The agent loop is the most important piece. It is the cycle that calls the LLM, reads the response, executes tool calls, feeds results back, and repeats until the task is done. This is where all the interesting AI behavior happens.
The system prompt is how I control the agent's behavior and personality. I want to experiment with how different prompt structures affect the quality of the agent's reasoning. This is the context engineering part I want to learn deeply.
Memory is how the agent remembers things. There are two types. Short term memory is just the current conversation — what was said in this session. It is cleared when the task is done. Long term memory is information that persists across sessions — my preferences, things the agent has learned about me, patterns it has noticed. The agent should be able to access long term memory when it is relevant to the current task, rather than loading everything every time.
Tool descriptions are how I tell the LLM what tools are available and when to use them. I want to experiment with how the quality and wording of tool descriptions affects the agent's decisions.

Memory files
I want four types of memory storage:
Preferences file — things I explicitly tell the agent to always remember. For example never schedule meetings before 7am, or I prefer 30 minute meetings over 1 hour.
Long term memory file — cross session information. Things the agent learns about me over time that should be available in future conversations. For example that John is my research collaborator, or that I like calm instrumental music for focus sessions.
Task scratchpad — short term working notes for the current task. Cleared when the task is done.
Tool call log — a record of every tool the agent called, with what parameters, what the result was, and whether I confirmed or cancelled it. This is for auditing and debugging.
Design  long term memory file in a clean structured way — JSON or markdown with clear categories so that migrating to RAG later is straightforward. Each memory entry becomes a document to embed. The retrieval just replaces the current "load everything" approach with "load only what is relevant. RAG is for future and I will decide later when memory becomes long.

Tools and MCP servers
The agent connects to external services through MCP servers. I am building a custom MCP client from scratch — not using any built-in SDK support — because I want to understand how tool calling works at a low level.
To start with I want two MCP servers connected — Google Calendar for booking meetings and Spotify for creating playlists. The code should be structured so adding more MCP servers later is easy and does not require changing the agent logic.

What the agent can do to start with
Just two things to begin with:
Book a calendar meeting when I tell it to. For example "block 30 minutes with John on 15th April between 6 and 9am." The agent should check availability, find a slot, confirm with me before creating anything, and then book it with a Google Meet link.
Create a Spotify playlist based on my description. For example "create a 30 minute meditation playlist with calm instrumental music." The agent should search for tracks, create the playlist, add the tracks, and confirm it is done.

What I want to add later
Once the core is working and I have learned from it, I want to expand the assistant to handle more tasks. Things like showing me daily news highlights, finding new YouTube videos on topics I care about, summarising research papers I send it, managing emails, and anything else that becomes useful. Each new capability should be additive — just a new MCP server and tool description, nothing else should change.

Confirmation and safety
Before the agent does anything that changes the real world — creating a calendar event, sending a message, adding tracks to a playlist — it must pause and ask me to confirm with a simple YES or NO. It should never just act without my approval on write actions.
There should also be a simple emergency stop command I can send on Telegram that immediately halts whatever the agent is doing.
I also want basic protection against prompt injection — if any external content the agent reads contains something that looks like an instruction trying to hijack the agent, it should be stripped out before being sent to the LLM.

LLM
I am using OpenAI GPT-4o mini as the LLM. It is fast, cheap, and good enough for this use case. I want the architecture to be clean enough that switching to a different LLM later — like Claude or Gemini — requires changing as little code as possible.

What I am NOT using
I am deliberately not using LangChain or LangGraph. My goal is to understand how agents work from the ground up. Using a framework would hide the interesting parts. I am building the agent loop, memory, and tool calling myself so I actually learn how they work.

Development approach — phases
I want to build this in phases, starting as simple as possible and adding complexity only when the previous phase is working and understood.
Phase 1 — get the ReAct loop working in a plain Python script. No Telegram, no FastAPI. Just run it from the terminal and see the THINK, ACT, OBSERVE output. This is where the most learning happens.
Phase 2 — add memory. Short term conversation history and long term preferences. Experiment with how different memory structures affect the agent's reasoning.
Phase 3 — connect MCP tools. Google Calendar first, then Spotify. Experiment with tool descriptions and see how wording changes agent behavior.
Phase 4 — wrap in Telegram. Minimal polling bot. Show ReAct steps as messages. Add YES/NO confirmation buttons for write actions.
Phase 5 — experiment and expand. Add new tools one at a time. Each new tool is a learning experiment.
Phase 6 — production. Only after I have learned what I want to learn. Switch to webhook, add proper guardrails, deploy to a server.

Project structure
The project has two clearly separated parts.
The AI folder contains everything related to the agent's intelligence — the loop, the system prompt, the memory logic, and the tool definitions. This is where I spend most of my time and where all the interesting experiments happen. The code here should be well commented and easy to read.
Everything else — the Telegram bot, the MCP client, the FastAPI server — is kept as simple as possible. It is just the delivery mechanism. It should not distract from the AI work.

Final goal
By the end of this project I want to deeply understand how to engineer an AI agent — how to structure context, how memory affects reasoning, how tool descriptions influence decisions, and how the ReAct loop produces coherent multi-step behavior. The assistant itself is useful, but the learning is the real outcome.


