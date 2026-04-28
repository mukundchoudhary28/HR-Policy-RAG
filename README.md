# 📋 HR Policy RAG API

> An enterprise-grade **Retrieval-Augmented Generation (RAG)** system that lets employees query company HR documents in natural language — with cited, accurate answers grounded strictly in your own policy files.

---

## ✨ Features

| Feature | Detail |
|---|---|
| 🔍 **Hybrid Search** | Combines dense vector search (ChromaDB, cosine similarity) with sparse BM25 keyword search for best-of-both recall |
| ⚡ **Cross-Encoder Reranking** | `ms-marco-MiniLM-L-6-v2` reranker refines the candidate pool before sending context to the LLM |
| 🧠 **Structured LLM Output** | GPT-4o-mini returns a Pydantic-validated `{answer, citations}` schema — no free-form hallucination |
| 📄 **Document Version Awareness** | SHA-256 manifest detects unchanged files and skips re-ingestion; only the latest version of a document is retrieved |
| 🗂️ **Full Document Lifecycle** | REST endpoints for ingesting, listing, and deleting documents, with automatic vector-store cleanup |
| 🐳 **Docker-Compose Deployment** | API and Streamlit UI spin up as isolated services with persistent volumes and a health-check gate |
| 📊 **RAGAS Evaluation Suite** | Async evaluation pipeline measuring Faithfulness, Answer Relevancy, Context Precision, and Context Recall |
| 🔭 **LangSmith Tracing** | Every `Retrieval`, `Reranker`, and `Generator` step is traced for latency profiling and debugging |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI (:8501)                  │
└───────────────────────┬─────────────────────────────────┘
                        │  REST (JSON)
┌───────────────────────▼─────────────────────────────────┐
│                  FastAPI Backend (:8000)                 │
│                                                         │
│  POST /ingest      GET /list      POST /delete          │
│  POST /query                                            │
└─────────┬───────────────────────────┬───────────────────┘
          │                           │
┌─────────▼──────────┐   ┌───────────▼────────────────────┐
│   Ingestion Path   │   │          Query Path             │
│                    │   │                                 │
│  .docx → chunks   │   │  1. Embed query (MiniLM-L6)    │
│  MiniLM-L6 embed  │   │  2. Vector search  (Chroma)    │
│  ChromaDB persist │   │  3. BM25 keyword search        │
│  SHA-256 manifest │   │  4. Score fusion (0.7/0.3)     │
│  BM25 index build │   │  5. Cross-encoder rerank       │
└────────────────────┘   │  6. GPT-4o-mini generation    │
                         │  7. Return answer + citations  │
                         └────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- An OpenAI API key

### 1. Clone & configure

```bash
git clone https://github.com/your-username/hr-policy-rag.git
cd hr-policy-rag
cp .env.example .env          # fill in OPENAI_API_KEY and LANGSMITH_API_KEY
```

### 2. Run with Docker

```bash
docker-compose up --build
```

| Service | URL |
|---|---|
| FastAPI (Swagger UI) | http://localhost:8000/docs |
| Streamlit Chat UI | http://localhost:8501 |

### 3. Local Development (without Docker)

```bash
# Requires Python 3.12 and `uv`
uv sync
uvicorn src.main:app --reload           # API
streamlit run src/ui/app.py             # UI (separate terminal)
```

---

## ⚙️ Configuration

All settings are managed through environment variables (`.env`) and validated by **Pydantic Settings**.

```env
# LLM
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.2

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Retrieval tuning
TOP_K=5
VECTOR_WEIGHT=0.7
KEYWORD_WEIGHT=0.3
RERANKER_TOP_K=3

# Observability
LANGSMITH_API_KEY=ls__...
LANGSMITH_PROJECT=hr-policy-rag
```

---

## 📡 API Reference

### `POST /ingest`
Upload one or more `.docx` files. Unchanged files (same SHA-256) are skipped automatically.

```bash
curl -X POST http://localhost:8000/ingest \
  -F "files=@HR_policy.docx"
```

**Response**
```json
{
  "message": "Ingestion complete",
  "logs": [{"filename": "HR_policy.docx", "status": "indexed", "chunks": 42}]
}
```

### `POST /query`
Ask a natural-language question. Returns a grounded answer with document citations.

```bash
curl -X POST "http://localhost:8000/query?q=What+is+the+PTO+carryover+limit"
```

**Response**
```json
{
  "query": "What is the PTO carryover limit?",
  "answer": "Employees may carry over up to 5 days of unused PTO...",
  "citations": "HR policy_v2.docx"
}
```

### `GET /list`
List all currently indexed documents and their hash fingerprints.

### `POST /delete?file_name=<name>`
Remove a document from the vector store, BM25 index, and manifest in one atomic operation.

---

## 🔬 RAG Pipeline Deep Dive

### 1. Document Ingestion

