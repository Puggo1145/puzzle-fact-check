from .graph import PlanAgentGraph
from langchain_deepseek import ChatDeepSeek
from utils.llm_callbacks import ReasonerStreamingCallback


def test_plan_agent():
    model = ChatDeepSeek(
        model="deepseek-reasoner",
        temperature=0.6,
        streaming=True,
        callbacks=[ReasonerStreamingCallback()]
    )
    
    example_initial_state = {
        "news_text": """
2021 年 7 月 26 日，东京奥运会男子铁人三项比赛结束后，
金牌得主挪威选手 Kristian Blummenfelt 和一些其他选手跪地
呕吐，中文网络流传说法称："铁人三项选手集体呕吐"因
为"赛场水中大肠杆菌严重超标"、"铁人三项选手在粪水
中游泳"等
"""
    }
    
    plan_agent = PlanAgentGraph(model=model)
    result = plan_agent.invoke(example_initial_state)
    
    print(result)

if __name__ == "__main__":
    test_plan_agent()
