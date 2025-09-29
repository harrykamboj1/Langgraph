from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
import datetime
from langchain_ollama import ChatOllama
from schema import AnswerQuestion  # your schema
from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langchain_core.messages import HumanMessage

llm = ChatOllama(model="qwen2:7b")

pydanticToolsParser = PydanticToolsParser(tools=[AnswerQuestion])

actor_prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system",
         """You are an expert AI Researcher.
         Current time: {time}

         1. {first_instruction}
         2. Reflect and critique your answer. Be **very severe** and specific.
         3. After the Reflection, **list 1-3 search queries separately** for researching improvements.

         📝 Respond **ONLY** in the following strict JSON format:

         {{
           "answer": "Your detailed 250-word answer here",
           "reflection": "Your reflection and critique here",
           "search_queries": "1-3 search queries seperate for improvements to address the critiques of your current answer"
         }}
         """),
        MessagesPlaceholder(variable_name="messages"),
        ("system", "Answer the user's question above using the required JSON format exactly."),
    ]
).partial(time=lambda: datetime.datetime.now().isoformat())

# 4️⃣ Pre-fill first instruction
first_response_prompt_template = actor_prompt_template.partial(
    first_instruction="Answer the question in 250 detailed words."
)

# 5️⃣ Build chain: prompt → LLM → parser
first_response_chain = first_response_prompt_template | llm | pydanticToolsParser

# 6️⃣ Invoke
response = first_response_chain.invoke({
    "messages": [HumanMessage(content="Write me a blog on LLM")]
})

# 7️⃣ Output structured data
print("\n--- Parsed Response ---")
print(response)