- `.docx` files are loaded with `python-docx`, chunked with a sliding window (`chunk_size=900`, `overlap=75`), and embedded using `sentence-transformers/all-MiniLM-L6-v2`.
- Embeddings are persisted in **ChromaDB** (local disk).
- A `manifest.json` stores per-file SHA-256 hashes. On startup and re-ingest, only **changed or new** files are processed — making the pipeline idempotent.
- Each chunk carries rich metadata: `file_name`, `Is Latest`, `region`, `doc_type`, `effective_date`.

### 2. Hybrid Retrieval

```
Vector Score  ──(×0.7)──┐
                         ├──► Hybrid Score ──► Reranker ──► Top-3 chunks
BM25 Score    ──(×0.3)──┘
```

- **Vector search**: Chroma queries by cosine similarity; distance is normalised to a `[0,1]` score.
- **BM25**: A tokenized BM25 index (rebuilt from Chroma on every startup/ingest) provides complementary exact-keyword recall.
- Results from both arms are merged by `(content, file_name)` key; scores are summed for duplicates.
- **Only the latest version** of each document (`Is Latest == "Yes"`) is surfaced to the user.

### 3. Cross-Encoder Reranking

The hybrid top-K candidates are re-scored by a cross-encoder (`ms-marco-MiniLM-L-6-v2`) that reads the query and passage together — far more accurate than embedding cosine distance alone. The top `reranker_top_k=3` passages are passed to the LLM.

### 4. Generation

A LangChain `ChatPromptTemplate` wraps the retrieved context and user query. `gpt-4o-mini` is called with **structured output** bound to a Pydantic `ResponseSchema`, guaranteeing a machine-readable `{answer, sources}` response every time.

---

## 📊 Evaluation

The project ships with an async **RAGAS** evaluation harness:

```bash
python -m evaluation.evaluation_v2
```

| Metric | What it measures |
|---|---|
| **Faithfulness** | Is the answer supported by the retrieved context? |
| **Answer Relevancy** | Does the answer actually address the question? |
| **Context Precision** | Are the retrieved chunks actually useful? |
| **Context Recall** | Did retrieval capture all necessary information? |

Results are written to `evaluation_results_async.csv`. Up to 5 evaluations run concurrently via `asyncio.Semaphore` to respect API rate limits while still finishing the suite quickly.

---

## 🗂️ Project Structure

```
├── src/
│   ├── main.py              # FastAPI app, lifespan startup ingestion
│   ├── api/
│   │   └── models.py        # Pydantic request/response schemas
│   ├── core/
│   │   ├── config.py        # Pydantic Settings (all env vars)
│   │   └── dependencies.py  # FastAPI dependency injection (Chroma client)
│   ├── rag/
│   │   ├── loader.py        # .docx loading + SHA-256 change detection
│   │   ├── chunking.py      # Sliding-window text splitter
│   │   ├── embedding.py     # HuggingFace embedding helpers
│   │   ├── hybrid_search.py # HybridRetriever (vector + BM25 + score fusion)
│   │   ├── reranker.py      # CrossEncoderReranker (singleton)
│   │   └── pipeline.py      # End-to-end RAG pipeline (used by eval)
│   ├── generator/
│   │   └── llm.py           # LangChain LLM call with structured output
│   ├── prompts/
│   │   └── generator.py     # System & user prompt templates
│   └── ui/
│       └── app.py           # Streamlit chat interface
├── evaluation/
│   ├── evaluation_v2.py     # Async RAGAS evaluation runner
│   └── eval_dataset_v2.py   # Curated Q&A test set
├── data/
│   ├── documents/           # HR policy .docx files
│   └── manifest.json        # SHA-256 file hash registry
├── docker-compose.yaml
├── Dockerfile
└── pyproject.toml
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **API** | FastAPI, Pydantic v2, Uvicorn |
| **UI** | Streamlit |
| **LLM** | OpenAI GPT-4o-mini via LangChain |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` (HuggingFace) |
| **Vector Store** | ChromaDB (persistent, local) |
| **Keyword Search** | BM25 (`rank-bm25`) |
| **Reranker** | `cross-encoder/ms-marco-MiniLM-L-6-v2` (sentence-transformers) |
| **Evaluation** | RAGAS |
| **Tracing** | LangSmith |
| **Packaging** | `uv`, Python 3.12 |
| **Deployment** | Docker Compose |

---

## 🔮 Potential Extensions

- **Metadata filtering** — expose `region`, `doc_type`, and `effective_date` filters on the `/query` endpoint to narrow retrieval before hybrid search
- **PDF support** — `pdfplumber` is already a dependency; extend `loader.py` to handle `.pdf` alongside `.docx`
- **Streaming responses** — replace `llm_call` with a streaming LangChain chain and push tokens via FastAPI `StreamingResponse`
- **Redis caching** — config already defines `REDIS_URL`; add a query-level cache to short-circuit identical questions
- **CI integration** — gate PRs on the RAGAS evaluation suite using the configurable `EVALUATION_THRESHOLD`

---

## 📄 License

MIT