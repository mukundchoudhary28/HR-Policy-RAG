from fastapi import FastAPI, UploadFile, File, HTTPException
import glob
import shutil
from typing import List
from contextlib import asynccontextmanager
from pathlib import Path


from src.core.config import get_settings
from src.rag.loader import upload_and_load_docs
from src.rag.chunking import split_docs_into_chunks
from src.rag.embedding import embed_chunks, store_chunks_in_db
from src.rag.hybrid_search import get_hybrid_retriever, HybridRetriever
from src.rag.reranker import CrossEncoderReranker

from src.rag.embedding import embed_user_query
# from src.rag.retrieval import retrieve_relevant_chunks
from src.generator.llm import llm_call

from langchain_huggingface import HuggingFaceEmbeddings
from langsmith import traceable
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

settings = get_settings()
model = HuggingFaceEmbeddings(model_name=settings.embedding_model)

retriever: Optional[HybridRetriever] = None
_reranker_singleton = CrossEncoderReranker()

def _rebuild_retriever() -> HybridRetriever:
    """Rebuild retriever with latest BM25 index."""
    global retriever
    retriever = get_hybrid_retriever(reranker=_reranker_singleton)
    return retriever

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up the application...")
    files = glob.glob(f"{settings.documents_dir}/**/*.docx", recursive=True)
    print("Starting document ingestion...")
    all_chunks = []

    for file_path in files:
        print(f"Processing: {file_path}")
        doc = upload_and_load_docs(file_path)  # Your code skips if unchanged
        if doc is None:
            continue
        chunks = split_docs_into_chunks(doc)
        all_chunks.extend(chunks)

    if len(all_chunks) != 0:
        embeddings = embed_chunks(all_chunks, model)
        store_chunks_in_db(embeddings)

    retriever = _rebuild_retriever()

    print("Startup complete... ready to serve requests.")

    yield

    # shutdown logic
    print("Shutting down...")

app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": f"Welcome to {settings.app_name}!"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/ingest")
async def ingest(files: List[UploadFile] = File(...)):
    """Ingest a new or updated document."""

    logs = []
    all_chunks = []

    for file in files:
        if not file.filename.endswith('.docx'):
            raise HTTPException(400, "Only .docx files allowed")
    
        file_path = settings.documents_dir / file.filename
        

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        doc = upload_and_load_docs(str(file_path))
        
        if doc is None:
            logs.append({"filename": file.filename, "status": "unchanged"})
            continue
        
        chunks = split_docs_into_chunks(doc)
        logs.append({"filename": file.filename, "status": "indexed", "chunks": len(chunks)})
        all_chunks.extend(chunks)

    if len(all_chunks) != 0:
        chunk_embeddings = embed_chunks(all_chunks, model)
        store_chunks_in_db(chunk_embeddings)

        retriever = _rebuild_retriever()

        
    return {"message": "Ingestion complete", "logs": logs}






def _format_context(results: List[dict]) -> str:
    """Format retrieval results into LLM context string."""
    contexts = []
    for r in results:
        content = r["content"]
        metadata = r.get("metadata", {})
        file_path = metadata.get("file_name", "Unknown")
        file_name = Path(file_path).name
        contexts.append(f"[{file_name}]\n{content}")
    return "\n\n".join(contexts)


import time
# from fastapi.concurrency import run_in_threadpool

# @app.post("/query")
# @traceable(name="Query")
# async def query(q: str):
#     t0 = time.perf_counter()
    
#     # 1. Embedding (CPU-bound — MUST run in threadpool)
#     t1 = time.perf_counter()
#     query_embedding = await run_in_threadpool(embed_user_query, q, model)
#     t2 = time.perf_counter()
#     print(f"[TIMING] Embedding: {t2-t1:.3f}s")
    
#     # 2. Retrieval (CPU-bound — BM25 + CrossEncoder block the event loop!)
#     t3 = time.perf_counter()
#     results = await run_in_threadpool(
#         retriever.search, query=q, query_embedding=query_embedding, filters={}
#     )
#     t4 = time.perf_counter()
#     print(f"[TIMING] Retrieval: {t4-t3:.3f}s")
    
#     # 3. Context formatting
#     t5 = time.perf_counter()
#     context = _format_context(results)
#     t6 = time.perf_counter()
#     print(f"[TIMING] Context format: {t6-t5:.3f}s")
    
#     # 4. LLM call (sync LLM calls also block!)
#     t7 = time.perf_counter()
#     result = await run_in_threadpool(llm_call, context, q)
#     t8 = time.perf_counter()
#     print(f"[TIMING] LLM call: {t8-t7:.3f}s")
    
#     print(f"[TIMING] TOTAL: {t8-t0:.3f}s | Untraced overhead: {t8-t0 - ((t2-t1)+(t4-t3)+(t6-t5)+(t8-t7)):.3f}s")
    
#     return {
#         "query": q,
#         "answer": result.answer,
#         "citations": result.sources,
#         "_timing": {
#             "embedding_ms": round((t2-t1)*1000),
#             "retrieval_ms": round((t4-t3)*1000),
#             "format_ms": round((t6-t5)*1000),
#             "llm_ms": round((t8-t7)*1000),
#             "total_ms": round((t8-t0)*1000),
#         }
#     }

import os
import json
from fastapi import HTTPException


@app.get("/list")
def get_file_names():
    HASH_FILE = settings.HASH_FILE_PATH

    if not os.path.exists(HASH_FILE):
        return {"files": [], "message": "No files indexed yet"}

    try:
        with open(HASH_FILE, "r") as f:
            mapping = json.load(f)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Corrupted hash file")

    if not mapping:
        return {"files": [], "message": "No files indexed yet"}

    files = [
        {
            "file_name": Path(path).name,
            "path": path,
            "hash": value
        }
        for path, value in mapping.items()
    ]

    return {"files": files}


from src.core.dependencies import get_chroma_collection

@app.post("/delete")
def delete_file(file_name: str):
    HASH_FILE = settings.HASH_FILE_PATH

    if not os.path.exists(HASH_FILE):
        raise HTTPException(status_code=404, detail="No files indexed")

    with open(HASH_FILE, "r") as f:
        mapping = json.load(f)

    # find matching paths
    matching_paths = [
        path for path in mapping.keys()
        if Path(path).name == file_name
    ]

    if not matching_paths:
        raise HTTPException(status_code=404, detail="File not found")

    # 🔥 1. Remove from vector DB
    for path in matching_paths:
        collection = get_chroma_collection()
        collection.delete(where={"file_name": path})
        retriever = _rebuild_retriever()

    # 🔥 2. Remove from manifest
    for path in matching_paths:
        del mapping[path]

    with open(HASH_FILE, "w") as f:
        json.dump(mapping, f, indent=2)

    # 🔥 3. Optional: delete actual file
    for path in matching_paths:
        if os.path.exists(path):
            os.remove(path)

    return {
        "deleted_files": [Path(p).name for p in matching_paths]
    }





@app.post("/query")
@traceable(name="Query")
async def query(q: str):
    """Query the RAG system."""

    query_embedding = embed_user_query(q, model)

    results = retriever.search(
        query=q,
        query_embedding=query_embedding,
        filters={"Is Latest": "Yes"}
    )

    context = _format_context(results)
    result = llm_call(context, q)
    
    return {
        "query": q,
        "answer": result.answer,
        "citations": result.sources
    }