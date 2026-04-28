from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from src.prompts.generator import prompt_template
from src.core.config import settings
from src.api.models import ResponseSchema
from langsmith import traceable
import time

@traceable(name="Generator - LLM call")
def llm_call(relevant_chunks, user_query):


    llm = ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        temperature=settings.openai_temperature, 
        max_tokens=settings.openai_max_tokens
    )

    structured_llm = llm.with_structured_output(ResponseSchema)

    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | structured_llm

    response = chain.invoke({
        "relevant_chunks": relevant_chunks,
        "user_query": user_query
    })

    return response