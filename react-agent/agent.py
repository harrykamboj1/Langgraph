from langchain_openai import ChatOpenAI
from langchain.agents import tool, create_react_agent
import datetime
from langchain_community.tools import TavilySearchResults
from langchain import hub
import os
import getpass
from dotenv import load_dotenv
load_dotenv()

# Initialize the language model
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass(
        "Enter API key for OpenAI: ")

llm = ChatOpenAI(model="gpt-4", temperature=0)

search_tool = TavilySearchResults(search_depth="basic")


tools = [search_tool]
react_prompt = hub.pull('hwchase17/react')
agent = create_react_agent(llm, tools, prompt=react_prompt)
