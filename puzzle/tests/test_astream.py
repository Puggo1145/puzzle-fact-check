import asyncio
from api.agent_service import run_main_agent
from api.model import CreateAgentConfig, MainAgentConfig, MetadataExtractorConfig, SearcherConfig


async def test_astream():
    await run_main_agent(
        news_text="最近有网络流传说法称，2025 年初，美国共和党议员Riley Moore通过了一项新法案，将禁止中国公民以学生身份来美国。这项法案会导致每年大约30万中国学生将无法获得F、J、M类签证，从而无法到美国学习或参与学术交流。",
        config=CreateAgentConfig(
            main_agent=MainAgentConfig(
                model_name="qwq-plus-latest",
                model_provider="qwen",
                max_retries=1,
            ),
            metadata_extractor=MetadataExtractorConfig(
                model_name="qwen-turbo",
                model_provider="qwen",
                temperature=0,
            ),
            searcher=SearcherConfig(
                model_name="qwen-plus-latest",
                model_provider="qwen",
                temperature=0,
                max_search_tokens=6000,
                selected_tools=[],
            ),
        )
    )

if __name__ == "__main__":
    asyncio.run(test_astream())