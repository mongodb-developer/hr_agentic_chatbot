from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langgraph.graph import END, StateGraph
from utilities import sanitize_name
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.messages import BaseMessage
from typing import Annotated, Sequence, TypedDict
import functools
import operator


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    sender: str


def agent_node(state, config, agent, name):
    result = agent.invoke(state, config)
    if isinstance(result, ToolMessage):
        result.name = sanitize_name(result.name)
    else:
        result = AIMessage(**result.dict(exclude={"type", "name"}), name=sanitize_name(name))
    return {
        "messages": [result],
        "sender": sanitize_name(name),
    }

def create_workflow(chatbot_agent, tools):
    chatbot_node = functools.partial(agent_node, agent=chatbot_agent, name="HR Chatbot")
    tool_node = ToolNode(tools, name="tools")

    workflow = StateGraph(AgentState)

    workflow.add_node("chatbot", chatbot_node)
    workflow.add_node("tools", tool_node)

    workflow.set_entry_point("chatbot")
    workflow.add_conditional_edges(
        "chatbot",
        tools_condition,
        {"tools": "tools", END: END}
    )

    workflow.add_edge("tools", "chatbot")

    return workflow