"""
Test for the agent service and SSE stream
"""
import asyncio
import json

async def test_main_agent(news_text: str, thread_id: str):
    """Simple test agent that generates events for testing SSE"""
    # Initial delay to simulate processing
    await asyncio.sleep(1)
    
    # Yield a series of events to simulate agent processing
    yield {
        "event": "extract_basic_metadata_start",
        "data": None
    }
    await asyncio.sleep(1)
    
    yield {
        "event": "extract_basic_metadata_end",
        "data": {
            "news_type": "技术新闻",
            "who": ["OpenAI", "研究人员"],
            "when": ["最近"],
            "where": ["全球"],
            "what": ["发布了GPT-4模型"],
            "why": ["提高AI能力"],
            "how": ["通过大规模计算训练"]
        }
    }
    await asyncio.sleep(1)
    
    yield {
        "event": "extract_knowledge_start",
        "data": None
    }
    await asyncio.sleep(1)
    
    yield {
        "event": "extract_knowledge_end",
        "data": [
            {
                "term": "GPT-4",
                "category": "AI模型",
                "description": "OpenAI的最新大型语言模型",
                "source": "新闻内容"
            }
        ]
    }
    await asyncio.sleep(1)
    
    yield {
        "event": "extract_check_point_start",
        "data": None
    }
    await asyncio.sleep(1)
    
    yield {
        "event": "extract_check_point_end",
        "data": [
            {
                "id": "cp1",
                "content": "OpenAI发布了GPT-4模型",
                "is_verification_point": True,
                "importance": "高"
            }
        ]
    }
    await asyncio.sleep(1)
    
    yield {
        "event": "search_agent_start",
        "data": {
            "content": "OpenAI发布了GPT-4模型",
            "purpose": "验证OpenAI是否确实发布了GPT-4模型",
            "expected_sources": ["OpenAI官网", "技术新闻网站"]
        }
    }
    await asyncio.sleep(1)
    
    yield {
        "event": "tool_start",
        "data": {
            "tool_name": "search_web",
            "input_str": "{\"query\": \"OpenAI GPT-4发布\"}"
        }
    }
    await asyncio.sleep(1)
    
    yield {
        "event": "tool_end",
        "data": {
            "tool_name": "search_web",
            "output_str": "搜索结果显示OpenAI确实发布了GPT-4模型"
        }
    }
    await asyncio.sleep(1)
    
    yield {
        "event": "generate_answer_end",
        "data": {
            "summary": "搜索结果证实OpenAI确实发布了GPT-4模型",
            "conclusion": "新闻声明是正确的",
            "confidence": "高"
        }
    }
    await asyncio.sleep(1)
    
    yield {
        "event": "write_fact_check_report_start",
        "data": None
    }
    await asyncio.sleep(1)
    
    yield {
        "event": "write_fact_check_report_end",
        "data": {
            "report": "# 事实核查报告\n\n根据我们的核查，OpenAI确实发布了GPT-4模型。这一声明得到了多个可靠来源的证实，包括OpenAI官方网站。\n\n**结论：**新闻准确报道了此事实。"
        }
    }
    

if __name__ == "__main__":
    # Simple test to run the agent
    async def run_test():
        async for event in test_main_agent("OpenAI发布了全新的GPT-4模型", "test-thread-id"):
            print(f"Event: {event['event']}")
            print(f"Data: {json.dumps(event['data'], ensure_ascii=False)}")
            print("-" * 50)
    
    asyncio.run(run_test()) 