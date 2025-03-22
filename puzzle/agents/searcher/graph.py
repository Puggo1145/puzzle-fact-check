import json
from agents.base import BaseAgent
from langchain_core.utils.function_calling import convert_to_openai_tool
from utils import count_tokens
from .states import SearchAgentState, Status, SearchResult
from .prompts import (
    search_method_prompt_template,
    evaluate_current_status_prompt_template,
    evaluate_current_status_output_parser,
    generate_answer_prompt_template,
    generate_answer_output_parser,
)
from models import ChatQwen
from tools import (
    SearchBingTool,
    SearchGoogleTool,
    ReadWebpageTool,
    get_current_time,
    TavilySearch
)
from langgraph.graph.state import StateGraph
from .events import SearchAgentEvents, CLIModeEvents, DBEvents
from pubsub import pub

from typing import cast, List, Literal, Dict, Any
from langchain_core.messages import ToolCall


class SearchAgentGraph(BaseAgent[ChatQwen]):
    """
    Search Agent: 负责执行具体的检索计划
        
    Args:
        max_tokens：子 agent 检索时允许消耗的最大 token 数
    """
    def __init__(
        self,
        model: ChatQwen,
        max_search_tokens: int,
        mode: Literal["CLI", "API"] = "CLI",
    ):
        super().__init__(
            mode=mode,
            model=model,
        )

        self.max_search_tokens = max_search_tokens
        self.token_usage = 0
        
        self.tools = [
            SearchBingTool(),
            SearchGoogleTool(),
            TavilySearch(),
            ReadWebpageTool(),
            get_current_time,
        ]
        self.tools_by_name = {tool.name: tool for tool in self.tools}
        self.tool_calling_schema = [convert_to_openai_tool(tool) for tool in self.tools]
        
        self.db_events = DBEvents()
        if mode == "CLI":
            self.cli_events = CLIModeEvents()
        
    def _build_graph(self):
        graph_builder = StateGraph(SearchAgentState)
        
        graph_builder.add_node("initialization", self.initialization)
        graph_builder.add_node("check_token_usage", self.check_token_usage)
        graph_builder.add_node("evaluate_current_status", self.evaluate_current_status)
        graph_builder.add_node("tools", self.tool_node)
        graph_builder.add_node("generate_answer", self.generate_answer)

        graph_builder.set_entry_point("initialization")
        graph_builder.add_edge("initialization", "check_token_usage")
        graph_builder.add_conditional_edges(
            "check_token_usage",
            self._route_based_on_token_usage,
            {
                "exceeded": "generate_answer",
                "not_exceeded": "evaluate_current_status"
            }
        )
        graph_builder.add_conditional_edges(
            "evaluate_current_status",
            self._does_llm_generate_answer,
            {"tools": "tools", "generate_answer": "generate_answer"},
        )
        graph_builder.add_edge("tools", "check_token_usage") # 工具调用后再次检查token
        graph_builder.set_finish_point("generate_answer")
        
        return graph_builder.compile()
    
    def initialization(self, state: SearchAgentState):
        """初始化搜索代理"""
        pub.sendMessage(
            SearchAgentEvents.STORE_CHECK_POINT.value,
            content=state.content,
            purpose=state.purpose,
            expected_sources=state.expected_sources,
        )
        pub.sendMessage(
            SearchAgentEvents.PRINT_SEARCH_AGENT_START.value,
            content=state.content,
            purpose=state.purpose,
            expected_sources=state.expected_sources,
        )
        
        return state
    
    def check_token_usage(self, state: SearchAgentState):
        """检查 token 是否超出最大窗口"""
        pub.sendMessage(
            SearchAgentEvents.PRINT_TOKEN_USAGE.value,
            current_tokens=self.token_usage
        )
        
        # 超出最大 token 窗口，强制进行回答
        if self.token_usage >= self.max_search_tokens:
            forced_answer_status = Status(
                evaluation="检索 token 超出最大可用 token，强制基于当前信息开始回答",
                memory="检索消耗的 token 超出最大可用 token",
                next_step="基于已收集的信息生成最终回答",
                action="answer",
            )
            return {"statuses": [forced_answer_status]}
        # 没有超出，继续检索
        else:
            return state
    
    def _route_based_on_token_usage(self, state: SearchAgentState):
        """根据 token 消耗结果决策的 router"""

        # token 消耗超出限制，强制回答
        if self.token_usage >= self.max_search_tokens:
            return "exceeded"
        else:
            return "not_exceeded"
    
    def _is_in_loop(self, state: SearchAgentState) -> bool:
        """检测是否陷入搜索循环"""
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
                if tool_call.get("name") in [
                    "search_google",
                    "search_bing",
                    "search_wikipedia",
                ]:
                    query = tool_call.get("args", {}).get("query", "")
                    queries.append(query)

        # 如果有3个相同的查询，则认为陷入了循环
        return len(queries) == 3 and len(set(queries)) == 1
    
    # nodes
    def evaluate_current_status(self, state: SearchAgentState):
        """模型自我评估当前状态并决定下一步行动"""

        # 如果搜索陷入循环，强制结束并生成回答
        if self._is_in_loop(state):
            forced_status = Status(
                evaluation="搜索陷入循环，需要改变搜索策略或基于当前信息生成回答。",
                memory="搜索过程陷入循环，多次执行相同的搜索查询。",
                next_step="基于已收集的信息生成最终回答",
                action="answer",
            )

            return {"statuses": [forced_status]}

        search_method_prompt = search_method_prompt_template.format(
            basic_metadata=state.basic_metadata.serialize_for_llm(),
            content=state.content,
            purpose=state.purpose,
            expected_sources=state.expected_sources,
            tools_schema=self.tool_calling_schema,
        )

        evaluate_current_status_prompt = evaluate_current_status_prompt_template.format(
            retrieved_information=state.latest_tool_messages,
            statuses=state.statuses,
            evidences=state.evidences,
        )
        messages = [search_method_prompt, evaluate_current_status_prompt]

        # 发送LLM开始评估状态的事件
        pub.sendMessage(
            SearchAgentEvents.PRINT_EVALUATE_STATUS_START.value,
            model_name=self.model.model_name
        )

        response = self.model.invoke(input=messages)
        self.token_usage += count_tokens(messages + [response])
        
        new_status: Status = evaluate_current_status_output_parser.parse(str(response.content))
        
        # 发送LLM评估状态结束的事件
        pub.sendMessage(
            SearchAgentEvents.PRINT_STATUS_EVALUATION_END.value,
            status=new_status
        )
        
        updated_state: Dict[str, Any] = {"statuses": [new_status]}
        if new_status.new_evidence:
            updated_state["evidences"] = new_status.new_evidence
            # 存储搜索证据到数据库
            pub.sendMessage(
                SearchAgentEvents.STORE_SEARCH_EVIDENCES.value,
                evidences=new_status.new_evidence
            )
        
        # 发送token使用情况事件
        pub.sendMessage(
            SearchAgentEvents.PRINT_TOKEN_USAGE.value,
            current_tokens=self.token_usage
        )
        
        return updated_state
    
    def tool_node(self, state: SearchAgentState):
        """执行工具调用"""
        # 找到最近的一条 action 消息，提取工具调用信息
        tool_calls = cast(List[ToolCall], cast(Status, state.statuses[-1]).action)

        tool_calling_results: List[str] = []
        for tool_call in tool_calls:
            # 发送工具开始执行事件
            pub.sendMessage(
                SearchAgentEvents.PRINT_TOOL_START.value,
                tool_name=tool_call["name"],
                input_str=json.dumps(tool_call["args"], ensure_ascii=False)
            )
            
            try:
                # 调用 tool
                tool_result = self.tools_by_name[tool_call["name"]].invoke(tool_call["args"])
                
                pub.sendMessage(
                    SearchAgentEvents.PRINT_TOOL_RESULT.value,
                    output=tool_result
                )
                
                # 确保工具结果是字符串格式
                if not isinstance(tool_result, str):
                    # 如果是复杂对象，转换为格式化的JSON字符串
                    tool_result = json.dumps(tool_result, ensure_ascii=False, indent=2)
                
                # 创建简洁明了的结果格式
                formatted_result = f"工具名称: {tool_call['name']}\n调用结果:\n{tool_result}"
                tool_calling_results.append(formatted_result)
            
            except Exception as e:
                # 添加错误信息到结果
                error_result = f"工具名称: {tool_call['name']}\n错误:\n{str(e)}"
                pub.sendMessage(
                    SearchAgentEvents.PRINT_TOOL_ERROR.value,
                    error=error_result
                )
                tool_calling_results.append(error_result)

        return {"latest_tool_messages": tool_calling_results}
    
    def _does_llm_generate_answer(self, state: SearchAgentState):
        """决定是否继续执行工具调用或生成回答"""
        last_action = cast(Status, state.statuses[-1]).action
        if last_action == "answer":
            return "generate_answer"
        else:
            return "tools"
    
    def generate_answer(self, state: SearchAgentState):
        """生成最终答案"""
        generate_answer_prompt = generate_answer_prompt_template.format(
            basic_metadata=state.basic_metadata.serialize_for_llm(),
            content=state.content,
            purpose=state.purpose,
            expected_sources=state.expected_sources,
            statuses=state.statuses,
            evidences=state.evidences,
        )
        messages = [generate_answer_prompt]

        # 发送LLM开始生成答案的事件
        pub.sendMessage(
            SearchAgentEvents.PRINT_GENERATE_ANSWER_START.value,
            model_name=self.model.model_name
        )

        response = self.model.invoke(input=messages)
        answer: SearchResult = generate_answer_output_parser.parse(str(response.content))

        self.token_usage += count_tokens(messages + [response])
        
        pub.sendMessage(
            SearchAgentEvents.PRINT_GENERATE_ANSWER_END.value,
            result=answer
        )
        pub.sendMessage(
            SearchAgentEvents.STORE_SEARCH_RESULT.value,
            result=answer
        )
        pub.sendMessage(
            SearchAgentEvents.PRINT_TOKEN_USAGE.value,
            current_tokens=self.token_usage
        )
        
        return {"result": answer}
