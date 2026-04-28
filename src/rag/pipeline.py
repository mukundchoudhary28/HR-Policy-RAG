# src/rag/pipeline.py

from src.rag.embedding import embed_user_query
from src.rag.hybrid_search import get_hybrid_retriever
from src.generator.llm import llm_call
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

def run_rag_pipeline(question: str, model, retriever):

    query_embedding = embed_user_query(question, model)

    results = retriever.search(
        query=question,
        query_embedding=query_embedding,
        filters={"Is Latest": "Yes"},
    )

    contexts = []

    for x in results:
        content = x["content"]
        metadata = x.get("metadata", {})

        file_path = metadata.get("file_name", "Unknown")  # or "file_name" depending on your schema\
        file_name = Path(file_path).name

        formatted = f"[{file_name}]\n{content}"
        contexts.append(formatted)

    context = "\n\n".join(contexts)

    result = llm_call(context, question)

    return {
        "answer": result.answer,
        "citations": result.sources,
        "contexts": contexts
    }

# from langchain_huggingface import HuggingFaceEmbeddings
# from src.core.config import settings

# retriever = get_hybrid_retriever()
# model = HuggingFaceEmbeddings(model_name=settings.embedding_model)
# result = run_rag_pipeline("What is the maternity leave policy", model, retriever)
# print(result)