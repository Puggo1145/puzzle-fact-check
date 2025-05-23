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
from tools import (
    get_current_time,
    SearchBingTool,
    SearchGoogleOfficial,
    SearchGoogleAlternative,
    ReadWebpageTool,
    TavilySearch,
    SearchBaiduTool,
    ReadPDFTool,
)
from langgraph.graph.state import StateGraph

from typing import cast, List, Dict, Any
from langchain_core.messages import ToolCall
from langchain_openai.chat_models.base import BaseChatOpenAI

class SearchAgentGraph(BaseAgent):
    """
    Search Agent: 负责执行具体的检索计划
        
    Args:
        max_search_tokens：子 agent 检索时允许消耗的最大 token 数
        selected_tools: 从前端传入的工具选择配置
    """
    def __init__(
        self,
        model: BaseChatOpenAI,
        max_search_tokens: int,
        selected_tools: List[str] = [],
    ):
        super().__init__(model=model)

        self.max_search_tokens = max_search_tokens
        self.token_usage = 0
        
        # 定义所有可用工具
        self.available_tools = {
            "basic": [
                get_current_time,
                # SearchBingTool(),
                SearchBaiduTool(),
                SearchGoogleOfficial(),
                SearchGoogleAlternative(),
                ReadWebpageTool(),
                ReadPDFTool(),
            ],
            "tavily_search": [
                TavilySearch()
            ],
            # 其他工具将来在这里添加
            # "browser_use": [],
            # "vision": [],
        }
        
        # 初始化工具列表
        self.tools = self._get_tools(selected_tools)
        self.tools_by_name = {tool.name: tool for tool in self.tools}
        self.tool_calling_schema = [convert_to_openai_tool(tool) for tool in self.tools]
        
    def _get_tools(self, selected_tools: List[str] = []) -> List[Any]:
        """
        根据选择的工具配置返回工具列表
        
        Args:
            selected_tools: 从前端传入的工具选择列表，如 ["tavily_search"]
            
        Returns:
            所有应该启用的工具列表
        """
        tools = []
        
        # 总是添加基本工具
        tools.extend(self.available_tools["basic"])
        
        # 根据选择添加额外工具
        if selected_tools:
            for tool_name in selected_tools:
                if tool_name in self.available_tools:
                    tools.extend(self.available_tools[tool_name])
        
        return tools
        
    def _build_graph(self):
        graph_builder = StateGraph(SearchAgentState)
        
        graph_builder.add_node("check_token_usage", self.check_token_usage)
        graph_builder.add_node("evaluate_current_status", self.evaluate_current_status)
        graph_builder.add_node("tools", self.tool_node)
        graph_builder.add_node("generate_answer", self.generate_answer)

        graph_builder.set_entry_point("check_token_usage")
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
    
    def check_token_usage(self, state: SearchAgentState):
        """检查 token 是否超出最大窗口"""
        # 超出最大 token 窗口，强制进行回答
        if self.token_usage >= self.max_search_tokens:
            forced_answer_status = Status(
                evaluation="检索 token 超出最大可用 token，强制基于当前信息开始回答",
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

        # 检查最近的3个状态是否都是相同的搜索工具和查询
        tool_query_pairs = []
        for status in recent_statuses:
            if isinstance(status.action, dict):
                tool_call = status.action
                tool_name = tool_call.get("name")
                if tool_name in [
                    "search_google_official",
                    "search_google_alternative",
                    "search_bing",
                    "search_wikipedia",
                    "search_baidu",
                ]:
                    query = tool_call.get("args", {}).get("query", "")
                    tool_query_pairs.append((tool_name, query))

        # 如果有3个相同的(工具,查询)对，则认为陷入了循环
        return len(tool_query_pairs) == 3 and len(set(tool_query_pairs)) == 1
    
    # nodes
    def evaluate_current_status(self, state: SearchAgentState):
        """模型自我评估当前状态并决定下一步行动"""

        # 如果搜索陷入循环，强制结束并生成回答
        if self._is_in_loop(state):
            forced_status = Status(
                evaluation="搜索陷入循环",
                next_step="基于已收集的信息给出检索结论",
                action="answer",
            )

            return {"statuses": [forced_status]}

        search_method_prompt = search_method_prompt_template.format(
            basic_metadata=state.basic_metadata.serialize_for_llm(),
            content=state.content,
            purpose=state.purpose,
            expected_source=state.expected_source,
            tools_schema=self.tool_calling_schema,
        )

        evaluate_current_status_prompt = evaluate_current_status_prompt_template.format(
            retrieved_information=state.latest_tool_result,
            statuses=state.statuses,
            evidences=state.evidences,
        )
        messages = [search_method_prompt, evaluate_current_status_prompt]

        response = self.model.invoke(input=messages)
        self.token_usage += count_tokens(messages + [response])
        
        new_status: Status = evaluate_current_status_output_parser.parse(str(response.content))
        
        updated_state: Dict[str, Any] = {"statuses": [new_status]}
        if new_status.new_evidence:
            updated_state["evidences"] = new_status.new_evidence
        
        return updated_state
    
    def tool_node(self, state: SearchAgentState):
        """执行工具调用"""
        # 找到最近的一条 action 消息，提取工具调用信息
        tool_call = cast(ToolCall, state.statuses[-1].action)

        tool_calling_result: str = ""
        try:
            # 调用 tool
            tool_result = self.tools_by_name[tool_call["name"]].invoke(tool_call["args"])
            
            # 确保工具结果是字符串格式
            if not isinstance(tool_result, str):
                # 如果是复杂对象，转换为格式化的JSON字符串
                tool_result = json.dumps(tool_result, ensure_ascii=False, indent=2)
            
            # 创建简洁明了的结果格式
            formatted_result = f"工具名称: {tool_call['name']}\n调用结果:\n{tool_result}"
            tool_calling_result = formatted_result
        
        except Exception as e:
            # 添加错误信息到结果
            error_result = f"工具名称: {tool_call['name']}\n错误:\n{str(e)}"
            tool_calling_result = error_result

        return {"latest_tool_result": tool_calling_result}
    
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
            expected_source=state.expected_source,
            statuses=state.statuses,
            evidences=state.evidences,
        )
        messages = [generate_answer_prompt]

        response = self.model.invoke(input=messages)
        answer: SearchResult = generate_answer_output_parser.parse(str(response.content))

        # self.token_usage += count_tokens(messages + [response])
        self.token_usage = 0
        
        return {"result": answer}
