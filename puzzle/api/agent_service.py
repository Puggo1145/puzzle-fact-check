import json
from typing import cast

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

async def run_main_agent(news_text: str, config: CreateAgentConfig):
    thread_id = str(uuid.uuid4())

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

            if (
                kind == "on_chain_start"
                and node == "invoke_metadata_extract_agent"
                and name == "extract_basic_metadata"
            ):
                sse_event = OnExtractBasicMetadataStart()
                pretier_print_event(sse_event)
            elif (
                kind == "on_chain_end"
                and node == "invoke_metadata_extract_agent"
                and name == "extract_basic_metadata"
            ):
                basic_metadata = data.get("output", {})["basic_metadata"]
                sse_event = OnExtractBasicMetadataEnd(data=basic_metadata)
                pretier_print_event(sse_event)
            elif (
                kind == "on_chain_start"
                and node == "invoke_metadata_extract_agent"
                and name == "extract_knowledge"
            ):
                sse_event = OnExtractKnowledgeStart()
                pretier_print_event(sse_event)
            elif (
                kind == "on_chain_end"
                and node == "invoke_metadata_extract_agent"
                and name == "extract_knowledge"
            ):
                knowledges = data.get("output", {})["knowledges"]
                sse_event = OnExtractKnowledgeEnd(data=knowledges)
                pretier_print_event(sse_event)
            elif (
                kind == "on_chain_start"
                and node == "invoke_metadata_extract_agent"
                and name == "retrieve_knowledge"
            ):
                sse_event = OnRetrieveKnowledgeStart()
                pretier_print_event(sse_event)
            elif (
                kind == "on_chain_end"
                and node == "invoke_metadata_extract_agent"
                and name == "retrieve_knowledge"
            ):
                retrieved_knowledge = data.get("output", {})["retrieved_knowledges"][0]
                sse_event = OnRetrieveKnowledgeEnd(data=retrieved_knowledge)
                pretier_print_event(sse_event)
            elif (
                kind == "on_chain_start"
                and name == "extract_check_point"
            ):
                sse_event = OnExtractCheckPointStart()
                pretier_print_event(sse_event)
            elif (
                kind == "on_chain_end"
                and name == "extract_check_point"
            ):
                check_points = data.get("output", {})["check_points"]
                sse_event = OnExtractCheckPointEnd(data=check_points)
                pretier_print_event(sse_event)
            elif (
                kind == "on_chain_start"
                and name == "__start__"
                and node == "invoke_search_agent"
            ):
                input_data = cast(SearchAgentState, data.get("input"))
                sse_event = OnSearchAgentStart(
                    data=SearchAgentInput(
                        content=input_data.content,
                        purpose=input_data.purpose,
                        expected_sources=input_data.expected_sources,
                    )
                )
                pretier_print_event(sse_event)
            elif (
                kind == "on_chain_start"
                and name == "evaluate_current_status"
                and node == "invoke_search_agent"
            ):
                sse_event = OnEvaluateCurrentStatusStart()
                pretier_print_event(sse_event)
            elif (
                kind == "on_chain_end"
                and name == "evaluate_current_status"
                and node == "invoke_search_agent"
            ):
                status = data.get("output", {})["statuses"][0]
                sse_event = OnEvaluateCurrentStatusEnd(data=status)
                pretier_print_event(sse_event)
            elif (
                kind == "on_chain_start"
                and name == "generate_answer"
                and node == "invoke_search_agent"
            ):
                sse_event = OnGenerateAnswerStart()
                pretier_print_event(sse_event)
            elif (
                kind == "on_chain_end"
                and name == "generate_answer"
                and node == "invoke_search_agent"
            ):
                search_result = data.get("output", {})["result"]
                sse_event = OnGenerateAnswerEnd(data=search_result)
                pretier_print_event(sse_event)
            elif (
                kind == "on_chain_start"
                and name == "evaluate_search_result"
            ):
                sse_event = OnEvaluateSearchResultStart()
                pretier_print_event(sse_event)
            elif (
                kind == "on_parser_end"
                and node == "evaluate_search_result"
            ):
                verification = cast(RetrievalResultVerification, data.get("output"))
                sse_event = OnEvaluateSearchResultEnd(data=verification)
                pretier_print_event(sse_event)
            elif (
                kind == "on_chain_end"
                and name == "should_retry_or_continue"
            ):
                decision = cast(str, data.get("output", {}))
                sse_event = OnLLMDecision(data=LLMDecisionData(decision=decision))
                pretier_print_event(sse_event)
            elif (
                kind == "on_chain_start"
                and name == "write_fact_check_report"
            ):
                sse_event = OnWriteFactCheckReportStart()
                pretier_print_event(sse_event)
            elif (
                kind == "on_chain_end"
                and name == "write_fact_check_report"
            ):
                report = data.get("output", {})["report"]
                sse_event = OnWriteFactCheckReportEnd(data=FactCheckReportData(report=report))
                pretier_print_event(sse_event)
            elif (
                kind == "on_tool_start"
            ):
                tool_name = name
                tool_input_str = json.dumps(data.get("input", {}))
                sse_event = OnToolStart(
                    data=ToolStartData(
                        tool_name=tool_name,
                        input_str=tool_input_str
                    )
                )
                pretier_print_event(sse_event)
            elif (
                kind == "on_tool_end"
            ):
                tool_name = name
                tool_output_str = None
                if isinstance(data.get("output"), ToolMessage):
                    tool_output_str = str(cast(ToolMessage, data.get("output")).content)
                else:
                    tool_output_str = str(data.get("output"))
                    
                sse_event = OnToolEnd(
                    data=ToolEndData(
                        tool_name=tool_name,
                        output_str=tool_output_str
                    )
                )
                pretier_print_event(sse_event)
            # else:
            #     print(f"kind: {kind}")
            #     print(f"data: {data}")
            #     print(f"name: {name}")
            #     print(f"node: {node}")
            #     print("-" * 100)

    except Exception as e:
        raise e
