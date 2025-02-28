import json
from typing import cast
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, ToolMessage
from .states import SearchAgentState, Status
from .prompts import (
    system_prompt_template,
    evaluate_current_status_prompt_template,
    evaluate_current_status_output_parser,
)
from langchain_openai import ChatOpenAI
from tools import (
    SearchBingTool,
    SearchGoogleTool,
    SearchWikipediaTool,
    ReadWebpageTool,
    get_current_time,
)
from langgraph.graph.state import StateGraph, END


tools = [
    SearchBingTool,
    SearchGoogleTool,
    SearchWikipediaTool,
    ReadWebpageTool,
    get_current_time,
]

model = ChatOpenAI(model="gpt-4o-mini", temperature=0.3).bind_tools(tools)


# Nodes
def evaluate_current_status(state: SearchAgentState, config: RunnableConfig):
    """
    Let Model evaluate and reflect on the result of the previous step
    based on the purpose and expected results of the task.
    Make sure it is aligned with the goal
    """
    system_prompt = system_prompt_template.format(
        content=state.content,
        purpose=state.purpose,
        expected_results=state.expected_result,
    )
    evaluate_current_status_prompt = evaluate_current_status_prompt_template.format(
        retrieved_information=state.latest_tool_messages, 
        statuses=state.statuses
    )
    messages = [system_prompt, evaluate_current_status_prompt]

    response = model.invoke(input=messages, config=config)
    new_status = evaluate_current_status_output_parser.parse(str(response.content))

    return {"statuses": new_status}


tools_by_name = {tool.name: tool for tool in tools}


def tool_node(state: SearchAgentState):
    """Tools for search agent"""
    # 找到最近的一条 action 消息，提取工具调用信息
    tool_calls = cast(AIMessage, cast(Status, state.statuses[-1]).action).tool_calls

    tool_calling_results = []
    for tool_call in tool_calls:
        # 调用 tool
        tool_result = tools_by_name[tool_call["name"]].invoke(tool_call["args"])
        # 将调用结果返回到 State 上
        tool_calling_results.append(
            ToolMessage(
                content=json.dumps(tool_result),
                name=tool_call["name"],
                tool_call_id=tool_call["id"],
            )
        )

    return {"latest_tool_messages": tool_calling_results}


def should_yield_answer(state: SearchAgentState):
    last_action = cast(Status, state.statuses[-1]).action
    if last_action is "answer":
        return "generate_answer"
    else:
        return "continue"


# Graph
graph_builder = StateGraph(SearchAgentState)
graph_builder.add_node("evaluate_current_status", evaluate_current_status)
graph_builder.add_node("tools", tool_node)
graph_builder.add_edge("evaluate_current_status", "tools")

graph_builder.set_entry_point("evaluate_current_status")

graph_builder.add_conditional_edges(
    "evaluate_current_status",
    should_yield_answer,
    {
        "continue": "tools",
        "generate_answer": END
    }
)

search_agent = graph_builder.compile()
