import uuid
from pathlib import Path

from src.utils.reindexing import get_file_hash, load_hashes, save_hashes
from src.core.dependencies import get_chroma_collection
from langsmith import traceable

hashes = load_hashes()


def embed_chunks(chunks, model):

    collection = get_chroma_collection()

    ids = [str(uuid.uuid4()) for _ in chunks]
    embeddings = model.embed_documents([chunk.page_content for chunk in chunks])
    metadatas = [chunk.metadata for chunk in chunks]
    chunk_text = [chunk.page_content for chunk in chunks]

    files_modified = set(metadata['file_name'] for metadata in metadatas)
    for file in files_modified:
        file_hash = get_file_hash(Path(file))
        hashes[file] = file_hash
        collection.delete(where={"file_name": file})
    save_hashes(hashes)

    return {"ids": ids, "embeddings": embeddings, "documents": chunk_text, "metadatas": metadatas}


def store_chunks_in_db(chunk_embeddings):

    collection = get_chroma_collection()

    collection.add(
        ids=chunk_embeddings['ids'],
        embeddings=chunk_embeddings['embeddings'],
        documents=chunk_embeddings['documents'],
        metadatas=chunk_embeddings['metadatas'],
        )

@traceable(name="Embedding")
def embed_user_query(query: str, model):

    query_embedding = model.embed_query(query)
    return query_embedding
