import sys
import asyncio
import logging
import datetime
from agents.main.graph import MainAgent
from models import ChatGemini
from langchain_openai import ChatOpenAI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"./logs/agent_logs/main_agent_{datetime.datetime.now().strftime('%Y-%m-%d')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def test_astream():
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
        mode="API",
        max_search_tokens=5000,
    )
    
    example_initial_state = {
        "news_text": "最近有网络流传说法称，2025 年初，美国共和党议员Riley Moore通过了一项新法案，将禁止中国公民以学生身份来美国。这项法案会导致每年大约30万中国学生将无法获得F、J、M类签证，从而无法到美国学习或参与学术交流。"
    }
    
    thread_config = {"thread_id": "test_id"}
    async for event in main_agent.graph.astream_events(
        input=example_initial_state,
        config={"configurable": thread_config},
    ):
        kind = event.get("event")
        data = event.get("data")
        name = event.get("name")
        metadata = event.get("metadata", {})
        node = (
            ""
            if (metadata.get("checkpoint_ns") is None)
            else metadata.get("checkpoint_ns", "None").split(":")[0]
        )
        langgraph_step = (
            ""
            if (metadata.get("langgraph_step") is None)
            else str(metadata["langgraph_step"])
        )
        run_id = "" if (event.get("run_id") is None) else str(event["run_id"])
        
        logger.info(f"kind: {kind}")
        logger.info(f"data: {data}")
        logger.info(f"name: {name}")
        logger.info(f"node: {node}")
        logger.info(f"langgraph_step: {langgraph_step}")
        logger.info(f"run_id: {run_id}")
        logger.info("\n")


if __name__ == "__main__":
    asyncio.run(test_astream())
