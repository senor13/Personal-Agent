# Daily Tracker — 2026-04-04 — Phase 6a RAG Pipeline Complete

---

## Quick Summary
- Built full RAG pipeline from scratch — PDF ingestion to agent retrieval
- Used PyMuPDF for text extraction, RecursiveCharacterTextSplitter for chunking
- OpenAI `text-embedding-3-small` for embeddings (batched)
- ChromaDB with cosine similarity for vector storage
- Cross-encoder reranker (`ms-marco-MiniLM-L-6-v2`) for result reranking
- Added `RAG_tool` to agent — retrieves from AI Engineering book on demand

---

## What Was Built

### `AI/rag/rag.py`

**Ingestion (runs once)**
- Load PDF with PyMuPDF
- Extract text from all pages
- Chunk with `RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)`
- Embed chunks in batches of 2048 using `text-embedding-3-small`
- Store in ChromaDB `PersistentClient` — survives restarts
- Collection: `AI_book_oreily` with `hnsw:space: cosine`
- Guard: only ingests if `collection.count() == 0`
- Total chunks: **2412**

**Retrieval (runs on every query)**
```python
def retrieval(message):
    query = embed([message])
    results = collection.query(query_embeddings=query, n_results=5)
    retrieved_chunks = results["documents"][0]
    pairs = [(message, chunk) for chunk in retrieved_chunks]
    scores = reranker.predict(pairs)
    ranked_chunks = sorted(zip(scores, retrieved_chunks), key=lambda x: x[0], reverse=True)
    final_retrieved = ""
    for score, chunk in ranked_chunks:
        if score > 0:
            final_retrieved += chunk + "\n\n"
    return final_retrieved
```

### `AI/agent.py` — RAG tool added
```python
{
    "name": "RAG_tool",
    "description": "ALWAYS use this tool first when user asks ANY question about AI, LLMs, agents, RAG, fine-tuning, evaluation..."
}
```
Added to `function_map`: `"RAG_tool": retrieval`

---

## Key Concepts Learned

### Similarity metric vs indexing algorithm
- **Cosine, L2, dot product** — similarity metrics (how to measure distance between vectors)
- **HNSW, IVF** — indexing algorithms (how to search efficiently through millions of vectors)
- ChromaDB uses HNSW by default. `hnsw:space: cosine` sets the metric, not the algorithm

### Why cosine over L2 for text
Cosine measures angle between vectors, ignores magnitude. L2 measures straight-line distance, sensitive to magnitude. For text embeddings, direction matters more than length — cosine is better.

### Reranking
Cross-encoder sees query + chunk together (not separately like bi-encoder). Slower but more accurate. Scores can be negative — negative = chunk not relevant to query. Filter out negative scores before passing to LLM.

### PersistentClient
ChromaDB saves to disk. Next run loads existing data — no re-ingestion needed. `get_or_create_collection` reuses existing collection.

### Batched embedding
OpenAI embeddings API max 2048 texts per call. For 2412 chunks: two batches (2048 + 364). Use `extend` to combine results.

### Tool description controls retrieval behavior
Vague description = agent answers from own knowledge. Explicit "ALWAYS use this tool first" = agent calls RAG before answering.

---

## RAG Pipeline Architecture

```
User query
→ embed query (text-embedding-3-small)
→ ChromaDB vector search (cosine, top-5)
→ Cross-encoder reranking (ms-marco-MiniLM-L-6-v2)
→ Filter negative scores
→ Pass relevant chunks to LLM
→ LLM answers using chunks as context
```

---

## Bugs Fixed

### `embed_model` not defined
Function was renamed to `embed` but old name used in retrieval. Fix: use `embed`.

### Query embedding returning 2412 vectors
Passing string instead of list to `embed()`. String iteration = one embedding per character batch. Fix: `embed(["query string"])`.

### ChromaDB results nested list
`results["documents"]` returns `[[chunk1, chunk2, ...]]`. Need `[0]` to get flat list.

### Agent not calling RAG tool
Tool description too vague — agent answered from own knowledge. Fixed with explicit "ALWAYS use this tool first" instruction.

---

## Project Status

**Phase 1 — Complete**
**Phase 2a — Complete**
**Phase 2b — Complete**
**Phase 3 — Complete**
**Phase 4 — Complete**
**Phase 5 — In Progress**
**Phase 6a — Complete (RAG pipeline working)**
**Phase 6b — Not started (multi-agent + YouTube RAG)**
**Phase 7 — Partially done (metrics in run_bot.py)**
**Phase 8 — Complete (eval framework)**

---

## Tomorrow — Resume Here

Decide: multi-agent architecture or add second book first?
Then cover remaining topics:
- Multi-agent orchestrator
- Memory as RAG database
- Rubrics-based evaluation
- Guardrails
- Gmail tool
