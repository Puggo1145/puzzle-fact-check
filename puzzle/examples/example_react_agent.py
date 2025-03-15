from typing import Annotated, Sequence, TypedDict, cast
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage, AIMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


from langchain_openai import ChatOpenAI
from langchain_core.tools import tool


model = ChatOpenAI(model="gpt-4o-mini")


@tool
def get_weather(location: str):
    """Call to get the weather from a specific location."""
    # This is a placeholder for the actual implementation
    # Don't let the LLM know this though 😊
    if any([city in location.lower() for city in ["sf", "san francisco"]]):
        return "It's sunny in San Francisco, but you better look out if you're a Gemini 😈."
    else:
        return f"I am not sure what the weather is in {location}"


tools = [get_weather]

model = model.bind_tools(tools)


import json
from langchain_core.runnables import RunnableConfig


tools_by_name = {tool.name: tool for tool in tools}


# Define tool node
def tool_node(state: AgentState):
    outputs = []
    # 找到最近的一条 tool 消息，提取工具调用信息
    for tool_call in cast(AIMessage, state["messages"][-1]).tool_calls:
        # 调用 tool
        tool_result = tools_by_name[tool_call["name"]].invoke(tool_call["args"])
        # 将调用结果返回到 State 上
        outputs.append(
            ToolMessage(
                content=json.dumps(tool_result),
                name=tool_call["name"],
                tool_call_id=tool_call["id"],
            )
        )
    return {"messages": outputs}


def call_model(state: AgentState, config: RunnableConfig):
    system_prompt = SystemMessage(
        "You are a helpful AI assistant, please respond to the users query to the best of your ability!"
    )
    # 确保 System message 始终位于上下文顶层
    messages = [
        system_prompt,
        state["messages"]
    ]
    response = model.invoke(messages, config)
    
    return {"messages": [response]}


# conditional edge
def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = cast(AIMessage, messages[-1])
    # If no tool call, finish
    if not last_message.tool_calls:
        return "end"
    else:
        "continue"
    

from langgraph.graph import StateGraph, END

graph_builder = StateGraph(AgentState)

graph_builder.add_node("agent", call_model)
graph_builder.add_node("tools", tool_node)
graph_builder.add_edge("tools", "agent")

graph_builder.set_entry_point("agent")

graph_builder.add_conditional_edges(
    "agent", # where the condition start
    should_continue, # the fn deciding next move
    {
        "continue": "tools",
        "end": END
    }
)

graph_builder.compile()
