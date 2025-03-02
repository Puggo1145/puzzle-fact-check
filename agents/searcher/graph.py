import json
from typing import cast, List
from langchain_core.messages import ToolCall
from langchain_core.utils.function_calling import convert_to_openai_tool
from utils import count_tokens
from .states import SearchAgentState, Status
from .prompts import (
    system_prompt_template,
    evaluate_current_status_prompt_template,
    evaluate_current_status_output_parser,
    generate_answer_prompt_template,
    generate_answer_output_parser,
)
from langchain_openai import ChatOpenAI
from tools import (
    SearchBingTool,
    SearchGoogleTool,
    ReadWebpageTool,
    get_current_time,
)
from langgraph.graph.state import StateGraph, START, END
from .callback import AgentStateCallback



class SearchAgentGraph:
    """搜索代理图类"""
    
    def __init__(
        self,
        model: ChatOpenAI,
        max_tokens: int
    ):
        """
        初始化 search agent graph
        
        Args:
            config: 配置参数，包含max_tokens、model等
        """
        # params initialization
        self.model = model
        self.max_tokens = max_tokens
        
        self.tools = [
            SearchBingTool(),
            SearchGoogleTool(),
            ReadWebpageTool(),
            get_current_time,
        ]
        self.tools_by_name = {tool.name: tool for tool in self.tools}
        self.tool_calling_schema = [convert_to_openai_tool(tool) for tool in self.tools]
        
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """构建搜索代理图"""
        graph_builder = StateGraph(SearchAgentState)
        
        graph_builder.add_node("evaluate_current_status", self.evaluate_current_status)
        graph_builder.add_node("tools", self.tool_node)
        graph_builder.add_node("generate_answer", self.generate_answer)
        
        # 检查 token 是否超出
        graph_builder.add_conditional_edges(
            START,
            self.doesTokensExceeded,
            {True: "generate_answer", False: "evaluate_current_status"},
        )
        
        # 模型是否要输出回答
        graph_builder.add_conditional_edges(
            "evaluate_current_status",
            self.does_llm_generate_answer,
            {"tools": "tools", "generate_answer": "generate_answer"},
        )
        
        graph_builder.add_edge("tools", "evaluate_current_status")
        graph_builder.add_edge("generate_answer", END)
        
        # 编译图
        return graph_builder.compile()
    
    def invoke(self, initial_state: SearchAgentState):
        return self.graph.invoke(
            initial_state,
            config={ 
                "callbacks": [AgentStateCallback(verbose=True)] 
            }
        )
    
    # nodes
    def doesTokensExceeded(self, state: SearchAgentState):
        """检查是否超过最大token限制"""
        return state.token_usage >= self.max_tokens
    
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
    
    def evaluate_current_status(self, state: SearchAgentState):
        """评估当前状态并决定下一步行动"""
        # 检查是否陷入循环
        if self._is_in_loop(state):
            # 强制改变搜索策略或生成回答
            forced_status = Status(
                evaluation="搜索陷入循环，需要改变搜索策略或基于当前信息生成回答。",
                memory="搜索过程陷入循环，多次执行相同的搜索查询。",
                next_step="基于已收集的信息生成最终回答",
                action="answer",
            )

            state.statuses.append(forced_status)

            return {"statuses": state.statuses}

        system_prompt = system_prompt_template.format(
            news_metadata=state.news_metadata,
            content=state.content,
            purpose=state.purpose,
            expected_results=state.expected_results,
            tools_schema=self.tool_calling_schema,
        )

        evaluate_current_status_prompt = evaluate_current_status_prompt_template.format(
            retrieved_information=state.latest_tool_messages,
            statuses=state.statuses,
            supporting_evidence=state.supporting_evidence,
        )
        messages = [system_prompt, evaluate_current_status_prompt]

        response = self.model.invoke(input=messages)

        # 计算 token 消耗
        state.token_usage += count_tokens(messages + [response])

        new_status = evaluate_current_status_output_parser.parse(str(response.content))
        state.statuses.append(new_status)

        # 处理新的证据
        if hasattr(new_status, "new_evidence") and new_status.new_evidence:
            for evidence in new_status.new_evidence:
                state.supporting_evidence.append(evidence)

        return {
            "statuses": state.statuses,
            "supporting_evidence": state.supporting_evidence,
            "token_usage": state.token_usage
        }
    
    def generate_answer(self, state: SearchAgentState):
        """生成最终答案"""
        system_prompt = system_prompt_template.format(
            news_metadata=state.news_metadata,
            content=state.content,
            purpose=state.purpose,
            expected_results=state.expected_results,
            tools_schema=self.tool_calling_schema,
        )

        generate_answer_prompt = generate_answer_prompt_template.format(
            retrieved_information=state.latest_tool_messages,
            statuses=state.statuses,
            supporting_evidence=state.supporting_evidence,
        )
        messages = [system_prompt, generate_answer_prompt]

        response = self.model.invoke(input=messages)
        answer = generate_answer_output_parser.parse(str(response.content))

        state.token_usage += count_tokens(messages + [response])

        return {
            "result": answer,
            "token_usage": state.token_usage
        }
    
    def tool_node(self, state: SearchAgentState):
        """执行工具调用"""
        # 找到最近的一条 action 消息，提取工具调用信息
        tool_calls = cast(List[ToolCall], cast(Status, state.statuses[-1]).action)

        tool_calling_results: List[str] = []
        for tool_call in tool_calls:
            # 调用 tool
            tool_result = self.tools_by_name[tool_call["name"]].invoke(tool_call["args"])

            # 确保工具结果是字符串格式
            if not isinstance(tool_result, str):
                # 如果是复杂对象，转换为格式化的JSON字符串
                tool_result = json.dumps(tool_result, ensure_ascii=False, indent=2)

            # 创建简洁明了的结果格式
            formatted_result = f"工具名称: {tool_call['name']}\n结果内容:\n{tool_result}"
            tool_calling_results.append(formatted_result)

        return {"latest_tool_messages": tool_calling_results}
    
    def does_llm_generate_answer(self, state: SearchAgentState):
        """决定是否继续执行工具调用或生成回答"""
        last_action = cast(Status, state.statuses[-1]).action
        if last_action == "answer":
            return "generate_answer"
        else:
            return "tools"
    
