import json
from models import ChatQwen
from .graph import MetadataExtractAgentGraph
from db import db_integration

def test_metadata_extractor():
    model = ChatQwen(
        model="qwen-turbo",
        temperature=0,
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
    
    # 初始化 db news text node
    db_integration.initialize_with_news_text(news_text=example_initial_state["news_text"])
    
    metadata_extractor_agent = MetadataExtractAgentGraph(model)
    result = metadata_extractor_agent.invoke(example_initial_state)
    
    # 打印结果
    print(result)

if __name__ == "__main__":
    test_metadata_extractor()
