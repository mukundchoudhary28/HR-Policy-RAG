from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List

from src.core.config import settings


def split_docs_into_chunks(document: Document, chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap) -> List[Document]:
    text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap,
    separators=["\n\n", "\n", ".", " "]
    )
    chunks = text_splitter.split_documents([document])
    return chunks