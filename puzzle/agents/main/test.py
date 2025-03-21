from .graph import MainAgent
from models import ChatQwen
from langchain_openai import ChatOpenAI
from utils.llm_callbacks import ReasonerStreamingCallback


def test_plan_agent():
    example_initial_state = {
        "news_text": """2024 年 12 月 16 日，网传“中欧班列将绕过立陶宛，先前铺设的200多条铁轨也将一并拆除，班列改为停靠俄罗斯境内加里宁格勒”"""
    }
    
    # model = ChatDeepSeek(model="deepseek-reasoner", temperature=0.6, streaming=True)
    model = ChatQwen(
        model="qwq-plus-latest",
        streaming=True,
        callbacks=[ReasonerStreamingCallback()]
    )
    metadata_extract_model = ChatOpenAI(
        model="gpt-4o-mini", 
        temperature=0
    )
    # metadata_extract_model = ChatQwen(
    #     model="qwen-turbo",
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
