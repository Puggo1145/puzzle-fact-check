import json
from typing import cast, Callable, Optional

import uuid
from agents.main.graph import MainAgent
from langchain_openai.chat_models.base import BaseChatOpenAI
from langchain_core.messages import ToolMessage
from .model import CreateAgentConfig
from .events import *
from agents.searcher.states import SearchAgentState

# from langchain_core.runnables.schema import StreamEvent


def get_model_instance_from_provider(
    provider: str, model: str, temperature: float = 0.0, streaming: bool = True
) -> BaseChatOpenAI:
    """根据模型提供商获取模型，并注入从环境加载的API密钥"""
    from models import ChatQwen
    from langchain_openai import ChatOpenAI
    from langchain_deepseek import ChatDeepSeek

    if provider == "openai":
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            streaming=streaming,
        )
    elif provider == "qwen":
        return ChatQwen(
            model=model,
            temperature=temperature,
            streaming=streaming,
        )
    elif provider == "deepseek":
        return ChatDeepSeek(
            model=model,
            temperature=temperature,
            streaming=streaming,
        )
    else:
        raise ValueError(f"不支持的模型提供商: {provider}")


def filter_graph_events(kind: str, name: str, node: str, metadata: dict) -> bool:
    kind_filter = [
        "on_chat_model_stream", 
        "on_chain_stream",
        "on_parser_start",
    ]
    name_filter = [
        "LangGraph", 
        "_write", 
        "ChannelWrite", 
        "RunnableSequence",
    ]

    """过滤掉无关的节点事件"""
    if kind in kind_filter:
        return True
    elif name in name_filter or name.startswith("ChannelWrite"):
        return True

    return False


def pretier_print_event(sse_event: BaseEvent):
    print(f"event: {sse_event.event}")
    print(f"data: {sse_event.data}")
    print("-" * 100)

