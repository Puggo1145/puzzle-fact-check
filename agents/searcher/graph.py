import json
import tiktoken
from typing import cast, List
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import ToolCall, BaseMessage
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool
from utils import check_env
from .states import SearchAgentState, Status
from .prompts import (
    system_prompt_template,
    evaluate_current_status_prompt_template,
    evaluate_current_status_output_parser,
    generate_answer_prompt_template,
    generate_answer_output_parser,
)
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from tools import (
    SearchBingTool,
    SearchGoogleTool,
    SearchWikipediaTool,
    ReadWebpageTool,
    get_current_time,
)
from langgraph.graph.state import StateGraph, END


tools: list[BaseTool] = [
    SearchBingTool(),
    SearchGoogleTool(),
    # SearchWikipediaTool(),
    ReadWebpageTool(),
    get_current_time,
]

# 使用专用函数生成工具描述
tool_calling_schema = [
    convert_to_openai_tool(tool)
    for tool in tools
]

# model = ChatOpenAI(model="gpt-4o-mini", temperature=1) # 这几波玩意会原地卡死
# model = ChatDeepSeek(model="deepseek-chat", temperature=0.5)
model = ChatOpenAI(
    model="qwen-plus",
    temperature=0.3,
    api_key=check_env("ALI_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 初始化tokenizer
tokenizer = tiktoken.get_encoding("cl100k_base")

def count_tokens(messages: List[BaseMessage]) -> int:
    """计算消息列表的token数量"""
    # 将消息转换为字符串
    message_texts = []
    for message in messages:
        if hasattr(message, "content") and isinstance(message.content, str):
            message_texts.append(message.content)
        else:
            # 如果消息内容不是字符串，尝试转换为JSON字符串
            try:
                message_texts.append(json.dumps(message.content))
            except:
                message_texts.append(str(message.content))
    
    # 合并所有文本
    combined_text = " ".join(message_texts)
    
    # 计算token数量
    tokens = tokenizer.encode(combined_text)
    return len(tokens)

# Nodes
def evaluate_current_status(state: SearchAgentState, config: RunnableConfig):
    """
    Let Model evaluate and reflect on the result of the previous step
    based on the purpose and expected results of the task.
    Make sure it is aligned with the goal
    """
    # 只保留token检查
    if state.total_tokens >= state.max_tokens:
        # 强制生成回答
        forced_status = Status(
            evaluation=f"已达到最大token限制({state.max_tokens})，需要基于当前信息生成回答。",
            memory="搜索过程已达到最大token限制。",
            next_step="基于已收集的信息生成最终回答。",
            action="answer"
        )
        
        state.statuses.append(forced_status)
        
        return {"statuses": state.statuses, "total_tokens": state.total_tokens}
    
    # 检查是否陷入循环
    if _is_in_loop(state):
        # 强制改变搜索策略或生成回答
        forced_status = Status(
            evaluation="检测到搜索陷入循环，需要改变搜索策略或基于当前信息生成回答。",
            memory="搜索过程陷入循环，多次执行相同的搜索查询。",
            next_step="基于已收集的信息生成最终回答",
            action="answer"
        )
        
        state.statuses.append(forced_status)
        
        return {"statuses": state.statuses, "total_tokens": state.total_tokens}
    
    system_prompt = system_prompt_template.format(
        news_metadata=state.news_metadata,
        content=state.content,
        purpose=state.purpose,
        expected_results=state.expected_results,
        tools_schema=tool_calling_schema
    )
    
    evaluate_current_status_prompt = evaluate_current_status_prompt_template.format(
        retrieved_information=state.latest_tool_messages,
        statuses=state.statuses,
        total_tokens=state.total_tokens,
        max_tokens=state.max_tokens,
        supporting_evidence=state.supporting_evidence
    )
    messages = [
        system_prompt, 
        evaluate_current_status_prompt
    ]

    # 计算本次请求的token数量并累加
    tokens_this_request = count_tokens(messages)
    state.total_tokens += tokens_this_request
    
    response = model.invoke(input=messages, config=config)
    
    # 计算响应的token数量并累加
    response_tokens = count_tokens([response])
    state.total_tokens += response_tokens
    
    new_status = evaluate_current_status_output_parser.parse(str(response.content))
    state.statuses.append(new_status)
    
    # 处理新的证据
    if hasattr(new_status, "new_evidence") and new_status.new_evidence:
        for evidence in new_status.new_evidence:
            state.supporting_evidence.append(evidence)
    
    return {"statuses": state.statuses, "total_tokens": state.total_tokens, "supporting_evidence": state.supporting_evidence}


def _is_in_loop(state: SearchAgentState) -> bool:
    """
    检测是否陷入搜索循环
    """
    # 如果状态数量少于3，不可能陷入循环
    if len(state.statuses) < 3:
        return False
    
    # 获取最近的3个状态
    recent_statuses = state.statuses[-3:]
    
    # 检查最近的3个状态是否都是相同的搜索查询
    queries = []
    for status in recent_statuses:
        if isinstance(status.action, list) and len(status.action) > 0:
            tool_call = status.action[0]
            if tool_call.get("name") in ["search_google", "search_bing", "search_wikipedia"]:
                query = tool_call.get("args", {}).get("query", "")
                queries.append(query)
    
    # 如果有3个查询，并且它们都相同，则认为陷入了循环
    return len(queries) == 3 and len(set(queries)) == 1


def generate_answer(state: SearchAgentState, config: RunnableConfig):
    """
    Generate the final answer based on all the information collected
    """
    system_prompt = system_prompt_template.format(
        news_metadata=state.news_metadata,
        content=state.content,
        purpose=state.purpose,
        expected_results=state.expected_results,
        tools_schema=tool_calling_schema
    )
    
    # 格式化证据列表以便在提示中使用
    evidence_text = ""
    for i, evidence in enumerate(state.supporting_evidence):
        evidence_text += f"{i+1}. 内容: {evidence.content}\n   来源: {evidence.source}\n   相关性: {evidence.relevance}\n\n"
    
    generate_answer_prompt = generate_answer_prompt_template.format(
        retrieved_information=state.latest_tool_messages,
        statuses=state.statuses,
        supporting_evidence=evidence_text
    )
    messages = [
        system_prompt, 
        generate_answer_prompt
    ]

    # 计算本次请求的token数量并累加
    tokens_this_request = count_tokens(messages)
    state.total_tokens += tokens_this_request
    
    response = model.invoke(input=messages, config=config)
    
    # 计算响应的token数量并累加
    response_tokens = count_tokens([response])
    state.total_tokens += response_tokens
    
    # 解析回答
    answer = generate_answer_output_parser.parse(str(response.content))
    
    # 返回最终结果和token统计
    return {"result": answer, "total_tokens": state.total_tokens, "supporting_evidence": state.supporting_evidence}


tools_by_name = {
    tool.name: tool for tool in tools
}


def tool_node(state: SearchAgentState):
    """Tools for search agent"""
    # 找到最近的一条 action 消息，提取工具调用信息
    tool_calls = cast(List[ToolCall], cast(Status, state.statuses[-1]).action)

    tool_calling_results: List[str] = []
    for tool_call in tool_calls:
        # 调用 tool
        tool_result = tools_by_name[tool_call["name"]].invoke(tool_call["args"])
        
        # 确保工具结果是字符串格式
        if not isinstance(tool_result, str):
            # 如果是复杂对象，转换为格式化的JSON字符串
            tool_result = json.dumps(tool_result, ensure_ascii=False, indent=2)
        
        # 创建简洁明了的结果格式
        formatted_result = f"工具名称: {tool_call['name']}\n结果内容:\n{tool_result}"
        tool_calling_results.append(formatted_result)
        
    return {"latest_tool_messages": tool_calling_results}


def should_continue(state: SearchAgentState):
    """
    决定是否继续执行工具调用或生成回答
    """
    last_action = cast(Status, state.statuses[-1]).action
    if last_action == "answer":
        return "generate_answer"
    else:
        return "tools"


# Graph
graph_builder = StateGraph(SearchAgentState)
graph_builder.add_node("evaluate_current_status", evaluate_current_status)
graph_builder.add_node("tools", tool_node)
graph_builder.add_node("generate_answer", generate_answer)

# 设置入口点
graph_builder.set_entry_point("evaluate_current_status")

# 修改图的流程，先检查是否应该生成回答
graph_builder.add_conditional_edges(
    "evaluate_current_status",
    should_continue,
    {
        "tools": "tools",
        "generate_answer": "generate_answer"
    }
)

# 从工具节点回到评估节点
graph_builder.add_edge("tools", "evaluate_current_status")

# 生成回答后结束
graph_builder.add_edge("generate_answer", END)

search_agent = graph_builder.compile()
