import os
from dotenv import load_dotenv
import chainlit as cl
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from config import DATABASE_NAME, MONGO_URI
from tools.mongodb_tools import tools
from agent import create_agent
from graph import create_workflow, AgentState
from mongodb.connect import get_mongo_client
from mongodb import checkpointer
from motor.motor_asyncio import AsyncIOMotorClient
from langchain_core.messages import HumanMessage, AIMessage
from utilities import sanitize_name
from langchain.schema.runnable import Runnable

# Load environment variables
load_dotenv()

# Connect to MongoDB database
if not MONGO_URI:
    print("MONGO_URI not set in environment variables")

mongo_client = get_mongo_client(MONGO_URI)

if not mongo_client:
    print("Failed to connect to MongoDB. Exiting...")
    exit(1)

@cl.on_chat_start
async def on_chat_start():
    # model = ChatAnthropic(name="chat_anthropic", model="claude-3-5-sonnet-20240620", temperature=0, streaming=True)
    model = ChatOpenAI(name="chat_openai", model="gpt-4o-2024-05-13", temperature=0, streaming=True)

    chatbot_agent = create_agent(
        model,
        tools,
        system_message="You are helpful HR Chatbot Agent.",
    )

    workflow = create_workflow(chatbot_agent, tools)

    mongo_client = AsyncIOMotorClient(MONGO_URI)
    mongodb_checkpointer = checkpointer.MongoDBSaver(mongo_client, DATABASE_NAME, "checkpoints_collection")

    graph = workflow.compile(checkpointer=mongodb_checkpointer)

    state = AgentState(messages=[])

    cl.user_session.set("graph", graph)
    cl.user_session.set("state", state)

@cl.on_message
async def on_message(message: cl.Message):
    try:
        graph: Runnable = cl.user_session.get("graph")
        state = cl.user_session.get("state")

        state["messages"] += [HumanMessage(content=message.content, name=sanitize_name("Human"))]

        ui_message = cl.Message(content="")
        await ui_message.send()
        config = {"configurable": {"thread_id": "20"}}

        async for event in graph.astream_events(state, config, version="v1"):
            if event["event"] == "on_chat_model_stream":
                content = event["data"]["chunk"].content or ""
                await ui_message.stream_token(token=content)
            elif event["event"] == "on_tool_start":
                tool_name = event.get("name", "Unknown Tool")
                tool_input = event["data"].get("input", "No input provided")
                async with cl.Step(name=f"Using Tool: {tool_name}", type="tool") as step:
                    step.input = tool_input


        cl.user_session.set("state", state)
        await ui_message.update()
    except Exception as e:
        print(f"An error occurred: {e}")
        await cl.Message(content="I'm sorry, but an error occurred. Please try again.").send()