async def run_main_agent(
    news_text: str, 
    config: CreateAgentConfig, 
    thread_id: str,
):
    model = get_model_instance_from_provider(
        config.main_agent.model_provider,
        config.main_agent.model_name,
        config.main_agent.temperature,
        config.main_agent.streaming,
    )
    metadata_extractor_model = get_model_instance_from_provider(
        config.metadata_extractor.model_provider,
        config.metadata_extractor.model_name,
        config.metadata_extractor.temperature,
        config.metadata_extractor.streaming,
    )
    searcher_model = get_model_instance_from_provider(
        config.searcher.model_provider,
        config.searcher.model_name,
        config.searcher.temperature,
        config.searcher.streaming,
    )

    main_agent = MainAgent(
        model=model,
        metadata_extract_model=metadata_extractor_model,
        search_model=searcher_model,
        max_retries=config.main_agent.max_retries,
        max_search_tokens=config.searcher.max_search_tokens,
        selected_tools=config.searcher.selected_tools,
    )

    try:
        async for event in main_agent.graph.astream_events(
            input={"news_text": news_text},
            config={"configurable": {"thread_id": thread_id}},
            version="v2",
        ):
            kind = event.get("event")
            data = event.get("data")
            name = event.get("name")
            metadata = event.get("metadata", {})
            node = metadata.get("checkpoint_ns", "").split(":")[0]

            if filter_graph_events(kind, name, node, metadata):
                continue

            sse_event = None
            
            if (
                kind == "on_chain_start"
                and node == "invoke_metadata_extract_agent"
                and name == "extract_basic_metadata"
            ):
                yield ExtractBasicMetadataStart().model_dump()
            elif (
                kind == "on_chain_end"
                and node == "invoke_metadata_extract_agent"
                and name == "extract_basic_metadata"
            ):
                basic_metadata = data.get("output", {})["basic_metadata"]
                yield ExtractBasicMetadataEnd(data=basic_metadata).model_dump()
            elif (
                kind == "on_chain_start"
                and node == "invoke_metadata_extract_agent"
                and name == "extract_knowledge"
            ):
                yield ExtractKnowledgeStart().model_dump()
            elif (
                kind == "on_chain_end"
                and node == "invoke_metadata_extract_agent"
                and name == "extract_knowledge"
            ):
                knowledges = data.get("output", {})["knowledges"]
                yield ExtractKnowledgeEnd(data=knowledges).model_dump()
            elif (
                kind == "on_chain_start"
                and node == "invoke_metadata_extract_agent"
                and name == "retrieve_knowledge"
            ):
                yield RetrieveKnowledgeStart().model_dump()
            elif (
                kind == "on_chain_end"
                and node == "invoke_metadata_extract_agent"
                and name == "retrieve_knowledge"
            ):
                retrieved_knowledge = data.get("output", {})["retrieved_knowledges"][0]
                yield RetrieveKnowledgeEnd(data=retrieved_knowledge).model_dump()
            elif (
                kind == "on_chain_start"
                and name == "extract_check_point"
            ):
                yield ExtractCheckPointStart().model_dump()
            elif (
                kind == "on_chain_end"
                and name == "extract_check_point"
            ):
                check_points = data.get("output", {})["check_points"]
                yield ExtractCheckPointEnd(data=check_points).model_dump()
            elif (
                kind == "on_chain_start"
                and name == "__start__"
                and node == "invoke_search_agent"
            ):
                input_data = cast(SearchAgentState, data.get("input"))
                yield SearchAgentStart(
                    data=SearchAgentInput(
                        content=input_data.content,
                        purpose=input_data.purpose,
                        expected_sources=input_data.expected_sources,
                    )
                ).model_dump()
            elif (
                kind == "on_chain_start"
                and name == "evaluate_current_status"
                and node == "invoke_search_agent"
            ):
                yield EvaluateCurrentStatusStart().model_dump()
            elif (
                kind == "on_chain_end"
                and name == "evaluate_current_status"
                and node == "invoke_search_agent"
            ):
                status = data.get("output", {})["statuses"][0]
                yield EvaluateCurrentStatusEnd(data=status).model_dump()
            elif (
                kind == "on_chain_start"
                and name == "generate_answer"
                and node == "invoke_search_agent"
            ):
                yield GenerateAnswerStart().model_dump()
            elif (
                kind == "on_chain_end"
                and name == "generate_answer"
                and node == "invoke_search_agent"
            ):
                search_result = data.get("output", {})["result"]
                yield GenerateAnswerEnd(data=search_result).model_dump()
            elif (
                kind == "on_chain_start"
                and name == "evaluate_search_result"
            ):
                yield EvaluateSearchResultStart().model_dump()
            elif (
                kind == "on_parser_end"
                and node == "evaluate_search_result"
            ):
                verification = cast(RetrievalResultVerification, data.get("output"))
                yield EvaluateSearchResultEnd(data=verification).model_dump()
            elif (
                kind == "on_chain_end"
                and name == "should_retry_or_continue"
            ):
                decision = cast(str, data.get("output", {}))
                yield LLMDecision(data=LLMDecisionData(decision=decision)).model_dump()
            elif (
                kind == "on_chain_start"
                and name == "write_fact_check_report"
            ):
                yield WriteFactCheckReportStart().model_dump()
            elif (
                kind == "on_chain_end"
                and name == "write_fact_check_report"
            ):
                report = data.get("output", {})["report"]
                yield WriteFactCheckReportEnd(data=FactCheckReportData(report=report)).model_dump()
            elif (
                kind == "on_tool_start"
            ):
                tool_name = name
                tool_input_str = json.dumps(data.get("input", {}))
                yield ToolStart(
                    data=ToolStartData(
                        tool_name=tool_name,
                        input_str=tool_input_str
                    )
                ).model_dump()
            elif (
                kind == "on_tool_end"
            ):
                tool_name = name
                tool_output_str = None
                if isinstance(data.get("output"), ToolMessage):
                    tool_output_str = str(cast(ToolMessage, data.get("output")).content)
                else:
                    tool_output_str = str(data.get("output"))
                    
                yield ToolEnd(
                    data=ToolEndData(
                        tool_name=tool_name,
                        output_str=tool_output_str
                    )
                ).model_dump()
            
    except Exception as e:
        error_message = f"Error running agent: {str(e)}"
        yield Error(data=ErrorData(message=error_message)).model_dump()
    
