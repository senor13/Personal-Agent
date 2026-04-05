# Phase 6 — RAG

---

## Phase 6a — Book RAG ✅ Complete

### What Was Built

Full RAG pipeline — PDF ingestion, chunking, embedding, vector storage, retrieval with reranking.

### Files Created

| File | What it does |
|---|---|
| `AI/rag/rag.py` | Ingestion + retrieval — PDF → chunks → embeddings → ChromaDB → retrieval function |

### Ingestion Pipeline

```
PDF → PyMuPDF text extraction → RecursiveCharacterTextSplitter → OpenAI embeddings → ChromaDB
```

- **PyMuPDF** — extracts text page by page. Good for text-heavy books. Tables/formulas lose structure but text content extracts cleanly.
- **RecursiveCharacterTextSplitter** — splits by paragraph → sentence → word. Respects natural boundaries. `chunk_size=500, chunk_overlap=50`.
- **OpenAI `text-embedding-3-small`** — 1536-dimension embeddings. Batched at 2048 texts per API call.
- **ChromaDB PersistentClient** — saves to disk. Survives restarts. Collection: `AI_book_oreily`, cosine similarity.
- **Guard** — only ingests if `collection.count() == 0`. Safe to import without re-ingesting.

Total chunks from AI Engineering (O'Reilly): **2412**

### Retrieval Pipeline

```
User query → embed query → ChromaDB top-5 → cross-encoder reranking → filter negatives → LLM
```

- **Vector search** — cosine similarity, top-5 candidates
- **Cross-encoder reranking** — `cross-encoder/ms-marco-MiniLM-L-6-v2`. Scores each (query, chunk) pair together. More accurate than bi-encoder alone.
- **Negative score filtering** — chunks with score < 0 are not relevant, filtered out before passing to LLM
- **LLM answers** using retrieved chunks as context

### RAG Tool in Agent

```python
{
    "name": "RAG_tool",
    "description": "ALWAYS use this tool first when user asks ANY question about AI, LLMs, agents, RAG, fine-tuning, evaluation..."
}
```

Tool description must be explicit — vague descriptions cause agent to answer from own knowledge instead of retrieving.

---

## Key Concepts

### Similarity metric vs indexing algorithm

| Term | What it is |
|---|---|
| Cosine, L2, dot product | Similarity metrics — how to measure distance between vectors |
| HNSW, IVF | Indexing algorithms — how to search efficiently through millions of vectors |

ChromaDB uses HNSW by default. `hnsw:space: cosine` sets the metric.

### Why cosine for text
Cosine measures angle between vectors, ignores magnitude. Text embeddings encode meaning in direction, not length. Cosine is the standard choice for semantic similarity.

### Bi-encoder vs cross-encoder

| | Bi-encoder | Cross-encoder |
|---|---|---|
| How | Encodes query and chunk separately | Encodes query + chunk together |
| Speed | Fast (vectors pre-computed) | Slow (runs at query time) |
| Accuracy | Good | Better |
| Use | First-pass retrieval (top-K) | Reranking (re-score top-K) |

Use both: bi-encoder for fast candidate retrieval, cross-encoder for accurate reranking.

### PersistentClient
ChromaDB saves vector store to disk. `get_or_create_collection` reuses existing data. Ingestion runs once — all subsequent runs just load the existing store.

---

## Phase 6b — Multi-Agent RAG (Not Started)

### Planned Architecture

One ChromaDB instance, multiple collections (namespaces):

```
ChromaDB
├── collection: "research"    ← AI Engineering books
├── collection: "interview"   ← Interview Q&A
├── collection: "news"        ← Latest AI news
└── collection: "memory"      ← Agent long-term memory (Phase 6c)
```

Master orchestrator routes queries to specialized agents. Each agent queries only its own collection.

### Planned Agents

| Agent | Collection | Knowledge source |
|---|---|---|
| Research Agent | research | AI Engineering book, ML book, Vizuara book |
| Interview Agent | interview | Interview questions and answers |
| News Agent | news | Latest AI developments |
| YouTube Agent | youtube | Video transcripts from preferred channels |

### Phase 6c — Memory as RAG (Not Started)

Replace flat `long_term.json` full-load with semantic retrieval:
- Embed each memory entry on save
- Store in `memory` ChromaDB collection
- At session start: embed user message, retrieve top-K relevant memories
- Preferences file still loaded in full (small, always relevant)
