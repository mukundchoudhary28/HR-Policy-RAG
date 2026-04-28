import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings

from ragas.llms import llm_factory
from ragas.embeddings import OpenAIEmbeddings
from ragas.metrics.collections import (
    Faithfulness,
    AnswerRelevancy,
    ContextPrecision,
    ContextRecall
)

from src.rag.pipeline import run_rag_pipeline
from src.core.config import get_settings
from src.rag.hybrid_search import get_hybrid_retriever
from evaluation.eval_dataset_v2 import ragas_eval_set

# ---------------------------------------------------------------------------

load_dotenv()

# ---------------------------------------------------------------------------
#Initialization

client = AsyncOpenAI()
settings = get_settings()
retriever = get_hybrid_retriever()

semaphore = asyncio.Semaphore(5)  # max 5 concurrent
hf_embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)

ragas_llm = llm_factory("gpt-4o-mini", client=client, max_tokens=800)
ragas_embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    client=client
)

# Metrics
faithfulness = Faithfulness(llm=ragas_llm)
answer_relevancy = AnswerRelevancy(llm=ragas_llm, embeddings=ragas_embeddings)
context_precision = ContextPrecision(llm=ragas_llm, embeddings=ragas_embeddings)
context_recall = ContextRecall(llm=ragas_llm, embeddings=ragas_embeddings)

# ---------------------------------------------------------------------------
# Functions

async def evaluate_single(q):
    async with semaphore:

        loop = asyncio.get_running_loop()

        try:
            #run_rag_pipeline is a blocking function. Therefore, running it in a separate thread ensures that it becomes non-blocking and allows for async calls.
            result = await loop.run_in_executor(
                None,
                run_rag_pipeline,
                q["question"],
                hf_embeddings,
                retriever
            )
        except Exception as exc:
            print(f"  ✗ Pipeline failed for [{q['id']}]: {exc}")
            return None


        # Evaluating a response on several metrics concurrently by using asyncio.gather
        scores_list = await asyncio.gather(
            faithfulness.ascore(
                user_input=q["question"],
                response=result["answer"],
                retrieved_contexts=result["contexts"]
            ),
            answer_relevancy.ascore(
                user_input=q["question"],
                response=result["answer"]
            ),
            context_precision.ascore(
                user_input=q["question"],
                retrieved_contexts=result["contexts"],
                reference=q["expected_answer"]

            ),
            context_recall.ascore(
                user_input=q["question"],
                retrieved_contexts=result["contexts"],
                reference=q["expected_answer"]
            )
        )

        scores = {
            "faithfulness": scores_list[0].value,
            "answer_relevancy": scores_list[1].value,
            "context_precision": scores_list[2].value,
            "context_recall": scores_list[3].value,
        }

        return {
            "id": q["id"],
            "question": q["question"],
            "answer": result["answer"],
            "expected_answer": q["expected_answer"],
            "scores": scores
        }
    

async def run_eval():
    tasks = [evaluate_single(q) for q in ragas_eval_set["questions"]]
    
    # Evaluating several responses concurrently by using asyncio.gather
    results = await asyncio.gather(*tasks)
    return results


async def main():
    results = await run_eval()

    rows = []
    for r in results:
        row = {
            "id": r["id"],
            "question": r["question"],
            "RAG answer": r["answer"],
            "Expected Answer": r["expected_answer"],
            **r["scores"]
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    print("\n📊 Results:")
    print(df)
    print("\n📈 Averages:")
    print(df.mean(numeric_only=True)[1:])

    df.to_csv("evaluation_results_async.csv", index=False)

asyncio.run(main())