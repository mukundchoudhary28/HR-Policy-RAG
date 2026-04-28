from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from typing import Dict
from api.models import Filter
from prompts.create_filter import prompt_template


def create_filter(query: str) -> Dict:

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.2, max_tokens=500)
    llm = model.with_structured_output(Filter)
    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | llm

    response = chain.invoke({
        "query": query
    })

    filter = response.model_dump()
    return filter
