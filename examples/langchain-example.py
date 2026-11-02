# Install: python3 -m pip install langchain-openai
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

model = ChatOpenAI(
    base_url=os.environ["OPENAI_BASE_URL"],
    api_key=os.environ["OPENAI_API_KEY"],
    model=os.environ["OPENAI_MODEL"],
    use_responses_api=False,
    timeout=120,
    max_retries=2,
)
prompt = ChatPromptTemplate.from_messages([
    ("system", "Classify survey sentiment. Reply with only positive, negative, mixed or neutral."),
    ("human", "{response}"),
])
chain = prompt | model
result = chain.invoke({"response": "The course was useful, but I wanted more exercises."})
print(result.content)
# Streaming alternative:
# for chunk in chain.stream({"response": "The examples were clear and helpful."}):
#     print(chunk.content, end="", flush=True)
