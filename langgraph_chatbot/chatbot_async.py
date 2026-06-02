from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun  # pyright: ignore[reportUnusedImport]
from langchain_core.tools import tool
import sqlite3
import requests
import random
import asyncio

load_dotenv()
import os
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

import sys
import subprocess

try:
    import ddgs  # noqa: F401
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "ddgs"])

search_tool = DuckDuckGoSearchRun(region="us-en")

@tool
def calculator(first_num: float, second_num: float, operator: str) -> dict:
    """
    Perform a basic arithmetic operator on teo numbers.
    Supported operations: add, sub, mul,dic
    """
    
    if operator == 'add':
        return {"result": first_num + second_num}
    elif operator == 'sub':
        return {"result": first_num - second_num}
    elif operator == 'mul':
        return {"result": first_num * second_num}
    elif operator == 'div':
        if second_num == 0:
            return {"error": "Division by zero is not allowed."}
        return {"result": first_num / second_num}
    else:
        return {"error": "Invalid operator. Please use one of the following: +, -, *, /."}

@tool    
def get_stock_price(symbol: str) -> dict:
    """"Fetch latest stock price for a given symbol using a free API."""

    api_key = os.getenv("ALPHAVANTAGE_API_KEY")
    if not api_key:
        raise ValueError("ALPHAVANTAGE_API_KEY is not set in the environment")

    url = (
        "https://www.alphavantage.co/query"
        f"?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
    )
    r = requests.get(url)
    return r.json()

tools = [get_stock_price, calculator, search_tool]

llm_with_tools = llm.bind_tools(tools)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def build_graph():

    async def chat_node(state: ChatState) -> ChatState:
        """LLM node that may answer or request a tool call."""
        messages = state["messages"]
        response = await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}

    tool_node = ToolNode(tools)

    #Checkpointer setup
    conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
    checkpointer = SqliteSaver(conn=conn)

    #Graph setup
    graph = StateGraph(ChatState)
    graph.add_node('chat_node', chat_node)
    graph.add_node('tools', tool_node)

    graph.add_edge(START, 'chat_node')
    graph.add_conditional_edges('chat_node', tools_condition)
    graph.add_edge('tools', 'chat_node')

    chatbot = graph.compile()

    return chatbot

    # def retrive_all_threads():
    #     all_threads = set()
    #     for checkpoint in checkpointer.list(None):
    #         all_threads.add(checkpoint.config['configurable']['thread_id'])
    #     return list(all_threads)

async def main():
    chatbot = build_graph()

    #running graph
    result = await chatbot.ainvoke({
        "messages": [HumanMessage(content="What is the stock price of AAPL?")]})
    print(result["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())


#7. Helper function to retrive all threads

