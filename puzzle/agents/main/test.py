from .graph import MainAgent
from models import ChatQwen


def test_plan_agent():
    example_initial_state = {
        "news_text": """
2021 年 7 月 26 日，东京奥运会男子铁人三项比赛结束后，
金牌得主挪威选手 Kristian Blummenfelt 和一些其他选手跪地
呕吐，中文网络流传说法称："铁人三项选手集体呕吐"因
为"赛场水中大肠杆菌严重超标"、"铁人三项选手在粪水
中游泳"等
"""
    }
    
    # model = ChatDeepSeek(model="deepseek-reasoner", temperature=0.6, streaming=True)
    model = ChatQwen(
        model="qwq-plus-0305",
        streaming=True
    )
    metadata_extract_model = ChatQwen(
        model="qwen-turbo", 
        temperature=0
    )
    search_model = ChatQwen(
        model="qwq-plus-0305",
        streaming=True
    )

    plan_agent = MainAgent(
        # mode="API",
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
