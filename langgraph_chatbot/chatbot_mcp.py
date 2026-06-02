from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
# from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode, tools_condition
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
load_dotenv()
import os
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


async def build_graph(tools, checkpointer):
    llm_with_tools = llm.bind_tools(tools)

    async def chat_node(state: ChatState) -> ChatState:
        response = await llm_with_tools.ainvoke(state["messages"])
        return {"messages": [response]}

    tool_node = ToolNode(tools)
    print(tools)

    graph = StateGraph(ChatState)
    graph.add_node('chat_node', chat_node)
    graph.add_node('tools', tool_node)

    graph.add_edge(START, 'chat_node')
    graph.add_conditional_edges('chat_node', tools_condition)
    graph.add_edge('tools', 'chat_node')

    return graph.compile(checkpointer=checkpointer)


async def main():
    client = MultiServerMCPClient(
        {
            "arith": {
                "transport": "stdio",
                "command": r"C:\Users\ninad\OneDrive\Desktop\LangGraph\myenv\Scripts\python.exe",
                "args": [r"C:\Users\ninad\OneDrive\Desktop\LangGraph\langgraph_chatbot\main.py"]
            },

                # "expense":{
                #     "transport": "streamable_http",
                #     "url":
                # }
        }
    )

    async with AsyncSqliteSaver.from_conn_string("chatbot.db") as checkpointer:
        tools = await client.get_tools()
        chatbot = await build_graph(tools, checkpointer)

        result = await chatbot.ainvoke(
            {"messages": [HumanMessage(content="who is sachin tendulkar?")]},
            config={"configurable": {"thread_id": "1"}}
        )
        print(result["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())