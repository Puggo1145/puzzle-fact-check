import uuid
import logging
import asyncio
from agents import MainAgent
from langchain_openai import ChatOpenAI
from models import ChatGemini
from agents.event_handlers import AgentEventHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


streamable_nodes = [
    "initialization",
    "invoke_metadata_extract_agent",
    "extract_check_point",
    "human_verification",
    "invoke_search_agent",
    "evaluate_search_result",
    "write_fact_checking_report",
    "evaluate_current_status",
    "generate_answer",
    "extract_basic_metadata",
    "extract_knowledge",
    "retrieve_knowledge",
]

async def run_main_agent(
    news_text: str,
):
    model = ChatGemini(
        model="gemini-2.5-pro-exp-03-25",
        temperature=0,
        streaming=True,
    )
    metadata_extract_model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
    )
    search_model = ChatGemini(
        model="gemini-2.5-pro-exp-03-25",
        temperature=0,
        streaming=True,
    )

    main_agent = MainAgent(
        model=model,
        metadata_extract_model=metadata_extract_model,
        search_model=search_model,
    )

    thread_id = str(uuid.uuid4())
    is_agent_started = False

    thread_config = {"thread_id": thread_id}
    
    event_handler = AgentEventHandler()
    
    try:
        async for event in main_agent.graph.astream_events(
            input=news_text,
            config={"configurable": thread_config},
            version="v2",
        ):
            # Process the event through the event handler
            event_handler.process_event(event)
            
            # For logging purposes
            kind = event.get("event")
            data = event.get("data")
            name = event.get("name")
            metadata = event.get("metadata", {})
            node = (
                None
                if (metadata.get("checkpoint_ns") is None)
                else metadata.get("checkpoint_ns", "None").split(":")[0]
            )
            langgraph_step = metadata.get("langgraph_step")
            run_id = event.get("run_id")

            logger.info(f"kind: {kind}")
            logger.info(f"data: {data}")
            logger.info(f"name: {name}")
            logger.info(f"node: {node}")
            logger.info(f"langgraph_step: {langgraph_step}")
            logger.info(f"run_id: {run_id}")
            logger.info("\n")
            
            # Set agent started flag when we see the first event
            if not is_agent_started:
                is_agent_started = True
                yield {
                    "event": "on_main_agent_start",
                    "data": {
                        "thread_id": thread_id,
                    },
                }
            
    except asyncio.CancelledError:
        logger.info("Cancelled")

    if is_agent_started:
        yield {
            "event": "on_main_agent_end",
            "data": {
                "thread_id": thread_id,
                # TODO: add result data
            },
        }
    yield {
        "event": "on_session_end",
        "data": {
            "thread_id": thread_id,
        },
    }
