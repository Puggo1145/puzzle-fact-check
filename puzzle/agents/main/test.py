from .graph import MainAgent
from models import ChatQwen
from langchain_openai import ChatOpenAI
from utils.llm_callbacks import ReasonerStreamingCallback


def test_plan_agent():
    example_initial_state = {
        "news_text": """
近日，微博平台有用户发帖称：2025 年 3 月 7 日，俄军使用导弹轰炸乌克兰克里沃罗格一栋五星级酒店，并炸死驻扎于此的欧盟雇佣军教官团。
"""
    }
    
    # model = ChatDeepSeek(model="deepseek-reasoner", temperature=0.6, streaming=True)
    model = ChatQwen(
        model="qwq-plus-latest",
        streaming=True,
        callbacks=[ReasonerStreamingCallback()]
    )
    metadata_extract_model = ChatOpenAI(
        model="gpt-4o", 
        temperature=0
    )
    # metadata_extract_model = ChatQwen(
    #     model="qwen-plus",
    #     temperature=0
    # )
    search_model = ChatQwen(
        model="qwq-plus-latest",
        streaming=True,
        callbacks=[ReasonerStreamingCallback()]
    )

    plan_agent = MainAgent(
        model=model,
        metadata_extract_model=metadata_extract_model,
        search_model=search_model,
    )

    thread_config = {"thread_id": "some_id"}
    plan_agent.invoke(
        example_initial_state,
        {"configurable": thread_config},
    )

if __name__ == "__main__":
    test_plan_agent()
